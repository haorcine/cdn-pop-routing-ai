import os
import pandas as pd

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE_VAO = os.path.join(GOC, "data", "data_sach.csv")
FILE_RA = os.path.join(GOC, "data", "data_pivot.csv")


def pivot_du_lieu():
    df = pd.read_csv(FILE_VAO)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    print(f"Doc {len(df)} dong tu {FILE_VAO}")

    khoa = ["timestamp", "vung_dia_ly", "isp", "gio", "thu_trong_tuan"]

    pivot = df.pivot_table(
        index=khoa,
        columns="pop_id",
        values=["latency_ms", "throughput_mbps", "latency_bat_thuong"],
    )
    pivot.columns = [f"{a}_{b}" for a, b in pivot.columns]
    pivot = pivot.reset_index()

    so_luot_truoc = pivot["timestamp"].count()
    pivot = pivot.dropna()
    so_luot_sau = len(pivot)
    print(f"So luot do truoc khi loai thieu PoP: {so_luot_truoc}")
    print(f"So luot do sau khi loai thieu PoP (con du 4 PoP): {so_luot_sau}")
    print(f"Loai {so_luot_truoc - so_luot_sau} luot do bi thieu PoP")

    cot_latency = [c for c in pivot.columns if c.startswith("latency_ms_")]
    pivot["pop_toi_uu"] = pivot[cot_latency].idxmin(axis=1).str.replace("latency_ms_", "")

    pivot.to_csv(FILE_RA, index=False)
    print(f"\nDa luu {FILE_RA}: {len(pivot)} dong, {len(pivot.columns)} cot")
    print("\nPhan bo nhan pop_toi_uu:")
    print(pivot["pop_toi_uu"].value_counts())
    print("\nPhan bo theo vung/isp:")
    print(pivot.groupby(["vung_dia_ly", "isp"]).size())
    return pivot


if __name__ == "__main__":
    pivot_du_lieu()