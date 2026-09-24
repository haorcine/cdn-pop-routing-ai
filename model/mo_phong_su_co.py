"""
KICH BAN MO PHONG SU CO (theo de cuong muc 7, Kich ban 2)

Chu dong gia lap 1 PoP bi suy giam hieu nang, DUA TREN HINH DANG SUY GIAM
LATENCY THAT da ghi nhan duoc trong du lieu (khong bia so lieu). Sau do cho
Bo Dinh Tuyen (Tang 1 + Tang 2) chay qua kich ban de do:
  - Ty le phat hien dung PoP loi (tren nhieu kich ban thu nghiem)
  - So chu ky do can de phat hien (gioi han boi tan suat thu thap du lieu)
  - Thoi gian XU LY THUAT TOAN thuc te (do bang dong ho may, khong phai
    gia dinh) - tach rieng khoi do tre cua chu ky do
"""

import os
import time
import pandas as pd
import numpy as np

from dinh_tuyen import BoDinhTuyen, POPS

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE_PIVOT = os.path.join(GOC, "data", "data_pivot.csv")

CHU_KY_DO_PHUT = 10.8  # chu ky do trung binh thuc te cua du lieu (xem Buoc 2)


def trich_hinh_dang_su_co_that(df, do_dai=8):
    """Tim mot dot bat thuong THAT trong du lieu (latency_bat_thuong_<pop>==1),
    lay chuoi latency quanh diem do, chuan hoa thanh he so nhan so voi
    latency trung vi 'binh thuong' cua chinh PoP do. Day la 'khuon mau'
    dung de mo phong sang cac tinh huong khac - khong bia so, chi tai su
    dung dang suy giam da xay ra that."""
    for pop in POPS:
        cot = f"latency_bat_thuong_{pop}"
        idx_bat_thuong = df.index[df[cot] == 1].tolist()
        if not idx_bat_thuong:
            continue
        i = idx_bat_thuong[0]
        lo = max(0, i - 2)
        hi = min(len(df), lo + do_dai)
        doan = df.loc[lo:hi - 1, f"latency_ms_{pop}"].values
        trung_vi_binh_thuong = df[f"latency_ms_{pop}"].median()
        he_so = doan / trung_vi_binh_thuong
        print(f"Trich hinh dang tu dot su co that cua '{pop}' (dong {lo}-{hi-1}):")
        print(f"  He so nhan so voi trung vi binh thuong: {np.round(he_so, 2).tolist()}")
        return he_so
    raise ValueError("Khong tim thay dot bat thuong nao trong du lieu de lam khuon mau")


def tim_vi_tri_dinh_su_co(he_so_khuon_mau, nguong_he_so=2.0):
    """Tra ve vi tri (offset) dau tien trong khuon mau ma he so nhan
    vuot qua nguong_he_so - do la thoi diem su co THAT SU bat dau
    (khac voi dau cua so mo phong, von co the bao gom vai luot binh
    thuong truoc do)."""
    for i, he_so in enumerate(he_so_khuon_mau):
        if he_so > nguong_he_so:
            return i
    return 0


