# D22 · LLM API 与提示工程（2026-10-10）

## 一、OpenAI 兼容 chat/completions 调用
POST {base_url}/chat/completions
headers: Authorization: Bearer <KEY>
payload: model / messages / temperature / max_tokens / response_format
DeepSeek: base_url=https://api.deepseek.com, model=deepseek-chat

## 二、消息结构（三段式）
- system: 角色+任务+输出约束（"只输出 JSON，字段缺失给 null"）
- user: 任务指令 + 输入文本
- assistant: 模型回复（多轮时回填历史）

## 三、关键参数
- temperature: 低(0.3)=确定, 高=发散；抽取任务用低
- max_tokens: 输出上限（512 够用）
- response_format={"type":"json_object"}: JSON 模式 → 输出可 json.loads
- tools: 函数声明格式（D23 深入）

## 四、报错与重试（工程策略）
- 401/403（Key 无效）: 致命，不重试，直接退出
- 429（限流）: 指数退避重试（1s/2s/4s）
- 5xx（服务端）: 指数退避重试
- 超时: 指数退避重试
- 重试上限 3 次，避免无限循环

## 五、token 估算（面试）
- 中文≈1 字 1 token, 英文≈4 字符 1 token
- 请求消耗 = 全部消息文本累计
- 超出上下文 → 400 context_length_exceeded → 截断/摘要历史

## 六、实测（结构化抽取）
输入: 618 大促运营文本
输出: 9 字段全抽取（商品/原价/现价/限购/活动时间/优惠规则/赠品/售后）
★ 折扣力度=null —— 文本未提及, 模型不编造（system 约束生效）
坏 Key 验证: 401 立即致命退出, 不重试

## 七、提示词设计要点（面试）
角色+任务+约束三段式 / JSON 模式保可解析 / 缺失给 null 不编造 /
低 temperature 提确定性 / 字段清单明示

## 坑
venv 缺 requests → pip install requests（或用 urllib 标准库零依赖）
