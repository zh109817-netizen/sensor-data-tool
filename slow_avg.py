"""性能分析靶子：纯 Python 循环版滑动平均（故意写慢）"""
import random
import time

def generate(n):
    """生成 n 个随机温度点"""
    return [random.random() * 30 for _ in range(n)]

def moving_average_slow(data, window):
    """滑动平均：每个点都重新加一遍前 window 个数（慢）"""
    out = []
    for i in range(window - 1, len(data)):
        out.append(sum(data[i - window + 1 : i + 1]) / window)
    return out

if __name__ == "__main__":
    data = generate(1_000_000)
    t0 = time.perf_counter()
    result = moving_average_slow(data, 5)
    t1 = time.perf_counter()
    print(f"纯循环版耗时: {t1 - t0:.3f} 秒, 输出 {len(result)} 个点")
