import os
import json
from datetime import datetime

import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE_PIVOT = os.path.join(GOC, "data", "data_pivot.csv")
FILE_LOG = os.path.join(GOC, "logs", "tier2_log.csv")

POPS = ["cloudflare", "vultr_singapore", "vultr_seoul", "linode_singapore"]


def train_tier1_toan_bo(df):
    """Train lai mo hinh Tang 1 tren TOAN BO du lieu (khong chia test)
    de dung lam 'bo nao' cho Tang 2 trong luc mo phong giam sat."""
    le_vung, le_isp = LabelEncoder(), LabelEncoder()
    df["vung_ma"] = le_vung.fit_transform(df["vung_dia_ly"])
    df["isp_ma"] = le_isp.fit_transform(df["isp"])
    X = df[["vung_ma", "isp_ma", "gio", "thu_trong_tuan"]]
    y = df["pop_toi_uu"]
    mo_hinh = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
    mo_hinh.fit(X, y)
    return mo_hinh, le_vung, le_isp


def train_bo_phat_hien_bat_thuong(df):
    """Train 1 Isolation Forest rieng cho tung PoP, dua tren latency+throughput
    lich su cua chinh PoP do (dieu kien 'binh thuong' theo phan lon du lieu)."""
    bo_phat_hien = {}
    for pop in POPS:
        X = df[[f"latency_ms_{pop}", f"throughput_mbps_{pop}"]]
        clf = IsolationForest(contamination=0.05, random_state=42)
        clf.fit(X)
        bo_phat_hien[pop] = clf
    return bo_phat_hien


def chon_pop_thay_the(mo_hinh, le_vung, le_isp, dong, pop_dang_loi):
    """Chon PoP thay the bang cach ket hop:
    1) Tang 1 (goi y theo lich su: vung/isp/gio/thu), va
    2) latency THUC TE cua cac ung vien NGAY TAI THOI DIEM nay.
    Chi chon ung vien thuc su tot hon PoP dang loi; neu khong ung vien nao tot hon,
    danh dau la truong hop "khong co lua chon tot hon" va chon ung vien co latency thap nhat luc do."""
    X_dong = pd.DataFrame([{
        "vung_ma": le_vung.transform([dong["vung_dia_ly"]])[0],
        "isp_ma": le_isp.transform([dong["isp"]])[0],
        "gio": dong["gio"],
        "thu_trong_tuan": dong["thu_trong_tuan"],
    }])
    xac_suat = mo_hinh.predict_proba(X_dong)[0]
    cac_lop = mo_hinh.classes_
    xep_hang = sorted(zip(cac_lop, xac_suat), key=lambda x: -x[1])

    lat_dang_loi = dong[f"latency_ms_{pop_dang_loi}"]
    ung_vien = [pop for pop, _ in xep_hang if pop != pop_dang_loi]

    ung_vien_tot_hon = [p for p in ung_vien if dong[f"latency_ms_{p}"] < lat_dang_loi]

    if ung_vien_tot_hon:
        return ung_vien_tot_hon[0], True

    ung_vien_theo_latency = sorted(ung_vien, key=lambda p: dong[f"latency_ms_{p}"])
    return ung_vien_theo_latency[0], False


def mo_phong_giam_sat(df, mo_hinh, le_vung, le_isp, bo_phat_hien):
    """Chay qua tung dong theo thu tu thoi gian trong tung nhom vung/isp,
    mo phong 1 tien trinh giam sat lien tuc PoP dang dung."""
    log = []
    so_iso_rieng = [0]
    so_nguong_rieng = [0]
    so_ca_hai = [0]
    for (vung, isp), nhom in df.groupby(["vung_dia_ly", "isp"]):
        nhom = nhom.sort_values("timestamp").reset_index(drop=True)
        pop_dang_dung = nhom.loc[0, "pop_toi_uu"]

        for _, dong in nhom.iterrows():
            lat = dong[f"latency_ms_{pop_dang_dung}"]
            thr = dong[f"throughput_mbps_{pop_dang_dung}"]
            X_kiem_tra = pd.DataFrame([[lat, thr]], columns=[f"latency_ms_{pop_dang_dung}", f"throughput_mbps_{pop_dang_dung}"])
            iso_bat_thuong = bo_phat_hien[pop_dang_dung].predict(X_kiem_tra)[0] == -1  # Isolation Forest
            nguong_bat_thuong = dong[f"latency_bat_thuong_{pop_dang_dung}"] == 1        # nguong thong ke (buoc lam sach)

            # Phuong an A: chi kich hoat chuyen doi khi CA HAI cung xac nhan bat thuong
            la_bat_thuong = iso_bat_thuong and nguong_bat_thuong
            so_iso_rieng[0] += int(iso_bat_thuong)
            so_nguong_rieng[0] += int(nguong_bat_thuong)
            so_ca_hai[0] += int(la_bat_thuong)

            if la_bat_thuong:
                pop_moi, co_lua_chon_tot_hon = chon_pop_thay_the(mo_hinh, le_vung, le_isp, dong, pop_dang_dung)
                log.append({
                    "thoi_diem": dong["timestamp"],
                    "vung_dia_ly": vung,
                    "isp": isp,
                    "pop_cu": pop_dang_dung,
                    "latency_luc_phat_hien": round(float(lat), 1),
                    "pop_moi": pop_moi,
                    "latency_pop_moi_cung_thoi_diem": round(float(dong[f"latency_ms_{pop_moi}"]), 1),
                    "co_lua_chon_tot_hon": co_lua_chon_tot_hon,
                })
                pop_dang_dung = pop_moi

    print(f"\nIsolation Forest bao bat thuong: {so_iso_rieng[0]} lan")
    print(f"Nguong thong ke (>tb+3 do lech chuan) bao bat thuong: {so_nguong_rieng[0]} lan")
    print(f"Ca hai cung xac nhan (kich hoat chuyen doi that su): {so_ca_hai[0]} lan")
    return pd.DataFrame(log)


def main():
    df = pd.read_csv(FILE_PIVOT)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    print(f"Doc {len(df)} dong tu {FILE_PIVOT}")

    mo_hinh, le_vung, le_isp = train_tier1_toan_bo(df.copy())
    bo_phat_hien = train_bo_phat_hien_bat_thuong(df)

    log_df = mo_phong_giam_sat(df, mo_hinh, le_vung, le_isp, bo_phat_hien)

    print(f"\nSo lan phat hien bat thuong va chuyen doi PoP: {len(log_df)}")
    if len(log_df) > 0:
        print("\n5 lan chuyen doi dau tien:")
        print(log_df.head(5).to_string(index=False))
        print("\nSo lan chuyen doi theo vung/isp:")
        print(log_df.groupby(["vung_dia_ly", "isp"]).size())
        print("\nPoP hay bi phat hien loi nhat:")
        print(log_df["pop_cu"].value_counts())
        so_tot_hon = log_df["co_lua_chon_tot_hon"].sum()
        print(f"\nSo lan chon duoc PoP thay the TOT HON PoP loi: {so_tot_hon}/{len(log_df)}")
        if so_tot_hon < len(log_df):
            print("Cac lan KHONG co lua chon tot hon (su co dien rong, da chon PoP it te nhat):")
            print(log_df[~log_df["co_lua_chon_tot_hon"]].to_string(index=False))

    os.makedirs(os.path.dirname(FILE_LOG), exist_ok=True)
    log_df.to_csv(FILE_LOG, index=False)
    print(f"\nDa luu log: {FILE_LOG}")


if __name__ == "__main__":
    main()