"""
SCRIPT THU THAP DU LIEU LATENCY & THROUGHPUT
Chay: python collector.py
Dung: Ctrl+C
"""

import csv
import os
import subprocess
import time
from datetime import datetime

# ===== CHINH 2 DONG NAY THEO DUNG VI TRI/MANG CUA BAN =====
VUNG_DIA_LY = "Nam"      
ISP = "VNPT"             
TEN_THANH_VIEN = "Hao"  # Đổi thành tên bạn thật để phân biệt file khi gộp
# ============================================================

POPS = {
    "cloudflare": {
        "ip": "1.1.1.1",
        "url": "https://speed.cloudflare.com/__down?bytes=2000000",
    },
    "vultr_singapore": {
        "ip": "sgp-ping.vultr.com",
        "url": "http://sgp-ping.vultr.com/vultr.com.100MB.bin",
    },
    "vultr_seoul": {
        "ip": "sel-kor-ping.vultr.com",
        "url": "http://sel-kor-ping.vultr.com/vultr.com.100MB.bin",
    },
    "linode_singapore": {
        "ip": "speedtest.singapore.linode.com",
        "url": "http://speedtest.singapore.linode.com/100MB-singapore.bin",
    },
}

FILE_CSV = f"data_{VUNG_DIA_LY}_{ISP}.csv"
CHU_KY_GIAY = 15  # dang de 15 giay de test nhanh, sau nay doi thanh 1800 (30 phut)


def do_latency(dia_chi_ip, so_lan_ping=4):
    ket_qua = subprocess.run(
        ["ping", "-n", str(so_lan_ping), dia_chi_ip],
        capture_output=True,
        text=True
    )
    output = ket_qua.stdout

    vi_tri_bat_dau = output.find("Average = ")
    if vi_tri_bat_dau == -1:
        return None

    vi_tri_sau_cum = vi_tri_bat_dau + len("Average = ")
    vi_tri_ms = output.find("ms", vi_tri_sau_cum)
    chuoi_so = output[vi_tri_sau_cum:vi_tri_ms]

    try:
        return float(chuoi_so)
    except ValueError:
        return None


def do_throughput(url):
    ket_qua = subprocess.run(
        [
            "curl", "-o", "NUL", "-s", "--max-time", "15",
            "-w", "%{speed_download}",
            url
        ],
        capture_output=True,
        text=True
    )
    try:
        toc_do_byte_per_giay = float(ket_qua.stdout.strip())
        if toc_do_byte_per_giay <= 0:
            return None
        throughput_mbps = (toc_do_byte_per_giay * 8) / 1_000_000
        return round(throughput_mbps, 2)
    except ValueError:
        return None


def dam_bao_co_header():
    if not os.path.exists(FILE_CSV):
        with open(FILE_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "vung_dia_ly", "isp", "pop_id", "latency_ms", "throughput_mbps"])


def thu_thap_va_ghi():
    timestamp = datetime.now().isoformat(timespec="seconds")
    dong_moi = []

    for pop_id, thong_tin in POPS.items():
        print(f"  Dang do {pop_id} ...")
        latency = do_latency(thong_tin["ip"])
        throughput = do_throughput(thong_tin["url"])
        print(f"    latency={latency} ms | throughput={throughput} Mbps")
        dong_moi.append([timestamp, VUNG_DIA_LY, ISP, pop_id, latency, throughput])

    with open(FILE_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(dong_moi)

    print(f"  Da ghi {len(dong_moi)} dong vao {FILE_CSV}")


if __name__ == "__main__":
    dam_bao_co_header()
    print(f"Bat dau thu thap. File luu: {FILE_CSV}. Nhan Ctrl+C de dung.\n")

    lan = 0
    try:
        while True:
            lan += 1
            print(f"[Lan {lan}] {datetime.now().isoformat(timespec='seconds')}")
            thu_thap_va_ghi()
            print(f"Cho {CHU_KY_GIAY} giay den lan sau...\n")
            time.sleep(CHU_KY_GIAY)
    except KeyboardInterrupt:
        print(f"\nDa dung sau {lan} lan. Du lieu luu tai: {FILE_CSV}")