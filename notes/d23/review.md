# D23 · 工具调用与 ReAct（2026-10-10）

## 一、function calling 原理
模型不执行函数，只输出"工具名 + JSON 参数"（tool_calls）
系统执行 → 结果回填（tool 消息）→ 模型继续
★ 执行权在系统，决策权在模型

## 二、ReAct 循环（智能体核心）
思考(模型输出 tool_calls) → 行动(系统执行) → 观察(结果回填) → 再思考
直到模型不再要工具 → 输出最终回答

## 三、协议细节（必须精确）
1. assistant 消息必须原样回填（content + tool_calls），漏了模型失忆
2. tool 消息的 tool_call_id 必须等于 assistant 里 tc["id"]（配对）
3. 工具参数是 JSON 字符串 → json.loads 解析
4. 一次回复可含多个 tool_calls（并行执行逐个回填）

## 四、工具定义三要素（模型只看到声明）
- name: 唯一标识
- description: 说明书（写不好→该用不用/参数传错/乱用）
- parameters: JSON Schema（type/properties/required）

## 五、tool_choice 三态
auto=自主决定 / none=禁止调用 / 指定函数=强制调用

## 六、实测（DeepSeek deepseek-chat）
任务: 查 8/9 月均值 → 算环比 → 总结
第1轮 并行查两月(22.5/25.3) → 第2轮 compute_ratio→12.44% → 第3轮 结构化总结
★ 模型自主串联 查库→算数→总结 三步

## 七、问题要点
- 描述工具: 说明"何时用/参数格式/输出含义"，示例给具体值（如 YYYY-MM）
- 错误兜底: 工具返回错误字符串而不是崩溃；循环 try/except
- 最大步数限制防死循环（max_steps=8）
