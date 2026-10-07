"""生成模拟游戏运营数据：含重复行 + 缺失值。D4 改造：函数化。"""
import random
from pathlib import Path


def generate_data(output: Path) -> None:
    random.seed(42)
    dates = ["2026-09-28", "2026-09-29", "2026-09-30", "2026-10-01"]
    rows = []
    for _ in range(80):
        rows.append([
            random.choice(dates),
            f"p{random.randint(1, 30):02d}",
            f"S{random.randint(1, 3)}",
            round(random.uniform(0, 300), 2),
            random.randint(0, 240),
        ])
    rows.append(rows[3])
    rows.append(rows[10])
    for i in (5, 17, 33):
        rows[i][3] = ""
    for i in (9, 20):
        rows[i][4] = ""

    with open(output, "w", encoding="utf-8") as f:
        f.write("date,player_id,server,recharge_amount,online_minutes\n")
        for r in rows:
            f.write(",".join(map(str, r)) + "\n")
    print(f"生成完成：{output}")
