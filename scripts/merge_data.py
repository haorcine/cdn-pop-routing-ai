import glob
import os
import pandas as pd

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THU_MUC_DATA = os.path.join(GOC, "data")
FILE_RA = os.path.join(THU_MUC_DATA, "data_tong_hop.csv")

COT_BAT_BUOC = ["timestamp", "vung_dia_ly", "isp", "pop_id", "latency_ms", "throughput_mbps"]
FILE_LOAI_TRU = {"data_tong_hop.csv", "data_sach.csv"}

# Bang chuan hoa: khoa viet thuong, khong can biet ban goc viet hoa hay khong
CHUAN_VUNG = {"bac": "Bac", "bắc": "Bac", "trung": "Trung", "nam": "Nam"}
CHUAN_ISP = {"vnpt": "VNPT", "viettel": "Viettel", "fpt": "FPT", "fpt telecom": "FPT"}


def chuan_hoa(cot, bang, ten_cot, ten_file):
    khoa = cot.astype(str).str.strip().str.casefold()
    moi = khoa.map(bang)
    la = cot[moi.isna()].unique()
    if len(la) > 0:
        raise ValueError(f"{ten_file}: gia tri la o cot {ten_cot}: {list(la)} - can them vao bang chuan hoa")
    return moi


def gop_du_lieu():
    cac_file = sorted(
        f for f in glob.glob(os.path.join(THU_MUC_DATA, "data_*.csv"))
        if os.path.basename(f) not in FILE_LOAI_TRU
    )
    if not cac_file:
        raise FileNotFoundError(f"Khong tim thay file data_*.csv trong {THU_MUC_DATA}")

    cac_df = []
    tong_dong_goc = 0
    for f in cac_file:
        ten = os.path.basename(f)
        df = pd.read_csv(f, encoding="utf-8-sig")
        thieu = set(COT_BAT_BUOC) - set(df.columns)
        if thieu:
            raise ValueError(f"{ten} thieu cot: {sorted(thieu)}")
        df = df[COT_BAT_BUOC].copy()
        df["vung_dia_ly"] = chuan_hoa(df["vung_dia_ly"], CHUAN_VUNG, "vung_dia_ly", ten)
        df["isp"] = chuan_hoa(df["isp"], CHUAN_ISP, "isp", ten)
        df["pop_id"] = df["pop_id"].astype(str).str.strip()
        print(f"{ten}: {len(df)} dong")
        tong_dong_goc += len(df)
        cac_df.append(df)

    tong = pd.concat(cac_df, ignore_index=True)
    print(f"\nTong dong cac file goc: {tong_dong_goc}")

    truoc = len(tong)
    tong = tong.drop_duplicates()
    print(f"Loai {truoc - len(tong)} dong trung lap hoan toan")

    tong.to_csv(FILE_RA, index=False)
    print(f"Da luu {FILE_RA}: {len(tong)} dong tu {len(cac_file)} file")
    print("\nSo dong theo vung/ISP:")
    print(tong.groupby(["vung_dia_ly", "isp"]).size())
    print("\nSo dong theo PoP:")
    print(tong["pop_id"].value_counts())
    return tong


if __name__ == "__main__":
    gop_du_lieu()