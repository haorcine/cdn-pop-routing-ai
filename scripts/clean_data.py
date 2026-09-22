import os
import pandas as pd
import numpy as np

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE_VAO = os.path.join(GOC, "data", "data_tong_hop.csv")
FILE_RA = os.path.join(GOC, "data", "data_sach.csv")


def lam_sach():
    df = pd.read_csv(FILE_VAO)
    truoc = len(df)
    print(f"Doc {truoc} dong tu {FILE_VAO}")

    # 1. Loai dong thieu latency hoac throughput
    df = df.dropna(subset=["latency_ms", "throughput_mbps"])
    print(f"Loai {truoc - len(df)} dong bi thieu latency/throughput")

    # 2. Loai dong latency/throughput <= 0 (khong hop le)
    truoc2 = len(df)
    df = df[(df["latency_ms"] > 0) & (df["throughput_mbps"] > 0)]
    print(f"Loai {truoc2 - len(df)} dong latency/throughput <= 0")

    # 3. Them cot gio, thu_trong_tuan tu timestamp
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["gio"] = df["timestamp"].dt.hour
    df["thu_trong_tuan"] = df["timestamp"].dt.dayofweek  # 0=Thu Hai ... 6=Chu Nhat

    # 4. Danh dau (khong xoa) latency bat thuong theo tung PoP
    def danh_dau(nhom):
        tb = nhom["latency_ms"].mean()
        dl = nhom["latency_ms"].std()
        nguong_tren = tb + 3 * dl
        return (nhom["latency_ms"] > nguong_tren).astype(int)

    df["latency_bat_thuong"] = (
        df.groupby("pop_id", group_keys=False)
        .apply(danh_dau, include_groups=False)
    )
    so_bat_thuong = df["latency_bat_thuong"].sum()
    print(f"Danh dau {so_bat_thuong} dong latency bat thuong (giu lai, khong xoa)")

    # 5. Loai dong trung hoan toan (neu co)
    truoc3 = len(df)
    df = df.drop_duplicates(subset=["timestamp", "vung_dia_ly", "isp", "pop_id"])
    print(f"Loai {truoc3 - len(df)} dong trung khoa timestamp+vung+isp+pop")

    df.to_csv(FILE_RA, index=False)
    print(f"\nDa luu {FILE_RA}: {len(df)} dong (tu {truoc} dong ban dau)")
    print("\nSo dong bat thuong theo vung/isp/pop:")
    print(df[df["latency_bat_thuong"] == 1].groupby(["vung_dia_ly", "isp", "pop_id"]).size())
    return df


if __name__ == "__main__":
    lam_sach()