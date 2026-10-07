"""D3 练习升级版：去噪对比（函数化 + 命令行参数 + 日志）。"""
import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from kalman import kalman_1d

logger = logging.getLogger(__name__)


def compare_methods(input_path: Path) -> dict:



    """滑动平均 vs 卡尔曼：返回 RMSE 结果。"""

    if not input_path.exists():
        logger.error("输入文件不存在: %s（先运行 python sensor_demo.py 生成）", input_path)
        sys.exit(1)



    df = pd.read_csv(input_path, encoding="utf-8")
    true_temp = df["true_temp"].to_numpy()
    observed = df["observed"].to_numpy()

    df["sma5"] = df["observed"].rolling(5).mean()
    df["sma11"] = df["observed"].rolling(11).mean()
    df["kalman"] = kalman_1d(observed, Q=0.1, R=1.0)

    def rmse(a, b):
        return float(np.sqrt(np.mean((a - b) ** 2)))

    result = {
        "noise": rmse(observed, true_temp),
        "sma5": rmse(df["sma5"].dropna(), true_temp[4:]),
        "sma11": rmse(df["sma11"].dropna(), true_temp[10:]),
        "kalman": rmse(df["kalman"], true_temp),
    }
    logger.info(
        "RMSE: 噪声=%.3f 窗5=%.3f 窗11=%.3f 卡尔曼=%.3f",
        result["noise"], result["sma5"], result["sma11"], result["kalman"],
    )
    return result


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    if len(sys.argv) != 2:
        logger.error("用法: python smoothing_demo.py <输入csv>")
        sys.exit(1)
    compare_methods(Path(sys.argv[1]))


if __name__ == "__main__":
    main()
