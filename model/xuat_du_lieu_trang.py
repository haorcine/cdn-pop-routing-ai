"""
GIAI DOAN 1 - XUAT DU LIEU RA JSON CHO TRANG MO PHONG DONG

Doc du lieu that (data_pivot.csv) va chay lai Bo Dinh Tuyen (Tang 1 + Tang 2)
de tao 3 file JSON, moi file ung voi 1 tab tren trang:
  - du_lieu_that.json      : toan bo du lieu that, khong cat, ca 3 vung
  - su_co_ngan_han.json    : kich ban cu soc ngan (Buoc 9), 1 kich ban/vung
  - su_co_keo_dai.json     : kich ban su co keo dai (Buoc 10), 1 kich ban/vung

JSON CHI CHUA SO LIEU (khong chua toa do ban do) - vi tri hien thi tren
ban do la logic giao dien (Giai doan 2), khong phai du lieu.
"""

import os
import json
import pandas as pd
import numpy as np

from dinh_tuyen import BoDinhTuyen, POPS
from mo_phong_su_co import trich_hinh_dang_su_co_that, tim_vi_tri_dinh_su_co

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE_PIVOT = os.path.join(GOC, "data", "data_pivot.csv")
THU_MUC_RA = os.path.join(GOC, "web_data")
SO_LUOT_KEO_DAI = 6


def latency_tai_dong(dong):
    return {pop: round(float(dong[f"latency_ms_{pop}"]), 1) for pop in POPS}


def xuat_du_lieu_that(df, bo_dinh_tuyen):
    """Chay Bo Dinh Tuyen qua TOAN BO du lieu that (khong cat), ghi lai
    latency 4 PoP + PoP dang dung tai moi luot, va moi lan chuyen doi."""
    ket_qua_theo_vung = []
    for (vung, isp), nhom in df.groupby(["vung_dia_ly", "isp"]):
        nhom = nhom.sort_values("timestamp").reset_index(drop=True)
        khung = []
        su_kien = []
        pop_dang_dung = bo_dinh_tuyen.chon_pop_ban_dau(
            nhom.loc[0, "vung_dia_ly"], nhom.loc[0, "isp"], nhom.loc[0, "gio"], nhom.loc[0, "thu_trong_tuan"]
        )
        for t, (_, dong) in enumerate(nhom.iterrows()):
            khung.append({
                "t": t,
                "thoi_diem": dong["timestamp"],
                "latency": latency_tai_dong(dong),
                "pop_dang_dung": pop_dang_dung,
                "bat_thuong": bool(dong[f"latency_bat_thuong_{pop_dang_dung}"] == 1),
            })
            pop_dang_dung_moi, sk = bo_dinh_tuyen.xu_ly_1_buoc(dong, pop_dang_dung)
            if sk:
                su_kien.append({
                    "t": t,
                    "thoi_diem": sk["thoi_diem"],
                    "pop_cu": sk["pop_cu"],
                    "pop_moi": sk["pop_moi"],
                    "latency_luc_phat_hien": sk["latency_luc_phat_hien"],
                    "latency_pop_moi": sk["latency_pop_moi_cung_thoi_diem"],
                })
            pop_dang_dung = pop_dang_dung_moi

        ket_qua_theo_vung.append({"vung_dia_ly": vung, "isp": isp, "khung": khung, "su_kien_chuyen_doi": su_kien})

    return {"loai": "du_lieu_that", "vung": ket_qua_theo_vung}


