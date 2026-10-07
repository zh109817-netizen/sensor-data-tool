"""生成 8 个传感器站点数据文件（模拟多源数据），各 300,000 点"""
from pathlib import Path
import numpy as np

def generate():
    out = Path("sensor_data")
    out.mkdir(exist_ok=True)
    for site in range(8):
        t = np.arange(300_000)
        true = 25.0 + 0.02 * t + 2.0 * np.sin(t / 20.0)   # 真实温度
        observed = true + np.random.normal(0, 1.0, len(t)) # 加噪声
        np.savetxt(out / f"site_{site}.csv",
                   np.column_stack([true, observed]),
                   delimiter=",", header="true_temp,observed", comments="")
    print("生成完成：sensor_data/site_0.csv ~ site_7.csv（各 300,000 点）")

if __name__ == "__main__":
    generate()