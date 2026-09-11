"""Module ghi du lieu CSV va log loi."""

import csv
import os
from datetime import datetime

CSV_HEADER = ["timestamp", "vung_dia_ly", "isp", "pop_id", "latency_ms", "throughput_mbps"]


def duong_dan_file_csv(thu_muc_data, ten_thanh_vien, vung_dia_ly, isp):
    os.makedirs(thu_muc_data, exist_ok=True)
    ten_file = f"data_{ten_thanh_vien}_{vung_dia_ly}_{isp}.csv"
    return os.path.join(thu_muc_data, ten_file)


def duong_dan_file_log(thu_muc_logs, ten_thanh_vien):
    os.makedirs(thu_muc_logs, exist_ok=True)
    ten_file = f"log_loi_{ten_thanh_vien}.txt"
    return os.path.join(thu_muc_logs, ten_file)


def dam_bao_co_header(duong_dan_csv):
    if not os.path.exists(duong_dan_csv):
        with open(duong_dan_csv, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(CSV_HEADER)


def ghi_du_lieu(duong_dan_csv, danh_sach_dong):
    with open(duong_dan_csv, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(danh_sach_dong)


def tao_ham_ghi_log(duong_dan_log):
    def ghi_log_loi(noi_dung):
        with open(duong_dan_log, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().isoformat(timespec='seconds')} | {noi_dung}\n")
    return ghi_log_loi