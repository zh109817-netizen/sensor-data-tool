# D24 · 智能体框架与 MCP（2026-10-10）

## 一、LangGraph 核心概念（v1.2.14）
- StateGraph: 节点+边+状态 的声明式编排图
- 状态: TypedDict 定义; reducer 决定增量合并（add=追加, 默认=覆盖）
- 节点: 函数(state)->增量; 边: 显式路由; 条件边: router(state)->节点名
- checkpointer: 状态快照（MemorySaver/PG）; thread_id=会话隔离
- interrupt(): 节点内中断冻结; Command(resume=)恢复
- 运行: invoke(input, config); get_state 看 next 节点

## 二、实测（同 D23 任务）
agent→tools→agent 自动循环 → 中断(human_review) → get_state 确认 → resume 恢复 → 最终回答
★ 进程可退出, 同一 thread_id 恢复（D23 手写做不到）

## 三、手写循环 vs 框架编排
| 维度 | 手写(D23) | LangGraph(D24) |
| 控制流 | while+if/else | 声明式图 |
| 状态 | 手动列表 | reducer 自动 |
| 重试 | 自己写 | 框架内建 |
| 可中断 | 做不到 | checkpointer+interrupt |
| 人工确认 | 自己实现 | interrupt() 一行 |
| 代价 | 全自控 | 类型/API 约定适配 |

## 四、坑
add_messages reducer 会把 dict 改造成 LangChain Message 对象
→ 自写 API 调用序列化失败 → 换自定义 reducer add 保持纯 dict

## 五、MCP（模型上下文协议）
- 开放标准, "AI 应用的 USB-C"; 解决 N×M 集成爆炸
- 三角色: Host(宿主) / Client(连接器,1对1) / Server(工具服务器)
- JSON-RPC: 工具列表/调用/结果统一格式
- vs function calling: 单模型定制 vs 全生态标准
