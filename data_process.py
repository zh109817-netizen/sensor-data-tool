"""D2 练习升级版：数据清洗管道（函数化 + 命令行参数 + 日志）。"""
import logging
import sys
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def clean_and_aggregate(input_path: Path, output_path: Path) -> pd.DataFrame:
    """读→洗→算→出，返回按日统计表。"""
    df = pd.read_csv(input_path, encoding="utf-8")
    logger.info("读入 %d 行", len(df))

    df = df.drop_duplicates()
    df["recharge_amount"] = df["recharge_amount"].fillna(0.0)
    df["online_minutes"] = df["online_minutes"].fillna(0.0)
    logger.info("清洗后 %d 行", len(df))

    daily = df.groupby("date").agg(
        recharge_sum=("recharge_amount", "sum"),
        active_players=("player_id", "nunique"),
        total_minutes=("online_minutes", "sum"),
    ).reset_index()

    daily.to_csv(output_path, index=False, encoding="utf-8")
    logger.info("已导出 %s", output_path)
    return daily


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    if len(sys.argv) != 3:
        logger.error("用法: python data_process.py <输入csv> <输出csv>")
        sys.exit(1)
    clean_and_aggregate(Path(sys.argv[1]), Path(sys.argv[2]))


if __name__ == "__main__":
    main()
