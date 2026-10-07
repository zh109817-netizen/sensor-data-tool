"""一维卡尔曼滤波（常量模型）：从噪声测量还原真实值。"""
import numpy as np


def kalman_1d(zs, Q=0.1, R=1.0):
    """zs: 测量值序列。返回估计值序列。"""
    n = len(zs)
    x = np.zeros(n)      # 估计值
    P = 1.0              # 初始不确定性（先随便给，自动收敛）
    x[0] = zs[0]
    for k in range(1, n):
        # ① 预测
        P = P + Q
        # ② 卡尔曼增益
        K = P / (P + R)
        # ③ 修正
        x[k] = x[k - 1] + K * (zs[k] - x[k - 1])
        # ④ 更新不确定性
        P = (1 - K) * P
    return x
