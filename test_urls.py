import subprocess

candidates = {
    "Cloudflare (da xac nhan hoat dong)": "https://speed.cloudflare.com/__down?bytes=2000000",
    "Vultr Singapore": "http://sgp-ping.vultr.com/vultr.com.100MB.bin",
    "Vultr Tokyo": "http://hnd-jp-ping.vultr.com/vultr.com.100MB.bin",
    "Vultr Seoul": "http://sel-kor-ping.vultr.com/vultr.com.100MB.bin",
    "Linode Singapore": "http://speedtest.singapore.linode.com/100MB-singapore.bin",
    "Linode Tokyo": "http://speedtest.tokyo2.linode.com/100MB-tokyo2.bin",
}

for ten, url in candidates.items():
    print(f"\n=== Dang kiem tra: {ten} ===")
    print(f"URL: {url}")
    try:
        result = subprocess.run(
            ["curl", "-s", "-o", "NUL", "-w", "HTTP_CODE:%{http_code} SIZE:%{size_download} TIME:%{time_total}",
             "--max-time", "15", url],
            capture_output=True, text=True, timeout=20
        )
        print("Ket qua:", result.stdout)
        if result.stderr:
            print("Loi (neu co):", result.stderr.strip())
    except Exception as e:
        print("LOI KHONG CHAY DUOC:", e)