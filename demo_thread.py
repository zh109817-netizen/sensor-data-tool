"""补课 A①：threading——I/O 等待场景：串行 vs 多线程"""
import threading
import time

def fetch_sensor(i: int) -> None:
    """模拟从传感器接口拉数据的 I/O 等待（真实场景=网络/数据库请求）"""
    time.sleep(0.5)          # 0.5 秒"网络等待"
    # 真实项目这里会是 requests.get(...) / 数据库查询

def run_serial(n: int) -> float:
    """串行：一个一个来，总耗时 = n × 0.5s"""
    t0 = time.perf_counter()
    for i in range(n):
        fetch_sensor(i)
    return time.perf_counter() - t0

def run_threaded(n: int) -> float:
    """多线程：n 个线程同时等，总耗时 ≈ 0.5s"""
    t0 = time.perf_counter()
    threads = [threading.Thread(target=fetch_sensor, args=(i,)) for i in range(n)]
    for t in threads:
        t.start()            # 启动线程（开始"同时等"）
    for t in threads:
        t.join()             # 主线程等待所有线程结束
    return time.perf_counter() - t0

if __name__ == "__main__":
    n = 10
    s = run_serial(n)
    t = run_threaded(n)
    print(f"串行 10 个请求: {s:.2f}s  (预期 ≈5.0s)")
    print(f"线程 10 个请求: {t:.2f}s  (预期 ≈0.5s)")
    print(f"加速比: {s / t:.1f} 倍")
