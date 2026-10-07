"""D4 整合实战：一条命令跑通「生成→清洗→去噪对比」全管道。

用法:
    python pipeline.py
"""
import logging
import sys
from pathlib import Path

from data_process import clean_and_aggregate
from gen_data import generate_data
from smoothing_demo import compare_methods

logger = logging.getLogger(__name__)

GAME_CSV = Path("game_data.csv")
DAILY_CSV = Path("daily_report.csv")
SENSOR_CSV = Path("sensor_data.csv")


def run_pipeline() -> None:
    generate_data(GAME_CSV)          # ① 生成运营数据
    clean_and_aggregate(GAME_CSV, DAILY_CSV)   # ② 清洗统计
    compare_methods(SENSOR_CSV)      # ③ 去噪对比
    logger.info("全管道完成")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    try:
        run_pipeline()
    except Exception:
        logger.exception("管道执行失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
