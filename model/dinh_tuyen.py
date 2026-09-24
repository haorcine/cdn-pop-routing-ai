"""
BO DINH TUYEN - noi ghep Tang 1 (chon PoP theo ngu canh) va
Tang 2 (giam sat + tu dong chuyen doi) thanh MOT luong duy nhat.

Day la "bo nao trung tam" cua he thong: moi noi khac (mo phong tren
du lieu that trong tier2_anomaly.py, hay kich ban mo phong su co o
Buoc 9) deu nen goi qua class BoDinhTuyen nay thay vi tu viet lai
logic chon PoP / phat hien bat thuong.
"""

import os
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE_PIVOT = os.path.join(GOC, "data", "data_pivot.csv")

POPS = ["cloudflare", "vultr_singapore", "vultr_seoul", "linode_singapore"]


class BoDinhTuyen:
    """Ghep Tang 1 (chon PoP toi uu ban dau) va Tang 2 (giam sat +
    tu dong chuyen doi khi bat thuong) thanh mot bo dieu khien duy nhat."""

    def __init__(self, df_huan_luyen):
        """df_huan_luyen: DataFrame dang pivot (data_pivot.csv), dung de
        train Tang 1 va cac bo phat hien bat thuong cua Tang 2."""
        self._train_tang1(df_huan_luyen.copy())
        self._train_tang2(df_huan_luyen)

    # ---------- Tang 1: chon PoP theo ngu canh ----------

    def _train_tang1(self, df):
        self.le_vung = LabelEncoder()
        self.le_isp = LabelEncoder()
        df["vung_ma"] = self.le_vung.fit_transform(df["vung_dia_ly"])
        df["isp_ma"] = self.le_isp.fit_transform(df["isp"])
        X = df[["vung_ma", "isp_ma", "gio", "thu_trong_tuan"]]
        y = df["pop_toi_uu"]
        self.mo_hinh_tang1 = RandomForestClassifier(
            n_estimators=100, random_state=42, class_weight="balanced"
        )
        self.mo_hinh_tang1.fit(X, y)

    def _xep_hang_tang1(self, vung, isp, gio, thu):
        """Tra ve danh sach PoP xep hang theo xac suat toi uu cua Tang 1,
        tu cao den thap."""
        X_dong = pd.DataFrame([{
            "vung_ma": self.le_vung.transform([vung])[0],
            "isp_ma": self.le_isp.transform([isp])[0],
            "gio": gio,
            "thu_trong_tuan": thu,
        }])
        xac_suat = self.mo_hinh_tang1.predict_proba(X_dong)[0]
        cac_lop = self.mo_hinh_tang1.classes_
        return [pop for pop, _ in sorted(zip(cac_lop, xac_suat), key=lambda x: -x[1])]

    def chon_pop_ban_dau(self, vung, isp, gio, thu):
        """Goi Tang 1: dung khi he thong CHUA co PoP nao dang dung
        (vd luc khoi dong, hoac dau moi phien lam viec)."""
        return self._xep_hang_tang1(vung, isp, gio, thu)[0]

    # ---------- Tang 2: giam sat + tu dong chuyen doi ----------

    def _train_tang2(self, df):
        self.bo_phat_hien = {}
        for pop in POPS:
            X = df[[f"latency_ms_{pop}", f"throughput_mbps_{pop}"]]
            clf = IsolationForest(contamination=0.05, random_state=42)
            clf.fit(X)
            self.bo_phat_hien[pop] = clf

    def kiem_tra_bat_thuong(self, dong, pop_dang_dung):
        """Tra ve True/False: PoP dang dung co dang bat thuong tai thoi
        diem cua 'dong' hay khong. Ket hop Isolation Forest + nguong
        thong ke (co san trong cot latency_bat_thuong_<pop>) - chi bao
        bat thuong khi CA HAI cung xac nhan, de giam bao dong gia."""
        lat = dong[f"latency_ms_{pop_dang_dung}"]
        thr = dong[f"throughput_mbps_{pop_dang_dung}"]
        X_kiem_tra = pd.DataFrame(
            [[lat, thr]],
            columns=[f"latency_ms_{pop_dang_dung}", f"throughput_mbps_{pop_dang_dung}"],
        )
        iso_bat_thuong = self.bo_phat_hien[pop_dang_dung].predict(X_kiem_tra)[0] == -1
        nguong_bat_thuong = dong[f"latency_bat_thuong_{pop_dang_dung}"] == 1
        return iso_bat_thuong and nguong_bat_thuong

    def chon_pop_thay_the(self, dong, pop_dang_loi):
        """Goi Tang 1 de xep hang ung vien, nhung uu tien ung vien nao
        THUC SU co latency thap hon PoP dang loi NGAY TAI THOI DIEM nay.
        Tra ve (pop_moi, co_tot_hon_khong).

        LUU Y: danh sach ung vien luon lay tu TOAN BO POPS (hang so toan
        cuc), khong chi tu cac lop ma mo hinh Tang 1 "biet". Neu du lieu
        lech nhan nang, mo hinh co the chi hoc duoc rat it lop, gay loi
        neu chi dung classes_ lam ung vien."""
        xep_hang = self._xep_hang_tang1(
            dong["vung_dia_ly"], dong["isp"], dong["gio"], dong["thu_trong_tuan"]
        )
        lat_dang_loi = dong[f"latency_ms_{pop_dang_loi}"]

        ung_vien_theo_tang1 = [p for p in xep_hang if p != pop_dang_loi]
        ung_vien_tot_hon = [p for p in ung_vien_theo_tang1 if dong[f"latency_ms_{p}"] < lat_dang_loi]
        if ung_vien_tot_hon:
            return ung_vien_tot_hon[0], True

        ung_vien_toan_bo = [p for p in POPS if p != pop_dang_loi]
        ung_vien_tot_hon_toan_bo = [p for p in ung_vien_toan_bo if dong[f"latency_ms_{p}"] < lat_dang_loi]
        if ung_vien_tot_hon_toan_bo:
            uu_tien = [p for p in ung_vien_theo_tang1 if p in ung_vien_tot_hon_toan_bo]
            return (uu_tien[0] if uu_tien else ung_vien_tot_hon_toan_bo[0]), True

        ung_vien_theo_latency = sorted(ung_vien_toan_bo, key=lambda p: dong[f"latency_ms_{p}"])
        return ung_vien_theo_latency[0], False

    # ---------- Ham tong hop: xu ly 1 buoc thoi gian ----------

    def xu_ly_1_buoc(self, dong, pop_dang_dung):
        """Goi moi buoc mot lan (vd moi 10 phut khi giam sat thuc te).
        Tra ve (pop_nen_dung_tiep_theo, log_su_kien_hoac_None).
        Day la diem duy nhat ma phan mo phong / kich ban su co nen goi toi,
        thay vi tu viet lai logic kiem tra + chuyen doi."""
        if self.kiem_tra_bat_thuong(dong, pop_dang_dung):
            pop_moi, tot_hon = self.chon_pop_thay_the(dong, pop_dang_dung)
            su_kien = {
                "thoi_diem": dong["timestamp"],
                "vung_dia_ly": dong["vung_dia_ly"],
                "isp": dong["isp"],
                "pop_cu": pop_dang_dung,
                "latency_luc_phat_hien": round(float(dong[f"latency_ms_{pop_dang_dung}"]), 1),
                "pop_moi": pop_moi,
                "latency_pop_moi_cung_thoi_diem": round(float(dong[f"latency_ms_{pop_moi}"]), 1),
                "co_lua_chon_tot_hon": tot_hon,
            }
            return pop_moi, su_kien
        return pop_dang_dung, None


