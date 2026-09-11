"""Module do latency (ping) - ho tro Windows va Linux/Mac."""

import platform
import re
import subprocess

HE_DIEU_HANH = platform.system()


def do_latency(dia_chi_ip, so_lan_ping=4, ghi_log_loi=None):
    try:
        if HE_DIEU_HANH == "Windows":
            cmd = ["ping", "-n", str(so_lan_ping), dia_chi_ip]
        else:
            cmd = ["ping", "-c", str(so_lan_ping), dia_chi_ip]

        ket_qua = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        output = ket_qua.stdout

        if HE_DIEU_HANH == "Windows":
            vi_tri_bat_dau = output.find("Average = ")
            if vi_tri_bat_dau == -1:
                return None
            vi_tri_sau_cum = vi_tri_bat_dau + len("Average = ")
            vi_tri_ms = output.find("ms", vi_tri_sau_cum)
            return float(output[vi_tri_sau_cum:vi_tri_ms])
        else:
            match = re.search(r"= [\d.]+/([\d.]+)/", output)
            return float(match.group(1)) if match else None

    except subprocess.TimeoutExpired:
        if ghi_log_loi:
            ghi_log_loi(f"PING TIMEOUT toi {dia_chi_ip}")
        return None
    except Exception as loi:
        if ghi_log_loi:
            ghi_log_loi(f"PING LOI toi {dia_chi_ip}: {loi}")
        return None