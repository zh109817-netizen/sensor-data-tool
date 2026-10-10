
"""D20: Q/R 调参实验——观察误差如何变化"""
import numpy as np

dt, N, v_true = 1.0, 100, 2.0
rng = np.random.default_rng(7)
x_true = np.cumsum(v_true * dt + rng.normal(0, 0.1, N))
R1 = 4.0
z1 = x_true + rng.normal(0, np.sqrt(R1), N)

F = np.array([[1.0, dt], [0.0, 1.0]])
H = np.array([[1.0, 0.0]])
P0 = np.eye(2) * 100.0

def kalman_step(x, P, z, Q, R):
    x_pred = F @ x
    P_pred = F @ P @ F.T + Q
    S = H @ P_pred @ H.T + R
    K = P_pred @ H.T / S
    x_new = x_pred + K.flatten() * (z - H @ x_pred)
    P_new = (np.eye(2) - K @ H) @ P_pred
    return x_new, P_new

def run(obs_seq, R, Q):
    x, P = np.zeros(2), P0.copy()
    est = []
    for z in obs_seq:
        x, P = kalman_step(x, P, z, Q, R)
        est.append(x[0])
    return np.array(est)

print("=== 固定 R=4, 调 Q ===")
for q in [0.001, 0.1, 10.0]:
    mse = np.mean((run(z1, R1, np.eye(2)*q) - x_true)**2)
    print(f"Q={q:<7} MSE={mse:.3f}")

print("\n=== 固定 Q=0.1, 调 R ===")
for r in [0.5, 4.0, 50.0]:
    mse = np.mean((run(z1, r, np.eye(2)*0.1) - x_true)**2)
    print(f"R={r:<7} MSE={mse:.3f}")
