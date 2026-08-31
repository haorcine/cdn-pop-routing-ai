import subprocess

def do_latency(dia_chi_ip, so_lan_ping=4):
    ket_qua = subprocess.run(
        ["ping", "-n", str(so_lan_ping), dia_chi_ip],
        capture_output=True,
        text=True
    )
    output = ket_qua.stdout

    vi_tri_bat_dau = output.find("Average = ")
    if vi_tri_bat_dau == -1:
        return None  # không tìm thấy -> có thể ping lỗi/timeout

    vi_tri_sau_cum = vi_tri_bat_dau + len("Average = ")
    vi_tri_ms = output.find("ms", vi_tri_sau_cum)
    chuoi_so = output[vi_tri_sau_cum:vi_tri_ms]

    try:
        return float(chuoi_so)
    except ValueError:
        return None


# Thử gọi hàm với nhiều PoP khác nhau
print("Cloudflare:", do_latency("1.1.1.1"))
print("Google:", do_latency("8.8.8.8"))