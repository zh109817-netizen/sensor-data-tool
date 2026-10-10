
"""D18: 时序处理进阶——用 D17 入库真实数据走「插值-重采样-特征-存储」"""
import os
import random
import warnings
import pandas as pd
import psycopg
warnings.filterwarnings("ignore")   # 忽略 read_sql 的 DBAPI 警告（无碍）

# 1️⃣ 读 D17 入库的真实数据（959 行）
conn = psycopg.connect("host=localhost port=5433 dbname=sensor_db user=postgres password=postgres")
df = pd.read_sql("SELECT device_id, ts, value FROM sensor_events_part ORDER BY device_id, ts", conn)
conn.close()
print("① 全表:", len(df), "行,", df.device_id.nunique(), "台设备")

# 2️⃣ 选 sensor-00（含 D16+D17 数据，跨度 61 分钟——正好演示真实数据的杂乱）
s = df[df.device_id == "sensor-00"][["ts", "value"]].copy()
s["ts"] = pd.to_datetime(s["ts"])
s = s.set_index("ts").sort_index()
print("② sensor-00:", len(s), "条,", s.index.min(), "~", s.index.max())

# 3️⃣ 造缺失的正确姿势：置 NaN（保留行），不是删行
random.seed(42)
drop_idx = random.sample(list(s.index), 10)
s.loc[drop_idx, "value"] = float("nan")     # ★ 值变 NaN，行还在 → 插值有位置可填
print("③ 置 NaN 后: 共", len(s), "行, 缺失", int(s["value"].isna().sum()), "个点")

# 4️⃣ 插值对比：forward（拿上一个） vs linear（两点线性）
s_fill_f = s["value"].ffill()
s_fill_l = s["value"].interpolate(method="linear")
print("④ 插值前缺失:", int(s["value"].isna().sum()),
      "| ffill 后:", int(s_fill_f.isna().sum()),
      "| linear 后:", int(s_fill_l.isna().sum()))

# 5️⃣ 10 秒重采样（匹配秒级粒度，聚合 mean）
r10 = s_fill_l.resample("10s").mean().rename("value")
print("⑤ 10s 重采样:", int(r10.notna().sum()), "/", len(r10), "个桶")

# 6️⃣ 特征工程：滑动均值/标准差 + 一阶差分
feat = pd.DataFrame(r10)
feat["ma3"] = feat["value"].rolling(3).mean()     # 3 窗口滑动均值（趋势）
feat["std3"] = feat["value"].rolling(3).std()     # 3 窗口滑动标准差（波动）
feat["diff1"] = feat["value"].diff()              # 一阶差分（变化量）
print("⑥ 特征表（全部行）:")
print(feat.round(2))

# 7️⃣ 对比插值前后统计量
before = s["value"].dropna()
after_l = s_fill_l
stats = pd.DataFrame({
    "置NaN后": [before.count(), round(before.mean(),2), round(before.std(),2)],
    "插值后": [after_l.count(), round(after_l.mean(),2), round(after_l.std(),2)],
}, index=["count", "mean", "std"])
print("⑦ 统计量对比（插值填回 10 个点 → count 增加）:")
print(stats)

# 8️⃣ 导出 Parquet（列式存储）+ 读回验证
feat.to_parquet("d18_sensor00_features.parquet")
back = pd.read_parquet("d18_sensor00_features.parquet")
print("⑧ Parquet 导出:", feat.shape, "| 读回:", back.shape, "| 大小:",
      os.path.getsize("d18_sensor00_features.parquet"), "字节")

