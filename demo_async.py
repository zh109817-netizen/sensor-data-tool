"""补课 A②：asyncio——同一个 I/O 场景，单线程协程并发"""
import asyncio
import time

async def fetch_sensor(i: int) -> None:
    """协程版模拟 I/O：await 等待时让出控制权"""
    await asyncio.sleep(0.5)   # 异步 sleep：等待时不阻塞事件循环

async def run_serial(n: int) -> float:
    """串行（协程里逐个 await）"""
    t0 = time.perf_counter()
    for i in range(n):
        await fetch_sensor(i)
    return time.perf_counter() - t0

async def run_concurrent(n: int) -> float:
    """并发：n 个协程同时等待"""
    t0 = time.perf_counter()
    tasks = [fetch_sensor(i) for i in range(n)]   # 创建协程对象（还没执行）
    await asyncio.gather(*tasks)                  # 交给事件循环并发调度
    return time.perf_counter() - t0

if __name__ == "__main__":
    n = 10
    s = asyncio.run(run_serial(n))
    c = asyncio.run(run_concurrent(n))
    print(f"串行: {s:.2f}s (预期 ≈5.0s)")
    print(f"asyncio: {c:.2f}s (预期 ≈0.5s)")
    print(f"加速比: {s / c:.1f} 倍")