def _demo():
    """Chay thu bo dinh tuyen tren toan bo data_pivot.csv, giong het
    cach tier2_anomaly.py lam, de kiem chung ket qua khop nhau."""
    df = pd.read_csv(FILE_PIVOT)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    print(f"Doc {len(df)} dong tu {FILE_PIVOT}")

    bo_dinh_tuyen = BoDinhTuyen(df)

    log = []
    for (vung, isp), nhom in df.groupby(["vung_dia_ly", "isp"]):
        nhom = nhom.sort_values("timestamp").reset_index(drop=True)
        dong_dau = nhom.loc[0]
        pop_dang_dung = bo_dinh_tuyen.chon_pop_ban_dau(
            dong_dau["vung_dia_ly"], dong_dau["isp"], dong_dau["gio"], dong_dau["thu_trong_tuan"]
        )
        for _, dong in nhom.iterrows():
            pop_dang_dung, su_kien = bo_dinh_tuyen.xu_ly_1_buoc(dong, pop_dang_dung)
            if su_kien:
                log.append(su_kien)

    log_df = pd.DataFrame(log)
    print(f"\nSo lan chuyen doi: {len(log_df)}")
    if len(log_df) > 0:
        print(log_df.to_string(index=False))


if __name__ == "__main__":
    _demo()