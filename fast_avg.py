"""优化版：numpy 向量化滑动平均"""
import numpy as np
import time

def generate(n):
    return np.random.uniform(0, 30, n)

def moving_average_fast(data, window):
    """卷积实现滑动平均：一次算完所有点"""
    kernel = np.ones(window) / window
    return np.convolve(data, kernel, mode="valid")

if __name__ == "__main__":
    data = generate(1_000_000)
    t0 = time.perf_counter()
    result = moving_average_fast(data, 5)
    t1 = time.perf_counter()
    print(f"numpy 版耗时: {t1 - t0:.4f} 秒, 输出 {len(result)} 个点")
