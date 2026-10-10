"""D20: 调参场景依赖验证——杂乱轨迹 vs 规律轨迹"""
import numpy as np

dt, N, v_true = 1.0, 100, 2.0
rng = np.random.default_rng(7)

F = np.array([[1.0, dt], [0.0, 1.0]])
H = np.array([[1.0, 0.0]])
P0 = np.eye(2) * 100.0

def run(obs_seq, R, Q):
    x, P = np.zeros(2), P0.copy()
    est = []
    for z in obs_seq:
        x_pred = F @ x
        P_pred = F @ P @ F.T + Q
        S = H @ P_pred @ H.T + R
        K = P_pred @ H.T / S
        x = x_pred + K.flatten() * (z - H @ x_pred)
        P = (np.eye(2) - K @ H) @ P_pred
        est.append(x[0])
    return np.array(est)

# 场景A：规律轨迹（过程噪声小 σ=0.1）
xA = np.cumsum(v_true * dt + rng.normal(0, 0.1, N))
zA = xA + rng.normal(0, 2.0, N)
print("=== 场景A：规律轨迹（过程噪声 σ=0.1）===")
for q in [0.001, 0.1]:
    print(f"Q={q:<7} MSE={np.mean((run(zA, 4.0, np.eye(2)*q) - xA)**2):.3f}")

# 场景B：杂乱轨迹（过程噪声大 σ=1.0）
xB = np.cumsum(v_true * dt + rng.normal(0, 1.0, N))
zB = xB + rng.normal(0, 2.0, N)
print("\n=== 场景B：杂乱轨迹（过程噪声 σ=1.0）===")
for q in [0.001, 0.1, 1.0]:
    print(f"Q={q:<7} MSE={np.mean((run(zB, 4.0, np.eye(2)*q) - xB)**2):.3f}")
