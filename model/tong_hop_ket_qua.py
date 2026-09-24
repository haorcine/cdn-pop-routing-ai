"""
BUOC 10 - TONG HOP KET QUA CUOI CUNG (Chuong VI) - CHAY 1 LAN LA RA DU BANG

File nay tu chay lai toan bo: Buoc 7 (dieu kien binh thuong), Buoc 9
(ty le phat hien + thoi gian phan ung), va tinh % cai thien dieu kien co
su co (ca trung binh ca cua so mo phong LAN rieng tai dung DINH su co).
Khong can chay cac file khac roi chep tay so lieu qua - chi can chay file
nay la co bang tong ket day du.
"""

import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

from dinh_tuyen import BoDinhTuyen, POPS
from baseline import baseline_khoang_cach, baseline_latency_trung_binh
from mo_phong_su_co import trich_hinh_dang_su_co_that, tim_vi_tri_dinh_su_co

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE_PIVOT = os.path.join(GOC, "data", "data_pivot.csv")
CHU_KY_DO_PHUT = 10.8


# ========== PHAN 1: DIEU KIEN BINH THUONG (tuong duong Buoc 7) ==========

def tinh_ket_qua_binh_thuong(df, pop_baseline_kc, pop_baseline_tb):
    df = df.copy()
    le_vung, le_isp = LabelEncoder(), LabelEncoder()
    df["vung_ma"] = le_vung.fit_transform(df["vung_dia_ly"])
    df["isp_ma"] = le_isp.fit_transform(df["isp"])
    X = df[["vung_ma", "isp_ma", "gio", "thu_trong_tuan"]]
    y = df["pop_toi_uu"]

    so_mau_it_nhat = y.value_counts().min()
    stratify = y if so_mau_it_nhat >= 2 else None
    X_train, X_test, y_train, y_test, idx_train, idx_test = train_test_split(
        X, y, df.index, test_size=0.2, random_state=42, stratify=stratify
    )
    df_test = df.loc[idx_test]

    dt = DecisionTreeClassifier(max_depth=5, random_state=42, class_weight="balanced")
    dt.fit(X_train, y_train)
    rf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
    rf.fit(X_train, y_train)

    lat_dt = df_test.apply(lambda d: d[f"latency_ms_{dt.predict(X_test.loc[[d.name]])[0]}"], axis=1).mean()
    lat_rf = df_test.apply(lambda d: d[f"latency_ms_{rf.predict(X_test.loc[[d.name]])[0]}"], axis=1).mean()
    lat_kc = df_test[f"latency_ms_{pop_baseline_kc}"].mean()
    lat_tb = df_test[f"latency_ms_{pop_baseline_tb}"].mean()

    return {
        "cai_thien_dt_kc": (lat_kc - lat_dt) / lat_kc * 100,
        "cai_thien_dt_tb": (lat_tb - lat_dt) / lat_tb * 100,
        "cai_thien_rf_kc": (lat_kc - lat_rf) / lat_kc * 100,
        "cai_thien_rf_tb": (lat_tb - lat_rf) / lat_tb * 100,
    }


# ========== PHAN 2: DIEU KIEN CO SU CO (Buoc 9 + Buoc 10) ==========

