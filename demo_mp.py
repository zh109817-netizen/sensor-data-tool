"""补课 A③：multiprocessing——CPU 密集：批量去噪 串行 vs 多进程"""
import time
from multiprocessing import Pool
from pathlib import Path
import numpy as np

DATA_DIR = Path(__file__).parent / "sensor_data"

def moving_average_slow(data, window=5):
    """纯 Python 循环滑动平均（故意用循环版制造明显 CPU 负担；
    真实项目里这里可能是卡尔曼滤波/特征计算/模型推理等重计算）"""
    out = []
    for i in range(window - 1, len(data)):
        out.append(sum(data[i - window + 1: i + 1]) / window)
    return out

def process_file(path):
    """处理一个站点文件：读 → 循环滑动平均 → 返回统计"""
    arr = np.genfromtxt(path, delimiter=",", skip_header=1)
    observed = arr[:, 1].tolist()          # 转 list（循环版需要）
    sma = moving_average_slow(observed)
    return path.name, len(sma), round(sma[-1], 4)

def run_serial(files):
    t0 = time.perf_counter()
    results = [process_file(f) for f in files]
    return time.perf_counter() - t0, results

def run_parallel(files, workers=4):
    t0 = time.perf_counter()
    with Pool(workers) as pool:            # 进程池：4 个 worker 进程
        results = pool.map(process_file, files)   # 自动分发，并行执行
    return time.perf_counter() - t0, results

if __name__ == "__main__":
    files = sorted(DATA_DIR.glob("site_*.csv"))
    s, rs = run_serial(files)
    p, rp = run_parallel(files)
    print(f"串行 {len(files)} 个文件: {s:.3f}s")
    print(f"并行 {len(files)} 个文件: {p:.3f}s")
    print(f"加速比: {s / p:.1f} 倍（4 核理论上限 4 倍）")
    print(f"串并行结果一致: {rs == rp}")
