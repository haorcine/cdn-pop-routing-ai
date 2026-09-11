"""Module do throughput (curl) - ho tro Windows va Linux/Mac."""

import platform
import subprocess

HE_DIEU_HANH = platform.system()
NULL_DEVICE = "NUL" if HE_DIEU_HANH == "Windows" else "/dev/null"


def do_throughput(url, ghi_log_loi=None):
    try:
        ket_qua = subprocess.run(
            ["curl", "-o", NULL_DEVICE, "-s", "--max-time", "15",
             "-w", "%{speed_download}", url],
            capture_output=True, text=True, timeout=20,
        )
        toc_do_byte_per_giay = float(ket_qua.stdout.strip())
        if toc_do_byte_per_giay <= 0:
            return None
        return round((toc_do_byte_per_giay * 8) / 1_000_000, 2)

    except subprocess.TimeoutExpired:
        if ghi_log_loi:
            ghi_log_loi(f"CURL TIMEOUT toi {url}")
        return None
    except Exception as loi:
        if ghi_log_loi:
            ghi_log_loi(f"CURL LOI toi {url}: {loi}")
        return None