def mo_phong_1_kich_ban_day_du(df_goc, vung, isp, pop_bi_loi, vi_tri_bat_dau, he_so_khuon_mau, bo_dinh_tuyen, pop_baseline_kc, pop_baseline_tb):
    """Ket hop Buoc 9 (phat hien/phan ung) va Buoc 10 (latency) trong 1 lan chay."""
    import time

    nhom = (
        df_goc[(df_goc["vung_dia_ly"] == vung) & (df_goc["isp"] == isp)]
        .sort_values("timestamp")
        .reset_index(drop=True)
        .copy()
    )
    if vi_tri_bat_dau + len(he_so_khuon_mau) > len(nhom):
        return None

    tb_pop = df_goc[f"latency_ms_{pop_bi_loi}"].mean()
    dl_pop = df_goc[f"latency_ms_{pop_bi_loi}"].std()
    nguong_bat_thuong = tb_pop + 3 * dl_pop
    trung_vi_binh_thuong = df_goc[f"latency_ms_{pop_bi_loi}"].median()

    for offset, he_so in enumerate(he_so_khuon_mau):
        idx = vi_tri_bat_dau + offset
        lat_moi = trung_vi_binh_thuong * he_so
        nhom.loc[idx, f"latency_ms_{pop_bi_loi}"] = lat_moi
        nhom.loc[idx, f"latency_bat_thuong_{pop_bi_loi}"] = int(lat_moi > nguong_bat_thuong)

    offset_dinh = tim_vi_tri_dinh_su_co(he_so_khuon_mau)
    vi_tri_dinh = vi_tri_bat_dau + offset_dinh
    thoi_diem_dinh_su_co = nhom.loc[vi_tri_dinh, "timestamp"]
    thoi_diem_ket_thuc = nhom.loc[min(vi_tri_bat_dau + len(he_so_khuon_mau) - 1, len(nhom) - 1), "timestamp"]

    pop_dang_dung = pop_bi_loi
    log = []
    dong_theo_vi_tri = {}
    for offset_hien_tai, (_, dong) in enumerate(nhom.iloc[vi_tri_bat_dau:vi_tri_bat_dau + len(he_so_khuon_mau)].iterrows()):
        dong_theo_vi_tri[offset_hien_tai] = {
            "lat_ai": dong[f"latency_ms_{pop_dang_dung}"],
            "lat_baseline_kc": dong[f"latency_ms_{pop_baseline_kc}"],
            "lat_baseline_tb": dong[f"latency_ms_{pop_baseline_tb}"],
            "sau_dinh": offset_hien_tai > offset_dinh,
        }
        bat_dau_dong_ho = time.perf_counter()
        pop_dang_dung, su_kien = bo_dinh_tuyen.xu_ly_1_buoc(dong, pop_dang_dung)
        thoi_gian_xu_ly_ms = (time.perf_counter() - bat_dau_dong_ho) * 1000
        if su_kien:
            su_kien["thoi_gian_xu_ly_thuat_toan_ms"] = round(thoi_gian_xu_ly_ms, 2)
            log.append(su_kien)

    log_trong_khung_su_co = [
        sk for sk in log
        if thoi_diem_dinh_su_co <= sk["thoi_diem"] <= thoi_diem_ket_thuc + pd.Timedelta(minutes=30)
        and sk["pop_cu"] == pop_bi_loi
    ]
    phat_hien_dung = len(log_trong_khung_su_co) > 0
    thoi_gian_phan_ung_phut = None
    xu_ly_ms = None
    if phat_hien_dung:
        thoi_diem_phat_hien_dau_tien = log_trong_khung_su_co[0]["thoi_diem"]
        thoi_gian_phan_ung_phut = (thoi_diem_phat_hien_dau_tien - thoi_diem_dinh_su_co).total_seconds() / 60
        xu_ly_ms = log_trong_khung_su_co[0]["thoi_gian_xu_ly_thuat_toan_ms"]

    return {
        "vung_dia_ly": vung,
        "isp": isp,
        "pop_bi_loi": pop_bi_loi,
        "phat_hien_dung": phat_hien_dung,
        "so_chu_ky_do_de_phat_hien": (
            round(thoi_gian_phan_ung_phut / CHU_KY_DO_PHUT) if thoi_gian_phan_ung_phut is not None else None
        ),
        "thoi_gian_xu_ly_thuat_toan_ms": xu_ly_ms,
        "latency_toan_cua_so": pd.DataFrame(dong_theo_vi_tri).T,
        "latency_dinh_su_co": dong_theo_vi_tri[offset_dinh],
    }


