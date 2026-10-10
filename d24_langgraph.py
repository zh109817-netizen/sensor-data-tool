
"""D24: LangGraph 实现 ReAct Agent——状态/可中断/人工确认（对比 D23 手写循环）"""
import json
import os
import requests
import psycopg
from typing import Annotated, Literal, TypedDict
from operator import add
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

# ---- .env / API / PG（同 D23）----
for line in open(os.path.join(os.path.dirname(__file__), ".env")):
    if "=" in line and not line.startswith("#"):
        k, v = line.strip().split("=", 1)
        os.environ.setdefault(k, v)
API_KEY = os.environ["DEEPSEEK_API_KEY"]
BASE_URL = "https://api.deepseek.com"
MODEL = "deepseek-chat"
PG_DSN = "host=localhost port=5433 dbname=sensor_db user=postgres password=postgres"

def query_month_avg(month: str) -> str:
    with psycopg.connect(PG_DSN) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT avg_value FROM sensor_monthly_stats WHERE month=%s", (month,))
            row = cur.fetchone()
    return str(row[0]) if row else "无数据"

def compute_ratio(current: float, previous: float) -> str:
    if float(previous) == 0:
        return "错误：上期值为 0"
    return f"{(float(current)-float(previous))/float(previous)*100:.2f}%"

TOOL_FUNCS = {"query_month_avg": query_month_avg, "compute_ratio": compute_ratio}
TOOLS = [
    {"type": "function", "function": {"name": "query_month_avg",
     "description": "查询某月的传感器平均读数。month 参数格式为 YYYY-MM，例如 2026-09",
     "parameters": {"type": "object", "properties": {"month": {"type": "string"}},
                    "required": ["month"]}}},
    {"type": "function", "function": {"name": "compute_ratio",
     "description": "计算环比变化率百分比：current 当期值, previous 上期值",
     "parameters": {"type": "object", "properties": {"current": {"type": "number"},
                    "previous": {"type": "number"}}, "required": ["current", "previous"]}}},
]

def call_llm(messages):
    payload = {"model": MODEL, "messages": messages, "tools": TOOLS,
               "tool_choice": "auto", "temperature": 0.2, "max_tokens": 1024}
    resp = requests.post(f"{BASE_URL}/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json=payload, timeout=60)
    if resp.status_code != 200:
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:200]}")
    return resp.json()["choices"][0]["message"]

# ================= LangGraph：状态定义 =================
class AgentState(TypedDict):
    messages: Annotated[list, add]   # ★ 框架的 reducer：自动累积消息

# ================= 节点（复用 D23 的代码） =================
def agent_node(state):
    """节点1：模型决策（会输出 tool_calls 或最终回答）"""
    msg = call_llm(state["messages"])
    return {"messages": [msg]}

def tools_node(state):
    """节点2：系统执行工具"""
    last = state["messages"][-1]              # 最新 assistant 消息
    out = []
    for tc in last.get("tool_calls", []):
        fn = tc["function"]["name"]
        args = json.loads(tc["function"]["arguments"])
        print(f"  [工具执行] {fn}({args})")
        try:
            r = TOOL_FUNCS[fn](**args)
        except Exception as e:
            r = f"工具执行错误: {e}"
        print(f"  [观察] {r}")
        out.append({"role": "tool", "tool_call_id": tc["id"], "content": r})
    return {"messages": out}

def human_review(state):
    """节点3：人工确认——interrupt 中断，等用户恢复"""
    answer = interrupt({"question": "请人工确认最终结果（输入 确认 或 重算）"})
    print(f"  [人工确认] 用户回复: {answer}")
    return {"messages": [{"role": "assistant", "content": f"[已人工确认] {answer}"}]}

# ================= 边：条件路由 =================
def router(state) -> Literal["tools", "human_review", "__end__"]:
    last = state["messages"][-1]
    if last.get("tool_calls"):        # 要调工具 → 去执行
        return "tools"
    return "human_review"             # 最终回答 → 先人工确认

# ================= 组装图 =================
graph = StateGraph(AgentState)
graph.add_node("agent", agent_node)
graph.add_node("tools", tools_node)
graph.add_node("human_review", human_review)
graph.add_edge(START, "agent")
graph.add_conditional_edges("agent", router,
    {"tools": "tools", "human_review": "human_review", END: END})
graph.add_edge("tools", "agent")              # 执行完回 agent 再思考
graph.add_edge("human_review", END)
app = graph.compile(checkpointer=MemorySaver())   # ★ checkpointer：可中断/恢复

if __name__ == "__main__":
    with psycopg.connect(PG_DSN) as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE TABLE IF NOT EXISTS sensor_monthly_stats ("
                        " month TEXT PRIMARY KEY, avg_value DOUBLE PRECISION)")
            cur.execute("INSERT INTO sensor_monthly_stats (month, avg_value) VALUES "
                        "('2026-08', 22.5), ('2026-09', 25.3) ON CONFLICT (month) DO NOTHING")
        conn.commit()

    task = ("请查询 2026-08 和 2026-09 两个月的传感器平均读数，"
            "计算 9 月相对 8 月的环比变化率，并总结一句结论。")
    config = {"configurable": {"thread_id": "d24-demo"}}   # ★ 会话标识（状态隔离）

    print("== 第一次运行：会中断在人工确认 ==")
    app.invoke({"messages": [{"role": "user", "content": task}]}, config)

    st = app.get_state(config)
    print(f"\n== 中断点：next 节点 = {st.next}（checkpointer 保存了全部中间状态）==")
    print("  此时进程可退出，下次用同一 thread_id 恢复")

    print("\n== 恢复：人工确认通过 ==")
    result = app.invoke(Command(resume="确认无误"), config)

    print("\n== 最终结果 ==")
    for m in result["messages"]:
        if m.get("role") == "assistant" and not m.get("tool_calls"):
            print(m["content"])