def mo_phong_1_kich_ban(df_goc, vung, isp, pop_bi_loi, vi_tri_bat_dau, he_so_khuon_mau, bo_dinh_tuyen):
    """Ap khuon mau su co that len 1 doan du lieu that cua (vung, isp, pop_bi_loi),
    bat dau tu vi_tri_bat_dau. Cho Bo Dinh Tuyen chay TU DIEM SU CO BAT DAU,
    voi PoP dang dung = pop_bi_loi, do thoi gian phat hien + phan ung TINH TU
    DINH SU CO THAT (khong tinh tu dau cua so mo phong, vi vai luot dau co the
    van la latency binh thuong theo dung khuon mau da trich)."""
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

    vi_tri_dinh = vi_tri_bat_dau + tim_vi_tri_dinh_su_co(he_so_khuon_mau)
    thoi_diem_dinh_su_co = nhom.loc[vi_tri_dinh, "timestamp"]
    thoi_diem_ket_thuc = nhom.loc[min(vi_tri_bat_dau + len(he_so_khuon_mau) - 1, len(nhom) - 1), "timestamp"]

    # Chi bat dau giam sat TU DIEM XAY RA SU CO, voi gia dinh he thong dang
    # dung dung PoP nay luc do. Khong chay tu dau nhom, vi mot bat thuong
    # KHAC (khong lien quan) xay ra som hon co the da khien he thong doi
    # PoP truoc khi su co mo phong bat dau, lam sai lech phep do.
    pop_dang_dung = pop_bi_loi
    log = []
    for _, dong in nhom.iloc[vi_tri_bat_dau:].iterrows():
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
    if phat_hien_dung:
        thoi_diem_phat_hien_dau_tien = log_trong_khung_su_co[0]["thoi_diem"]
        thoi_gian_phan_ung_phut = (thoi_diem_phat_hien_dau_tien - thoi_diem_dinh_su_co).total_seconds() / 60

    return {
        "vung_dia_ly": vung,
        "isp": isp,
        "pop_bi_loi": pop_bi_loi,
        "thoi_diem_dinh_su_co": thoi_diem_dinh_su_co,
        "phat_hien_dung": phat_hien_dung,
        "so_chu_ky_do_de_phat_hien": (
            round(thoi_gian_phan_ung_phut / CHU_KY_DO_PHUT) if thoi_gian_phan_ung_phut is not None else None
        ),
        "thoi_gian_xu_ly_thuat_toan_ms": (
            log_trong_khung_su_co[0]["thoi_gian_xu_ly_thuat_toan_ms"] if phat_hien_dung else None
        ),
        "pop_chuyen_sang": log_trong_khung_su_co[0]["pop_moi"] if phat_hien_dung else None,
    }


def main():
    df = pd.read_csv(FILE_PIVOT)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    print(f"Doc {len(df)} dong tu {FILE_PIVOT}\n")

    he_so_khuon_mau = trich_hinh_dang_su_co_that(df)
    print()

    bo_dinh_tuyen = BoDinhTuyen(df)

    ket_qua = []
    for (vung, isp), nhom in df.groupby(["vung_dia_ly", "isp"]):
        so_dong = len(nhom)
        if so_dong < 30:
            continue
        vi_tri_bat_dau = so_dong // 3
        for pop in POPS:
            kq = mo_phong_1_kich_ban(df, vung, isp, pop, vi_tri_bat_dau, he_so_khuon_mau, bo_dinh_tuyen)
            if kq:
                ket_qua.append(kq)

    kq_df = pd.DataFrame(ket_qua)
    print(f"Tong so kich ban da chay: {len(kq_df)}\n")
    print(kq_df.to_string(index=False))

    ty_le_phat_hien = kq_df["phat_hien_dung"].mean() * 100
    da_phat_hien = kq_df.loc[kq_df["phat_hien_dung"]]
    so_chu_ky_tb = da_phat_hien["so_chu_ky_do_de_phat_hien"].mean()
    xu_ly_ms_tb = da_phat_hien["thoi_gian_xu_ly_thuat_toan_ms"].mean()

    print(f"\n=== KET QUA TONG HOP (Chuong VI) ===")
    print(f"Ty le phat hien dung: {ty_le_phat_hien:.1f}% ({kq_df['phat_hien_dung'].sum()}/{len(kq_df)} kich ban)")
    print(f"So chu ky do trung binh de phat hien: {so_chu_ky_tb:.2f} chu ky (moi chu ky ~{CHU_KY_DO_PHUT} phut theo du lieu that)")
    print(f"  -> 0 chu ky cho = he thong bat duoc su co ngay trong chu ky no xay ra,")
    print(f"     khong can cho them lan do nao ke tiep.")
    print(f"Thoi gian XU LY THUAT TOAN trung binh (Isolation Forest + tra cuu Tang 1): {xu_ly_ms_tb:.2f} ms")
    print(f"  -> Day la thoi gian tinh toan thuc te cua thuat toan (do bang dong ho may),")
    print(f"     KHONG bao gom do tre cua chu ky do (~{CHU_KY_DO_PHUT} phut) - yeu to nay phu")
    print(f"     thuoc tan suat thu thap du lieu, khong phai toc do xu ly cua mo hinh AI/ML.")


if __name__ == "__main__":
    main()