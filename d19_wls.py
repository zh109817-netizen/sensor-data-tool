"""D19: 手写 WLS——多传感器位置估计 vs 普通平均（打印 MSE）"""
import numpy as np

x_true = 10.0                 # 真实位置（未知，待估计）
sigmas = [0.5, 1.0, 3.0]      # 3 个传感器噪声标准差：0.5最准 / 3.0最差
N = 2000                      # 重复 2000 次实验
rng = np.random.default_rng(42)

# 权重 = 噪声方差倒数（★ 完成标准核心：权重来自噪声方差）
weights = [1.0 / s**2 for s in sigmas]
print("传感器噪声 σ:", sigmas)
print("权重 1/σ²   :", [round(w, 2) for w in weights])

err_mean, err_wls = [], []
for _ in range(N):
    # 每个时间点：3 个传感器各给 1 个被高斯噪声污染的观测
    obs = [x_true + rng.normal(0, s) for s in sigmas]

    # 普通平均（等权 LS）
    est_mean = np.mean(obs)

    # WLS：加权平均（权重=1/σ²）
    est_wls = np.average(obs, weights=weights)

    err_mean.append((est_mean - x_true) ** 2)
    err_wls.append((est_wls - x_true) ** 2)

mse_mean = np.mean(err_mean)
mse_wls = np.mean(err_wls)
print(f"\n普通平均 MSE = {mse_mean:.5f}")
print(f"WLS     MSE = {mse_wls:.5f}")
print(f"改善倍数    = {mse_mean/mse_wls:.2f} 倍")
