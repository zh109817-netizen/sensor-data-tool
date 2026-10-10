
"""D20: 一维卡尔曼 + 多观测融合（正规 H/R 矩阵化）· 对比源质量对融合收益的影响"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

dt, N, v_true = 1.0, 100, 2.0
rng = np.random.default_rng(7)
x_true = np.cumsum(v_true * dt + rng.normal(0, 0.1, N))

R1, R2 = 4.0, 16.0                    # 传感器1准，传感器2差
z1 = x_true + rng.normal(0, np.sqrt(R1), N)
z2 = x_true + rng.normal(0, np.sqrt(R2), N)

F = np.array([[1.0, dt], [0.0, 1.0]])
H = np.array([[1.0, 0.0]])
Q = np.eye(2) * 0.1
P0 = np.eye(2) * 100.0

def kalman_step(x, P, z, Q, R):
    x_pred = F @ x
    P_pred = F @ P @ F.T + Q
    S = H @ P_pred @ H.T + R
    K = P_pred @ H.T / S
    innov = z - H @ x_pred
    x_new = x_pred + K.flatten() * innov
    P_new = (np.eye(2) - K @ H) @ P_pred
    return x_new, P_new

def run_kalman(obs_seq, R):
    x, P = np.zeros(2), P0.copy()
    est = []
    for z in obs_seq:
        x, P = kalman_step(x, P, z, Q, R)
        est.append(x[0])
    return np.array(est)

def kalman_step_multi(x, P, zvec, Q, Rm, Hm):
    """多观测同时更新：H 2×2, R 对角阵, K 矩阵求逆"""
    x_pred = F @ x
    P_pred = F @ P @ F.T + Q
    S = Hm @ P_pred @ Hm.T + Rm        # (2,2)
    K = P_pred @ Hm.T @ np.linalg.inv(S)   # (2,2)
    innov = zvec - Hm @ x_pred         # (2,)
    x_new = x_pred + K @ innov
    P_new = (np.eye(2) - K @ Hm) @ P_pred
    return x_new, P_new

def run_kalman_multi(obs1, obs2, Rm):
    Hm = np.array([[1.0, 0.0], [1.0, 0.0]])
    x, P = np.zeros(2), P0.copy()
    est = []
    for a, b in zip(obs1, obs2):
        x, P = kalman_step_multi(x, P, np.array([a, b]), Q, Rm, Hm)
        est.append(x[0])
    return np.array(est)

est1 = run_kalman(z1, R1)

est_f16 = run_kalman_multi(z1, z2, np.diag([R1, R2]))      # 质量悬殊
z2b = x_true + rng.normal(0, 2.0, N)
est_f4 = run_kalman_multi(z1, z2b, np.diag([R1, 4.0]))     # 同质量

mse_raw = np.mean((z1 - x_true) ** 2)
mse_kf1 = np.mean((est1 - x_true) ** 2)
mse_f16 = np.mean((est_f16 - x_true) ** 2)
mse_f4 = np.mean((est_f4 - x_true) ** 2)
print(f"原始观测(传感器1) MSE = {mse_raw:.3f}")
print(f"单传感器卡尔曼    MSE = {mse_kf1:.3f}")
print(f"融合(质量悬殊)   MSE = {mse_f16:.3f}   ← 烂传感器几乎不加分")
print(f"融合(同质量)     MSE = {mse_f4:.3f}   ← 等效R减半, 明显加分")
print(f"卡尔曼 vs 原始    = {mse_raw/mse_kf1:.1f} 倍")
print(f"同质量融合 vs 单传感器 = {mse_kf1/mse_f4:.1f} 倍")

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 6))
ax1.plot(x_true, label="true trajectory", linewidth=2)
ax1.plot(z1, ".", alpha=0.5, label="obs (sensor1)")
ax1.plot(est1, label="Kalman (sensor1)", linewidth=2)
ax1.plot(est_f4, "--", label="Kalman (fused equal)", linewidth=2)
ax1.legend(); ax1.set_title("1D Kalman: constant-velocity track")
ax2.plot(est1 - x_true, label="error (sensor1)")
ax2.plot(est_f16 - x_true, label="error (fused R2=16)")
ax2.plot(est_f4 - x_true, label="error (fused equal)")
ax2.legend(); ax2.set_title("estimation error")
plt.tight_layout()
plt.savefig("d20_kalman_result.png", dpi=110)
print("已保存 d20_kalman_result.png")
