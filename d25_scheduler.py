"""D25: APScheduler 定时任务——每小时跑 D17 流水线"""
import subprocess
import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger


def run_pipeline():
    """一次流水线：生产 → 消费入库（D17 的两条命令）"""
    print(f"\n[{time.strftime('%H:%M:%S')}] == 定时任务触发: 跑流水线 ==")
    subprocess.run(["python", "pipeline_producer.py"])
    subprocess.run(["python", "pipeline_consumer.py"])
    print(f"[{time.strftime('%H:%M:%S')}] == 流水线完成 ==")


if __name__ == "__main__":
    scheduler = BackgroundScheduler()                    # 后台线程调度器
    scheduler.add_job(
        run_pipeline,
        CronTrigger(minute=0),                           # ★ cron: 每小时整点
        id="hourly_pipeline",
        misfire_grace_time=300,                          # 错过 <5 分钟仍补跑
        coalesce=True,                                   # 积压多次只跑一次
    )
    scheduler.start()

    job = scheduler.get_job("hourly_pipeline")
    print(f"调度器已启动: 每小时整点跑流水线")
    print(f"  下次触发: {job.next_run_time}")
    print("  错过补偿: misfire_grace_time=300s | 积压合并: coalesce=True")

    print("\n== 立即手动触发一次（验证任务本身可用）==")
    run_pipeline()

    print("\n演示结束。正式部署请让脚本常驻:")
    print("  nohup python d25_scheduler.py > scheduler.log 2>&1 &")
    scheduler.shutdown()
