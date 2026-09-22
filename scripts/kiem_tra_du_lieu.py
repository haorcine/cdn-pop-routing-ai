import os
import pandas as pd

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE_VAO = os.path.join(GOC, "data", "data_tong_hop.csv")

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 20)

df = pd.read_csv(FILE_VAO)
print(f"Tong: {len(df)} dong, cot: {list(df.columns)}\n")

print("=== 1. TIMESTAMP ===")
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
print(f"Timestamp khong doc duoc: {df['timestamp'].isna().sum()}")
print(f"Vi du 3 dong dau timestamp: {df['timestamp'].head(3).tolist()}\n")

print("=== 2. GIA TRI THIEU / KHONG HOP LE ===")
for cot in ["latency_ms", "throughput_mbps"]:
    print(f"{cot}: rong={df[cot].isna().sum()}, <=0={(df[cot] <= 0).sum()}")
khoa = ["timestamp", "vung_dia_ly", "isp", "pop_id"]
print(f"Dong trung khoa (timestamp+vung+isp+pop): {df.duplicated(subset=khoa).sum()}\n")

print("=== 3. THOI GIAN THU THAP THEO VUNG/ISP ===")
for (vung, isp), g in df.groupby(["vung_dia_ly", "isp"]):
    ts = g["timestamp"].dropna()
    cac_luot = pd.Series(sorted(ts.unique()))
    khoang_cach = cac_luot.diff().dropna().dt.total_seconds() / 60
    dong_moi_luot = g.groupby("timestamp").size().value_counts().to_dict()
    print(f"[{vung} - {isp}]")
    print(f"  Tu {ts.min()} den {ts.max()}  ({(ts.max() - ts.min()).total_seconds() / 86400:.1f} ngay)")
    print(f"  So luot do: {len(cac_luot)}, so ngay co du lieu: {ts.dt.normalize().nunique()}")
    print(f"  So dong moi luot do {{so dong: so luot}}: {dong_moi_luot}  (ky vong: chi co 4)")
    print(f"  Khoang cach giua 2 luot (phut): trung vi={khoang_cach.median():.1f}, lon nhat={khoang_cach.max():.1f}, so lan > 15 phut={(khoang_cach > 15).sum()}")
    print("  So luot do theo ngay:")
    print(cac_luot.dt.date.value_counts().sort_index().to_string())
    print()

print("=== 4. THONG KE LATENCY/THROUGHPUT THEO VUNG-ISP-POP ===")
print(df.groupby(["vung_dia_ly", "isp", "pop_id"])[["latency_ms", "throughput_mbps"]].agg(["min", "median", "max"]).round(1))


print("\n=== 5. DO PHU THEO KHUNG GIO (so luot do) ===")
def khung_gio(h):
    if 5 <= h <= 10:
        return "1_sang(5-10h)"
    if 11 <= h <= 13:
        return "2_trua(11-13h)"
    if 14 <= h <= 17:
        return "3_chieu(14-17h)"
    if 18 <= h <= 22:
        return "4_toi(18-22h)"
    return "5_dem(23-4h)"

luot = df.drop_duplicates(subset=["timestamp", "vung_dia_ly", "isp"]).copy()
luot["gio"] = luot["timestamp"].dt.hour
luot["khung_gio"] = luot["gio"].map(khung_gio)
print(pd.crosstab([luot["vung_dia_ly"], luot["isp"]], luot["khung_gio"]))
print("\nChi tiet theo tung gio (0-23):")
print(pd.crosstab([luot["vung_dia_ly"], luot["isp"]], luot["gio"]).to_string())