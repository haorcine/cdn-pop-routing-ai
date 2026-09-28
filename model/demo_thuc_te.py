"""
demo_thuc_te.py - Demo he thong chay THAT (khong phai mo phong tren giao dien).

Moi chu ky: ping that toi 4 PoP -> dua vao BoDinhTuyen (Tang 1 + Tang 2 that:
Isolation Forest + nguong 3 sigma + Random Forest) -> tu chuyen PoP neu bat thuong.
Ban dung Clumsy (Windows) de lam cham ket noi toi PoP dang dung, roi xem he thong phan ung.

Dat file nay vao thu muc model/ (cung cho voi dinh_tuyen.py). Chay bang quyen binh thuong.
"""
import os
import re
import sys
import time
import socket
import threading
import subprocess
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dinh_tuyen import BoDinhTuyen, POPS

# ===================== CAU HINH: DOI CHO DUNG MAY BAN =====================
VUNG = "Nam"          # phai la 1 trong: Bac, Trung, Nam (viet dung nhu trong data_pivot.csv)
ISP = "VNPT"          # phai la 1 trong: VNPT, Viettel, FPT
CHU_KY_GIAY = 2       # nghi giua 2 lan do (chu ky demo, khong phai 10 phut nhu luc thu thap)
SO_GOI_PING = 2       # so goi ping moi PoP moi chu ky
TIMEOUT_MS = 3000     # cho toi da moi goi ping (phai > do tre gay nghen)
SO_CHU_KY_TOI_DA = 60 # tu dung sau bay nhieu chu ky
# =========================================================================

HOSTS = {
    "cloudflare": "speed.cloudflare.com",
    "vultr_singapore": "sgp-ping.vultr.com",
    "vultr_seoul": "sel-kor-ping.vultr.com",
    "linode_singapore": "speedtest.singapore.linode.com",
}

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE_PIVOT = os.path.join(GOC, "data", "data_pivot.csv")
THU_MUC_LOG = os.path.join(GOC, "logs")
os.makedirs(THU_MUC_LOG, exist_ok=True)
FILE_LOG = os.path.join(THU_MUC_LOG, "demo_thuc_te_log.csv")

t_gay_nghen = {"t": None}


def doi_enter():
    input()
    t_gay_nghen["t"] = time.time()
    print(">>> [GHI NHAN] Thoi diem ban bam Enter (bat dau gay nghen): "
          + datetime.now().strftime("%H:%M:%S.%f")[:-3])


def ping_trung_binh(ip):
    """Ping that bang lenh ping cua Windows, tra ve latency trung binh (ms)."""
    lenh = ["ping", "-n", str(SO_GOI_PING), "-w", str(TIMEOUT_MS), ip]
    kq = subprocess.run(lenh, capture_output=True, text=True, errors="ignore")
    cac_gia_tri = []
    for dong in kq.stdout.splitlines():
        if "TTL" in dong.upper():           # chi lay dong tra loi thanh cong
            m = re.search(r"[=<]\s*(\d+)\s*ms", dong)
            if m:
                cac_gia_tri.append(float(m.group(1)))
    if not cac_gia_tri:
        return float(TIMEOUT_MS)            # mat het goi: coi nhu qua han
    return sum(cac_gia_tri) / len(cac_gia_tri)


def do_4_pop(ip_pop):
    with ThreadPoolExecutor(max_workers=4) as ex:
        tuong_lai = {p: ex.submit(ping_trung_binh, ip_pop[p]) for p in POPS}
        return {p: round(f.result(), 1) for p, f in tuong_lai.items()}


