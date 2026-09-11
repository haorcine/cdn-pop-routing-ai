"""
FILE CHAY CHINH - THU THAP DU LIEU LATENCY & THROUGHPUT
Chay: python run_collector.py
Dung: Ctrl+C
"""

import time
from datetime import datetime

import config
from src.collector.latency import do_latency
from src.collector.throughput import do_throughput
from src.collector.storage import (
    duong_dan_file_csv,
    duong_dan_file_log,
    dam_bao_co_header,
    ghi_du_lieu,
    tao_ham_ghi_log,
)


def thu_thap_mot_luot(ghi_log_loi):
    timestamp = datetime.now().isoformat(timespec="seconds")
    danh_sach_dong = []

    for pop_id, thong_tin in config.POPS.items():
        print(f"  Dang do {pop_id} ...")
        latency = do_latency(thong_tin["ip"], config.SO_LAN_PING_MOI_LUOT, ghi_log_loi)
        throughput = do_throughput(thong_tin["url"], ghi_log_loi)
        print(f"    latency={latency} ms | throughput={throughput} Mbps")
        danh_sach_dong.append([
            timestamp, config.VUNG_DIA_LY, config.ISP, pop_id,
            latency if latency is not None else "",
            throughput if throughput is not None else "",
        ])

    return danh_sach_dong


def chay_lien_tuc():
    duong_dan_csv = duong_dan_file_csv(config.THU_MUC_DATA, config.TEN_THANH_VIEN, config.VUNG_DIA_LY, config.ISP)
    duong_dan_log = duong_dan_file_log(config.THU_MUC_LOGS, config.TEN_THANH_VIEN)
    ghi_log_loi = tao_ham_ghi_log(duong_dan_log)
    dam_bao_co_header(duong_dan_csv)

    print(f"Bat dau thu thap. File: {duong_dan_csv}. Ctrl+C de dung.\n")
    lan = 0
    try:
        while True:
            lan += 1
            print(f"[Lan {lan}] {datetime.now().isoformat(timespec='seconds')}")
            dong = thu_thap_mot_luot(ghi_log_loi)
            ghi_du_lieu(duong_dan_csv, dong)
            print(f"  Da ghi {len(dong)} dong vao {duong_dan_csv}\n")
            time.sleep(config.CHU_KY_GIAY)
    except KeyboardInterrupt:
        print(f"\nDa dung sau {lan} lan. Du lieu: {duong_dan_csv}")


if __name__ == "__main__":
    chay_lien_tuc()