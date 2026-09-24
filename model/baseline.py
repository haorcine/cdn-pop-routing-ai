import os
import pandas as pd

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE_PIVOT = os.path.join(GOC, "data", "data_pivot.csv")

POP_GAN_NHAT_VN = "vultr_singapore"  # gan Viet Nam nhat trong 4 PoP


def baseline_khoang_cach(_df=None):
    """Luon tra ve 1 PoP co dinh gan Viet Nam nhat, khong xet input."""
    return POP_GAN_NHAT_VN


def baseline_latency_trung_binh(df_train):
    """Tinh latency trung binh lich su moi PoP tu tap train, chon PoP thap nhat."""
    cot_latency = [c for c in df_train.columns if c.startswith("latency_ms_")]
    trung_binh = df_train[cot_latency].mean()
    ten_pop = trung_binh.idxmin().replace("latency_ms_", "")
    return ten_pop


def latency_neu_chon(df, ten_pop):
    """Latency thuc te neu he thong luon chon ten_pop cho moi dong trong df."""
    return df[f"latency_ms_{ten_pop}"]


if __name__ == "__main__":
    df = pd.read_csv(FILE_PIVOT)
    print(f"Doc {len(df)} dong tu {FILE_PIVOT}\n")

    pop_kc = baseline_khoang_cach()
    pop_tb = baseline_latency_trung_binh(df)
    print(f"baseline_khoang_cach chon: {pop_kc}")
    print(f"baseline_latency_trung_binh chon: {pop_tb}\n")

    for ten, pop in [("khoang_cach", pop_kc), ("latency_trung_binh", pop_tb)]:
        lat = latency_neu_chon(df, pop)
        print(f"Baseline {ten} ({pop}): latency trung binh = {lat.mean():.1f} ms, trung vi = {lat.median():.1f} ms")