def main():
    df = pd.read_csv(FILE_PIVOT)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    bo = BoDinhTuyen(df)

    # nguong 3 sigma va throughput trung vi cua tung PoP (giong cach mo phong da dung)
    nguong = {p: df[f"latency_ms_{p}"].mean() + 3 * df[f"latency_ms_{p}"].std() for p in POPS}
    thr_trung_vi = {p: df[f"throughput_mbps_{p}"].median() for p in POPS}

    ip_pop = {p: socket.gethostbyname(HOSTS[p]) for p in POPS}
    print("=" * 70)
    print(f"May do: vung={VUNG}, isp={ISP}")
    print("IP tung PoP (giu co dinh suot phien demo):")
    for p in POPS:
        print(f"  {p:18s} {ip_pop[p]:16s} nguong bat thuong = {nguong[p]:.0f} ms")
    print("=" * 70)

    now = datetime.now()
    pop_dang_dung = bo.chon_pop_ban_dau(VUNG, ISP, now.hour, now.weekday())
    print(f"Tang 1 chon PoP ban dau: {pop_dang_dung}")
    print(f"=> Filter Clumsy: icmp and ip.DstAddr == {ip_pop[pop_dang_dung]}")
    print("Khi da bat Clumsy (bam Start), quay lai cua so nay va bam ENTER de ghi moc thoi gian.\n")

    threading.Thread(target=doi_enter, daemon=True).start()

    dong_log = []
    for chu_ky in range(1, SO_CHU_KY_TOI_DA + 1):
        now = datetime.now()
        lat = do_4_pop(ip_pop)
        dong = {
            "timestamp": now, "vung_dia_ly": VUNG, "isp": ISP,
            "gio": now.hour, "thu_trong_tuan": now.weekday(),
        }
        for p in POPS:
            dong[f"latency_ms_{p}"] = lat[p]
            dong[f"throughput_mbps_{p}"] = thr_trung_vi[p]
            dong[f"latency_bat_thuong_{p}"] = int(lat[p] > nguong[p])
        dong = pd.Series(dong)

        t0 = time.perf_counter()
        pop_moi, su_kien = bo.xu_ly_1_buoc(dong, pop_dang_dung)
        xu_ly_ms = (time.perf_counter() - t0) * 1000
        t_quyet_dinh = time.time()

        tt = now.strftime("%H:%M:%S")
        chuoi_lat = "  ".join(f"{p[:8]}={lat[p]:>6.0f}" for p in POPS)
        print(f"[{tt}] chu ky {chu_ky:>2} | dang dung: {pop_dang_dung:16s} | {chuoi_lat}")

        ban_ghi = {"thoi_diem": now.isoformat(timespec="milliseconds"),
                   "pop_dang_dung": pop_dang_dung, **{f"lat_{p}": lat[p] for p in POPS},
                   "bat_thuong": su_kien is not None, "pop_moi": pop_moi if su_kien else "",
                   "xu_ly_thuat_toan_ms": round(xu_ly_ms, 2), "phan_ung_dau_cuoi_s": ""}

        if su_kien is not None:
            print("\n" + "!" * 70)
            print(f"  PHAT HIEN BAT THUONG tai {pop_dang_dung}: {su_kien['latency_luc_phat_hien']} ms "
                  f"(nguong {nguong[pop_dang_dung]:.0f} ms)")
            print(f"  Tang 1 chon PoP thay the: {pop_moi} "
                  f"({su_kien['latency_pop_moi_cung_thoi_diem']} ms), tot hon = {su_kien['co_lua_chon_tot_hon']}")
            print(f"  Thoi gian xu ly thuat toan: {xu_ly_ms:.2f} ms")
            if t_gay_nghen["t"] is not None:
                phan_ung = t_quyet_dinh - t_gay_nghen["t"]
                ban_ghi["phan_ung_dau_cuoi_s"] = round(phan_ung, 2)
                print(f"  Phan ung dau-cuoi (tu luc bam Enter den luc quyet dinh chuyen): {phan_ung:.2f} s")
            print("!" * 70 + "\n")
            pop_dang_dung = pop_moi
            print(f"=> Dang dung: {pop_dang_dung} | tat Clumsy de ket thuc demo, roi Ctrl+C\n")

        dong_log.append(ban_ghi)
        pd.DataFrame(dong_log).to_csv(FILE_LOG, index=False, encoding="utf-8-sig")
        time.sleep(CHU_KY_GIAY)

    print(f"Da luu log: {FILE_LOG}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\nDung demo. Log da luu tai: {FILE_LOG}")
