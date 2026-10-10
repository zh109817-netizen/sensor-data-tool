
"""D23: ReAct 循环（function calling）——不依赖框架的智能体核心"""
import json
import os
import time
import requests
import psycopg

# ---- 加载 .env（D22 同款）----
for line in open(os.path.join(os.path.dirname(__file__), ".env")):
    if "=" in line and not line.startswith("#"):
        k, v = line.strip().split("=", 1)
        os.environ.setdefault(k, v)

API_KEY = os.environ["DEEPSEEK_API_KEY"]
BASE_URL = "https://api.deepseek.com"
MODEL = "deepseek-chat"
PG_DSN = "host=localhost port=5433 dbname=sensor_db user=postgres password=postgres"


# ================= 工具实现（系统执行的部分） =================
def query_month_avg(month: str) -> str:
    """查询某月传感器平均读数（month='YYYY-MM'）"""
    with psycopg.connect(PG_DSN) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT avg_value FROM sensor_monthly_stats WHERE month = %s",
                (month,),
            )
            row = cur.fetchone()
    return str(row[0]) if row else "无数据"


def compute_ratio(current: float, previous: float) -> str:
    """计算环比变化率（%）"""
    if float(previous) == 0:
        return "错误：上期值为 0，无法计算"
    return f"{(float(current) - float(previous)) / float(previous) * 100:.2f}%"


# 工具注册表：名字 → (函数, 描述)。模型只看描述选工具，系统按名字执行
TOOL_FUNCS = {
    "query_month_avg": query_month_avg,
    "compute_ratio": compute_ratio,
}

# ================= 工具定义（给模型看：name/description/parameters） =================
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "query_month_avg",
            "description": "查询某月的传感器平均读数。month 参数格式为 YYYY-MM，例如 2026-09",
            "parameters": {
                "type": "object",
                "properties": {
                    "month": {"type": "string", "description": "月份，如 2026-09"}
                },
                "required": ["month"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compute_ratio",
            "description": "计算环比变化率百分比：current 为当期值，previous 为上期值",
            "parameters": {
                "type": "object",
                "properties": {
                    "current": {"type": "number", "description": "当期值"},
                    "previous": {"type": "number", "description": "上期值"},
                },
                "required": ["current", "previous"],
            },
        },
    },
]


def call_llm(messages):
    """发请求，返回 message 对象（可能含 tool_calls）"""
    payload = {
        "model": MODEL,
        "messages": messages,
        "tools": TOOLS,                  # ★ 告诉模型有哪些工具可用
        "tool_choice": "auto",           # 模型自主决定是否/何时调用
        "temperature": 0.2,
        "max_tokens": 1024,
    }
    resp = requests.post(
        f"{BASE_URL}/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json=payload,
        timeout=60,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:200]}")
    return resp.json()["choices"][0]["message"]


def run_agent(task, max_steps=8):
    """ReAct 循环：思考(模型) → 行动(tool_calls) → 观察(工具结果回填) → 再思考"""
    messages = [
        {"role": "system",
         "content": "你是数据分析助手。请使用提供的工具完成用户任务，逐步执行，最后用中文总结结论。"},
        {"role": "user", "content": task},
    ]
    for step in range(max_steps):
        print(f"\n===== 第 {step+1} 轮 =====")
        msg = call_llm(messages)

        if msg.get("tool_calls"):                       # 模型要调用工具
            for tc in msg["tool_calls"]:                # 可能并行多个
                fn_name = tc["function"]["name"]
                args = json.loads(tc["function"]["arguments"])
                print(f"  [思考→行动] 调用 {fn_name}({args})")
                try:
                    result = TOOL_FUNCS[fn_name](**args)   # 系统执行
                except Exception as e:                     # 错误兜底
                    result = f"工具执行错误: {e}"
                print(f"  [观察] 结果 = {result}")
                # 回填：assistant 的 tool_calls 原样 + 每条 tool 结果
                messages.append({
                    "role": "assistant",
                    "content": msg.get("content"),
                    "tool_calls": [tc],
                })
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],           # 必须与 tool_calls 的 id 对应
                    "content": result,
                })
        else:                                           # 模型给出最终回答
            print(f"  [最终回答] {msg['content']}")
            return msg["content"]
    print("达到最大步数，强制结束")


if __name__ == "__main__":
    # 准备数据表（幂等）：8 月 22.5，9 月 25.3
    with psycopg.connect(PG_DSN) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "CREATE TABLE IF NOT EXISTS sensor_monthly_stats ("
                " month TEXT PRIMARY KEY, avg_value DOUBLE PRECISION)"
            )
            cur.execute(
                "INSERT INTO sensor_monthly_stats (month, avg_value) VALUES "
                "('2026-08', 22.5), ('2026-09', 25.3) "
                "ON CONFLICT (month) DO NOTHING"
            )
        conn.commit()
    print("数据表就绪: 2026-08=22.5, 2026-09=25.3")

    run_agent("请查询 2026-08 和 2026-09 两个月的传感器平均读数，"
              "计算 9 月相对 8 月的环比变化率，并总结一句结论。")