def xuat_kich_ban_mo_phong(df, bo_dinh_tuyen, he_so_khuon_mau, loai):
    """Voi moi vung, chon PoP MA VUNG DO TU NHIEN DANG DUNG (theo Tang 1)
    lam 'nan nhan', ap khuon mau su co, chay Bo Dinh Tuyen tu diem do."""
    ket_qua_theo_vung = []
    for (vung, isp), nhom_goc in df.groupby(["vung_dia_ly", "isp"]):
        nhom_goc = nhom_goc.sort_values("timestamp").reset_index(drop=True)
        if len(nhom_goc) < 30:
            continue
        vi_tri_bat_dau = len(nhom_goc) // 3

        dong_bat_dau = nhom_goc.loc[vi_tri_bat_dau]
        pop_bi_loi = bo_dinh_tuyen.chon_pop_ban_dau(
            dong_bat_dau["vung_dia_ly"], dong_bat_dau["isp"], dong_bat_dau["gio"], dong_bat_dau["thu_trong_tuan"]
        )

        nhom = nhom_goc.copy()
        tb_pop = df[f"latency_ms_{pop_bi_loi}"].mean()
        dl_pop = df[f"latency_ms_{pop_bi_loi}"].std()
        nguong = tb_pop + 3 * dl_pop
        trung_vi = df[f"latency_ms_{pop_bi_loi}"].median()
        for offset, he_so in enumerate(he_so_khuon_mau):
            idx = vi_tri_bat_dau + offset
            if idx >= len(nhom):
                break
            lat_moi = trung_vi * he_so
            nhom.loc[idx, f"latency_ms_{pop_bi_loi}"] = lat_moi
            nhom.loc[idx, f"latency_bat_thuong_{pop_bi_loi}"] = int(lat_moi > nguong)

        diem_dau = max(0, vi_tri_bat_dau - 3)
        diem_cuoi = min(len(nhom), vi_tri_bat_dau + len(he_so_khuon_mau) + 5)

        khung = []
        su_kien = []
        pop_dang_dung = pop_bi_loi
        for t, idx in enumerate(range(diem_dau, diem_cuoi)):
            dong = nhom.loc[idx]
            khung.append({
                "t": t,
                "thoi_diem": dong["timestamp"],
                "latency": latency_tai_dong(dong),
                "pop_dang_dung": pop_dang_dung,
                "bat_thuong": bool(dong[f"latency_bat_thuong_{pop_dang_dung}"] == 1),
            })
            if idx >= vi_tri_bat_dau:
                pop_dang_dung_moi, sk = bo_dinh_tuyen.xu_ly_1_buoc(dong, pop_dang_dung)
                if sk:
                    su_kien.append({
                        "t": t,
                        "thoi_diem": sk["thoi_diem"],
                        "pop_cu": sk["pop_cu"],
                        "pop_moi": sk["pop_moi"],
                        "latency_luc_phat_hien": sk["latency_luc_phat_hien"],
                        "latency_pop_moi": sk["latency_pop_moi_cung_thoi_diem"],
                    })
                pop_dang_dung = pop_dang_dung_moi

        ket_qua_theo_vung.append({
            "vung_dia_ly": vung, "isp": isp, "pop_bi_loi": pop_bi_loi,
            "khung": khung, "su_kien_chuyen_doi": su_kien,
        })

    return {"loai": loai, "vung": ket_qua_theo_vung}


class BoMaHoaJSON(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (pd.Timestamp,)):
            return o.isoformat()
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.floating,)):
            return float(o)
        if isinstance(o, (np.bool_,)):
            return bool(o)
        return super().default(o)


def main():
    os.makedirs(THU_MUC_RA, exist_ok=True)
    df = pd.read_csv(FILE_PIVOT)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    print(f"Doc {len(df)} dong tu {FILE_PIVOT}\n")

    bo_dinh_tuyen = BoDinhTuyen(df)

    print(">>> Xuat du_lieu_that.json ...")
    du_lieu_that = xuat_du_lieu_that(df, bo_dinh_tuyen)
    duong_dan = os.path.join(THU_MUC_RA, "du_lieu_that.json")
    with open(duong_dan, "w", encoding="utf-8") as f:
        json.dump(du_lieu_that, f, cls=BoMaHoaJSON, ensure_ascii=False)
    tong_khung = sum(len(v["khung"]) for v in du_lieu_that["vung"])
    tong_su_kien = sum(len(v["su_kien_chuyen_doi"]) for v in du_lieu_that["vung"])
    print(f"    {tong_khung} khung thoi gian, {tong_su_kien} su kien chuyen doi -> {duong_dan}")

    print(">>> Xuat su_co_ngan_han.json ...")
    he_so_ngan = trich_hinh_dang_su_co_that(df)
    kich_ban_ngan = xuat_kich_ban_mo_phong(df, bo_dinh_tuyen, he_so_ngan, "su_co_ngan_han")
    duong_dan = os.path.join(THU_MUC_RA, "su_co_ngan_han.json")
    with open(duong_dan, "w", encoding="utf-8") as f:
        json.dump(kich_ban_ngan, f, cls=BoMaHoaJSON, ensure_ascii=False)
    print(f"    {len(kich_ban_ngan['vung'])} vung -> {duong_dan}")

    print(">>> Xuat su_co_keo_dai.json ...")
    do_cao_dinh = he_so_ngan.max()
    he_so_dai = np.array([0.97, 0.99] + [do_cao_dinh] * SO_LUOT_KEO_DAI + [1.3, 1.0])
    kich_ban_dai = xuat_kich_ban_mo_phong(df, bo_dinh_tuyen, he_so_dai, "su_co_keo_dai")
    duong_dan = os.path.join(THU_MUC_RA, "su_co_keo_dai.json")
    with open(duong_dan, "w", encoding="utf-8") as f:
        json.dump(kich_ban_dai, f, cls=BoMaHoaJSON, ensure_ascii=False)
    print(f"    {len(kich_ban_dai['vung'])} vung -> {duong_dan}")

    print(f"\nHoan tat. Cac file JSON nam trong: {THU_MUC_RA}")


if __name__ == "__main__":
    main()