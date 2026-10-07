import time
import datetime

print("温度采集服务已启动", flush=True)
while True:
    now = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] 模拟采集 温度=25.3 度", flush=True)
    time.sleep(5)