def main():
    df = pd.read_csv(FILE_PIVOT)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    print(f"Doc {len(df)} dong tu {FILE_PIVOT}\n")

    pop_baseline_kc = baseline_khoang_cach()
    pop_baseline_tb = baseline_latency_trung_binh(df)
    print(f"Baseline khoang cach chon: {pop_baseline_kc}")
    print(f"Baseline latency trung binh chon: {pop_baseline_tb}\n")

    print(">>> Dang tinh dieu kien BINH THUONG (Buoc 7)...")
    kq_binh_thuong = tinh_ket_qua_binh_thuong(df, pop_baseline_kc, pop_baseline_tb)

    print(">>> Dang tinh dieu kien CO SU CO (Buoc 9 + 10)...")
    he_so_khuon_mau = trich_hinh_dang_su_co_that(df)
    bo_dinh_tuyen = BoDinhTuyen(df)

    tat_ca_kich_ban = []
    for (vung, isp), nhom in df.groupby(["vung_dia_ly", "isp"]):
        if len(nhom) < 30:
            continue
        vi_tri_bat_dau = len(nhom) // 3
        for pop in POPS:
            kq = mo_phong_1_kich_ban_day_du(
                df, vung, isp, pop, vi_tri_bat_dau, he_so_khuon_mau, bo_dinh_tuyen,
                pop_baseline_kc, pop_baseline_tb,
            )
            if kq:
                tat_ca_kich_ban.append(kq)

    ty_le_phat_hien = sum(k["phat_hien_dung"] for k in tat_ca_kich_ban) / len(tat_ca_kich_ban) * 100
    da_phat_hien = [k for k in tat_ca_kich_ban if k["phat_hien_dung"]]
    so_chu_ky_tb = sum(k["so_chu_ky_do_de_phat_hien"] for k in da_phat_hien) / len(da_phat_hien)
    xu_ly_ms_tb = sum(k["thoi_gian_xu_ly_thuat_toan_ms"] for k in da_phat_hien) / len(da_phat_hien)

    kich_ban_kc = [k for k in tat_ca_kich_ban if k["pop_bi_loi"] == pop_baseline_kc]
    kich_ban_tb = [k for k in tat_ca_kich_ban if k["pop_bi_loi"] == pop_baseline_tb]

    cai_thien_cua_so_kc = cai_thien_cua_so_tb = None
    cai_thien_dinh_kc = cai_thien_dinh_tb = None
    cai_thien_sau_dinh_kc = cai_thien_sau_dinh_tb = None

    if kich_ban_kc:
        df_kc = pd.concat([k["latency_toan_cua_so"] for k in kich_ban_kc], ignore_index=True)
        cai_thien_cua_so_kc = (df_kc["lat_baseline_kc"].mean() - df_kc["lat_ai"].mean()) / df_kc["lat_baseline_kc"].mean() * 100
        dinh_kc = [k["latency_dinh_su_co"] for k in kich_ban_kc]
        lat_ai_dinh = sum(d["lat_ai"] for d in dinh_kc) / len(dinh_kc)
        lat_kc_dinh = sum(d["lat_baseline_kc"] for d in dinh_kc) / len(dinh_kc)
        cai_thien_dinh_kc = (lat_kc_dinh - lat_ai_dinh) / lat_kc_dinh * 100
        df_kc_sau = df_kc[df_kc["sau_dinh"]]
        if len(df_kc_sau) > 0:
            cai_thien_sau_dinh_kc = (df_kc_sau["lat_baseline_kc"].mean() - df_kc_sau["lat_ai"].mean()) / df_kc_sau["lat_baseline_kc"].mean() * 100

    if kich_ban_tb:
        df_tb = pd.concat([k["latency_toan_cua_so"] for k in kich_ban_tb], ignore_index=True)
        cai_thien_cua_so_tb = (df_tb["lat_baseline_tb"].mean() - df_tb["lat_ai"].mean()) / df_tb["lat_baseline_tb"].mean() * 100
        dinh_tb = [k["latency_dinh_su_co"] for k in kich_ban_tb]
        lat_ai_dinh2 = sum(d["lat_ai"] for d in dinh_tb) / len(dinh_tb)
        lat_tb_dinh = sum(d["lat_baseline_tb"] for d in dinh_tb) / len(dinh_tb)
        cai_thien_dinh_tb = (lat_tb_dinh - lat_ai_dinh2) / lat_tb_dinh * 100
        df_tb_sau = df_tb[df_tb["sau_dinh"]]
        if len(df_tb_sau) > 0:
            cai_thien_sau_dinh_tb = (df_tb_sau["lat_baseline_tb"].mean() - df_tb_sau["lat_ai"].mean()) / df_tb_sau["lat_baseline_tb"].mean() * 100

    def fmt(x):
        return f"{x:+.1f}%" if x is not None else "khong du du lieu"

    print("\n" + "=" * 70)
    print("BANG TONG KET CUOI CUNG - CHUONG VI (tu dong, khong can chep tay)")
    print("=" * 70)
    print(f"""
  1. % CAI THIEN LATENCY - DIEU KIEN BINH THUONG (tap test, 20% du lieu):
       Decision Tree vs Baseline khoang cach       : {fmt(kq_binh_thuong['cai_thien_dt_kc'])}
       Decision Tree vs Baseline latency trung binh: {fmt(kq_binh_thuong['cai_thien_dt_tb'])}
       Random Forest vs Baseline khoang cach       : {fmt(kq_binh_thuong['cai_thien_rf_kc'])}
       Random Forest vs Baseline latency trung binh: {fmt(kq_binh_thuong['cai_thien_rf_tb'])}

  2. % CAI THIEN LATENCY - DIEU KIEN CO SU CO (12 kich ban mo phong):
     a) Trung binh CA CUA SO mo phong (8 luot do, gom ca truoc/sau dinh):
       vs Baseline khoang cach       : {fmt(cai_thien_cua_so_kc)}
       vs Baseline latency trung binh: {fmt(cai_thien_cua_so_tb)}
     b) CHI TAI DUNG LUOT DINH SU CO (luon la 0%, vi ca AI va baseline deu
        "chiu" dung 1 lan doc gay ra phat hien - khong the tranh duoc):
       vs Baseline khoang cach       : {fmt(cai_thien_dinh_kc)}
       vs Baseline latency trung binh: {fmt(cai_thien_dinh_tb)}
     c) CAC LUOT SAU KHI DA PHAT HIEN VA CHUYEN DOI (day moi la gia tri
        THAT SU cua Tang 2 - AI da doi PoP, baseline thi khong bao gio doi):
       vs Baseline khoang cach       : {fmt(cai_thien_sau_dinh_kc)}
       vs Baseline latency trung binh: {fmt(cai_thien_sau_dinh_tb)}
  3. Ty le phat hien dung PoP loi: {ty_le_phat_hien:.1f}% ({len(da_phat_hien)}/{len(tat_ca_kich_ban)} kich ban)

  4. Thoi gian phan ung:
       So chu ky do can cho          : {so_chu_ky_tb:.2f} chu ky (moi chu ky ~{CHU_KY_DO_PHUT} phut)
       Thoi gian xu ly thuat toan    : {xu_ly_ms_tb:.2f} ms (do thuc te bang dong ho may)
""")


if __name__ == "__main__":
    main()