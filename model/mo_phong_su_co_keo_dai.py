"""
KICH BAN MO PHONG THU 2 - SU CO KEO DAI (mo phong dang "dut cap quang bien")

Khac voi kich ban 1 (Buoc 9/10, mot cu soc ngan roi hoi phuc nhanh - dung
HINH DANG trich thang tu du lieu that), kich ban nay mo phong mot PoP suy
giam va DUY TRI trang thai xau trong NHIEU luot do lien tiep, khong hoi
phuc ngay - giong dac diem su co ha tang keo dai duoc mo ta o muc 3 de
cuong (dut cap quang bien anh huong nhieu gio).

MINH BACH VE PHUONG PHAP: du lieu thu thap duoc CHI co cac su co dang cu
soc ngan (xem hinh dang trich o Buoc 9), khong co dot nao keo dai lien tuc
tren 1 PoP de trich truc tiep. Vi vay kich ban nay GIU NGUYEN DO CAO dinh
that da quan sat duoc (khong bia so), nhung KEO DAI SO LUOT giu trang thai
xau - day la GIA DINH VE DO DAI, duoc neu ro la kich ban xay dung them de
kiem tra kha nang cua he thong trong tinh huong keo dai hon, khong phai
so lieu trich truc tiep tu du lieu thuc te.
"""

import os
import pandas as pd
import numpy as np

from dinh_tuyen import BoDinhTuyen, POPS
from baseline import baseline_khoang_cach, baseline_latency_trung_binh
from mo_phong_su_co import trich_hinh_dang_su_co_that
from tong_hop_ket_qua import mo_phong_1_kich_ban_day_du

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE_PIVOT = os.path.join(GOC, "data", "data_pivot.csv")
CHU_KY_DO_PHUT = 10.8
SO_LUOT_KEO_DAI = 6  # ~1 tieng theo chu ky do 10.8 phut - gia dinh do dai


def xay_dung_khuon_mau_keo_dai(df, so_luot_keo_dai=SO_LUOT_KEO_DAI):
    """Lay DO CAO dinh THAT tu dot su co ngan da trich (Buoc 9), nhung
    KEO DAI trang thai xau ra nhieu luot lien tiep thay vi chi 1 luot,
    truoc khi hoi phuc dan ve binh thuong."""
    he_so_ngan = trich_hinh_dang_su_co_that(df)
    do_cao_dinh = he_so_ngan.max()

    print(f"Do cao dinh THAT duoc tai su dung: {do_cao_dinh:.2f} lan")
    print(f"So luot GIU TRANG THAI XAU (gia dinh do dai, khong trich tu du lieu): {so_luot_keo_dai}")

    he_so_keo_dai = np.array(
        [0.97, 0.99]
        + [do_cao_dinh] * so_luot_keo_dai
        + [1.3, 1.0]
    )
    print(f"Khuon mau su co keo dai: {np.round(he_so_keo_dai, 2).tolist()}\n")
    return he_so_keo_dai


def main():
    df = pd.read_csv(FILE_PIVOT)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    print(f"Doc {len(df)} dong tu {FILE_PIVOT}\n")

    pop_baseline_kc = baseline_khoang_cach()
    pop_baseline_tb = baseline_latency_trung_binh(df)
    print(f"Baseline khoang cach chon: {pop_baseline_kc}")
    print(f"Baseline latency trung binh chon: {pop_baseline_tb}\n")

    he_so_keo_dai = xay_dung_khuon_mau_keo_dai(df)
    bo_dinh_tuyen = BoDinhTuyen(df)

    tat_ca_kich_ban = []
    for (vung, isp), nhom in df.groupby(["vung_dia_ly", "isp"]):
        if len(nhom) < 30:
            continue
        vi_tri_bat_dau = len(nhom) // 3
        for pop in POPS:
            kq = mo_phong_1_kich_ban_day_du(
                df, vung, isp, pop, vi_tri_bat_dau, he_so_keo_dai, bo_dinh_tuyen,
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
    cai_thien_sau_dinh_kc = cai_thien_sau_dinh_tb = None

    if kich_ban_kc:
        df_kc = pd.concat([k["latency_toan_cua_so"] for k in kich_ban_kc], ignore_index=True)
        cai_thien_cua_so_kc = (df_kc["lat_baseline_kc"].mean() - df_kc["lat_ai"].mean()) / df_kc["lat_baseline_kc"].mean() * 100
        df_kc_sau = df_kc[df_kc["sau_dinh"]]
        if len(df_kc_sau) > 0:
            cai_thien_sau_dinh_kc = (df_kc_sau["lat_baseline_kc"].mean() - df_kc_sau["lat_ai"].mean()) / df_kc_sau["lat_baseline_kc"].mean() * 100

    if kich_ban_tb:
        df_tb = pd.concat([k["latency_toan_cua_so"] for k in kich_ban_tb], ignore_index=True)
        cai_thien_cua_so_tb = (df_tb["lat_baseline_tb"].mean() - df_tb["lat_ai"].mean()) / df_tb["lat_baseline_tb"].mean() * 100
        df_tb_sau = df_tb[df_tb["sau_dinh"]]
        if len(df_tb_sau) > 0:
            cai_thien_sau_dinh_tb = (df_tb_sau["lat_baseline_tb"].mean() - df_tb_sau["lat_ai"].mean()) / df_tb_sau["lat_baseline_tb"].mean() * 100

    def fmt(x):
        return f"{x:+.1f}%" if x is not None else "khong du du lieu"

    print("=" * 70)
    print("KET QUA KICH BAN 2 - SU CO KEO DAI (mo phong dut cap bien)")
    print("=" * 70)
    print(f"""
  % cai thien latency, trung binh CA CUA SO mo phong ({len(he_so_keo_dai)} luot):
       vs Baseline khoang cach       : {fmt(cai_thien_cua_so_kc)}
       vs Baseline latency trung binh: {fmt(cai_thien_cua_so_tb)}

  % cai thien latency, CAC LUOT SAU KHI DA PHAT HIEN VA CHUYEN DOI:
       vs Baseline khoang cach       : {fmt(cai_thien_sau_dinh_kc)}
       vs Baseline latency trung binh: {fmt(cai_thien_sau_dinh_tb)}

  Ty le phat hien dung PoP loi: {ty_le_phat_hien:.1f}% ({len(da_phat_hien)}/{len(tat_ca_kich_ban)} kich ban)
  So chu ky do can cho de phat hien: {so_chu_ky_tb:.2f} chu ky
  Thoi gian xu ly thuat toan: {xu_ly_ms_tb:.2f} ms
""")


if __name__ == "__main__":
    main()