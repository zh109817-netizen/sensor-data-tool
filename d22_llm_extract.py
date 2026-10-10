
"""D22: LLM API 结构化抽取（DeepSeek, OpenAI 兼容 chat/completions）"""
import json
import os
import time
import requests

# ---- 从 .env 加载 Key（不写死在代码里）----
for line in open(os.path.join(os.path.dirname(__file__), ".env")):
    if "=" in line and not line.startswith("#"):
        k, v = line.strip().split("=", 1)
        os.environ.setdefault(k, v)

API_KEY = os.environ["DEEPSEEK_API_KEY"]
BASE_URL = "https://api.deepseek.com"
MODEL = "deepseek-chat"


def chat(messages, temperature=0.3, max_tokens=512, retries=3):
    """调用 chat/completions，JSON 模式，指数退避重试"""
    url = f"{BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": temperature,          # 越低越确定（抽取任务用 0.3）
        "max_tokens": max_tokens,
        "response_format": {"type": "json_object"},   # ★ JSON 模式
    }
    for attempt in range(retries):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
            if resp.status_code in (401, 403):      # Key 无效：重试无意义
                raise SystemExit(f"[致命] API Key 无效 ({resp.status_code}): {resp.text[:150]}")
            if resp.status_code == 429:             # 限流
                print(f"  [限流] 第 {attempt+1}/{retries} 次重试，等待 {2**attempt}s")
            else:                                   # 5xx 服务端错误
                print(f"  [HTTP {resp.status_code}] 第 {attempt+1}/{retries} 次重试: {resp.text[:100]}")
        except requests.exceptions.Timeout:
            print(f"  [超时] 第 {attempt+1}/{retries} 次重试，等待 {2**attempt}s")
        time.sleep(2 ** attempt)                    # 指数退避 1s/2s/4s
    raise RuntimeError("API 调用失败（已重试 3 次）")


# ---- 练习：运营文本结构化抽取 ----
text = (
    "XX 商城 618 大促：A 牌空气炸锅原价 399 元，现价 299 元，限量 500 台，"
    "7 月 1 日 0 点开抢，全场满 200 减 30，前 100 名下单送保温杯，"
    "售后支持 7 天无理由退货。"
)

messages = [
    {"role": "system",
     "content": "你是结构化抽取器。只输出 JSON，不要解释。字段不存在时给 null。"},
    {"role": "user",
     "content": (
         "从以下运营文本提取字段：商品名称、原价、现价、折扣力度、限购数量、"
         "活动时间、优惠规则、赠品、售后政策。\n\n" + text
     )},
]

print(f"调用 {MODEL} ...")
out = chat(messages)
data = json.loads(out)                 # JSON 模式保证可解析
print("\n抽取结果:")
print(json.dumps(data, ensure_ascii=False, indent=2))
