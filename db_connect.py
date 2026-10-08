"""D8：Python 连接 PostgreSQL（SQLAlchemy 版）——把 sensor_readings 读成 DataFrame"""
import pandas as pd
from sqlalchemy import create_engine, text

# 连接串：URL 风格  postgresql+psycopg://用户:密码@主机:端口/库名
ENGINE = create_engine("postgresql+psycopg://postgres:postgres@localhost:5432/sensor_db")

def main() -> None:
    # ① 原生 SQL（SQLAlchemy 2.0 要求 SQL 文本用 text() 包裹）
    with ENGINE.connect() as conn:
        rows = conn.execute(text("SELECT device_id, ts, value FROM sensor_readings")).fetchall()
    print("查询结果（元组）:")
    for r in rows:
        print(r)

    # ② pandas 直读 engine（官方推荐方式，无警告）
    df = pd.read_sql("SELECT device_id, ts, value FROM sensor_readings", ENGINE)
    print("\nDataFrame 形式:")
    print(df)

    print("\n按设备分组:")
    print(df.groupby("device_id")["value"].agg(["count", "mean"]))

if __name__ == "__main__":
    main()

