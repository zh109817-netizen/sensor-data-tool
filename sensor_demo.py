
"""生成模拟海洋表层水温数据：真实值 + 高斯噪声。"""
import numpy as np
import pandas as pd

np.random.seed(42)
n = 120
t = np.arange(n)

# 真实温度：缓慢上升趋势 + 日变化正弦波动（模拟海洋水温）
true_temp = 25.0 + 0.02 * t + 2.0 * np.sin(t / 20.0)

# 传感器读数 = 真实值 + 高斯噪声（均值 0，标准差 0.8）
noise = np.random.normal(0, 0.8, n)
observed = true_temp + noise

df = pd.DataFrame({"time": t, "true_temp": true_temp, "observed": observed})
df.to_csv("sensor_data.csv", index=False, encoding="utf-8")
print("生成完成：sensor_data.csv（120 条：真实值 + 噪声读数）")
