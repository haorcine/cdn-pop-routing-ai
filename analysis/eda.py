import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE_SACH = os.path.join(GOC, "data", "data_sach.csv")
THU_MUC_RA = os.path.join(GOC, "analysis", "hinh_anh")
os.makedirs(THU_MUC_RA, exist_ok=True)

sns.set_theme(style="whitegrid")


def ve_bieu_do():
    df = pd.read_csv(FILE_SACH)
    print(f"Doc {len(df)} dong tu {FILE_SACH}")

    # Cot ket hop vung + isp de khong hieu lam (hien tai moi vung chi co 1 isp)
    df["vung_isp"] = df["vung_dia_ly"] + " - " + df["isp"]

    # 1. Latency theo PoP
    plt.figure(figsize=(8, 5))
    sns.boxplot(data=df, x="pop_id", y="latency_ms")
    plt.title("Phan bo latency theo PoP")
    plt.xlabel("PoP")
    plt.ylabel("Latency (ms)")
    plt.xticks(rotation=15)
    plt.tight_layout()
    duong_dan = os.path.join(THU_MUC_RA, "01_latency_theo_pop.png")
    plt.savefig(duong_dan, dpi=150)
    plt.close()
    print(f"Da luu {duong_dan}")

    # 2. Latency theo gio trong ngay
    plt.figure(figsize=(10, 5))
    sns.lineplot(data=df, x="gio", y="latency_ms", hue="pop_id", errorbar=("ci", 95), marker="o")
    plt.title("Latency trung binh theo gio trong ngay")
    plt.xlabel("Gio (0-23)")
    plt.ylabel("Latency (ms)")
    plt.xticks(range(0, 24))
    plt.tight_layout()
    duong_dan = os.path.join(THU_MUC_RA, "02_latency_theo_gio.png")
    plt.savefig(duong_dan, dpi=150)
    plt.close()
    print(f"Da luu {duong_dan}")

    # 3. Latency theo vung-ISP
    plt.figure(figsize=(9, 5))
    sns.boxplot(data=df, x="vung_isp", y="latency_ms", hue="pop_id")
    plt.title("Phan bo latency theo vung-ISP va PoP")
    plt.xlabel("Vung - ISP")
    plt.ylabel("Latency (ms)")
    plt.legend(title="PoP", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    duong_dan = os.path.join(THU_MUC_RA, "03_latency_theo_vung_isp.png")
    plt.savefig(duong_dan, dpi=150)
    plt.close()
    print(f"Da luu {duong_dan}")

    # 4. Throughput theo PoP
    plt.figure(figsize=(8, 5))
    sns.boxplot(data=df, x="pop_id", y="throughput_mbps")
    plt.title("Phan bo throughput theo PoP")
    plt.xlabel("PoP")
    plt.ylabel("Throughput (Mbps)")
    plt.xticks(rotation=15)
    plt.tight_layout()
    duong_dan = os.path.join(THU_MUC_RA, "04_throughput_theo_pop.png")
    plt.savefig(duong_dan, dpi=150)
    plt.close()
    print(f"Da luu {duong_dan}")

    print("\nThong ke nhanh latency theo PoP:")
    print(df.groupby("pop_id")["latency_ms"].describe()[["count", "mean", "50%", "std"]].round(1))


if __name__ == "__main__":
    ve_bieu_do()