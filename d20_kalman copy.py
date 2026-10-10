
"""D20: 一维卡尔曼滤波——匀速运动轨迹估计 + 两传感器融合"""
import numpy as np
import matplotlib
matplotlib.use("Agg")                    # 无显示环境画图
import matplotlib.pyplot as plt

# ---- 1. 真实轨迹：匀速运动（速度 2 m/s，小幅过程扰动）----
dt, N, v_true = 1.0, 100, 2.0
rng = np.random.default_rng(7)
x_true = np.cumsum(v_true * dt + rng.normal(0, 0.1, N))   # 位置逐秒累加

# ---- 2. 两个传感器观测（噪声不同：传感器1准，传感器2差）----
R1, R2 = 4.0, 16.0
z1 = x_true + rng.normal(0, np.sqrt(R1), N)
z2 = x_true + rng.normal(0, np.sqrt(R2), N)

# ---- 3. 卡尔曼参数 ----
F = np.array([[1.0, dt], [0.0, 1.0]])   # 状态转移：位置+=速度·dt, 速度不变
H = np.array([[1.0, 0.0]])              # 观测矩阵：只观测位置
Q = np.eye(2) * 0.1                     # 过程噪声（★ 调参点）
P0 = np.eye(2) * 100.0                  # 初始协方差（起点不确定度大）

def kalman_step(x, P, z, Q, R):
    """预测-更新一步（一维观测）"""
    # 预测
    x_pred = F @ x
    P_pred = F @ P @ F.T + Q
    # 更新
    S = H @ P_pred @ H.T + R             # 观测残差协方差（标量）
    K = P_pred @ H.T / S                  # 卡尔曼增益（(2,1) 列向量）
    innov = z - H @ x_pred                # 观测残差（标量）
    x_new = x_pred + K.flatten() * innov  # 融合：(2,) + (2,)·标量
    P_new = (np.eye(2) - K @ H) @ P_pred  # (2,1)@(1,2)=(2,2) ✓
    return x_new, P_new

def run_kalman(obs_seq, R):
    x, P = np.zeros(2), P0.copy()
    est = []
    for z in obs_seq:
        x, P = kalman_step(x, P, z, Q, R)
        est.append(x[0])                 # 只记录位置估计
    return np.array(est)

# ---- 4. 单传感器卡尔曼（用传感器1）----
est1 = run_kalman(z1, R1)

# ---- 5. 两传感器融合：观测先按 1/σ² 加权平均（D19 思路），等效 R 更小 ----
w1, w2 = 1.0/R1, 1.0/R2
z_fuse = (w1 * z1 + w2 * z2) / (w1 + w2)
R_fuse = 1.0 / (w1 + w2)                 # 融合后等效噪声方差（变小）
est2 = run_kalman(z_fuse, R_fuse)

# ---- 6. 精度对比（MSE）----
mse_raw = np.mean((z1 - x_true) ** 2)
mse_kf1 = np.mean((est1 - x_true) ** 2)
mse_kf2 = np.mean((est2 - x_true) ** 2)
print(f"原始观测(传感器1) MSE = {mse_raw:.3f}")
print(f"单传感器卡尔曼  MSE = {mse_kf1:.3f}")
print(f"融合卡尔曼      MSE = {mse_kf2:.3f}")
print(f"卡尔曼 vs 原始改善 = {mse_raw/mse_kf1:.1f} 倍 | 融合 vs 单传感 = {mse_kf1/mse_kf2:.1f} 倍")

# ---- 7. 画图：轨迹对比 + 误差曲线 ----
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 6))
ax1.plot(x_true, label="真实轨迹", linewidth=2)
ax1.plot(z1, ".", alpha=0.5, label="传感器1观测")
ax1.plot(est1, label="单传感器卡尔曼", linewidth=2)
ax1.plot(est2, "--", label="融合卡尔曼", linewidth=2)
ax1.legend(); ax1.set_title("一维卡尔曼：匀速轨迹估计")
ax2.plot(est1 - x_true, label="单传感误差")
ax2.plot(est2 - x_true, label="融合误差")
ax2.legend(); ax2.set_title("估计误差曲线")
plt.tight_layout()
plt.savefig("d20_kalman_result.png", dpi=110)
print("已保存 d20_kalman_result.png")
