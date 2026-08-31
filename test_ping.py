output = """Pinging 1.1.1.1 with 32 bytes of data:
Reply from 1.1.1.1: bytes=32 time=49ms TTL=58
Reply from 1.1.1.1: bytes=32 time=47ms TTL=58
Reply from 1.1.1.1: bytes=32 time=48ms TTL=58
Reply from 1.1.1.1: bytes=32 time=49ms TTL=58
Ping statistics for 1.1.1.1:
    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss),
Approximate round trip times in milli-seconds:
    Minimum = 47ms, Maximum = 49ms, Average = 48ms
"""

# Bước 1: tìm vị trí bắt đầu của cụm "Average = "
vi_tri_bat_dau = output.find("Average = ")
print("Vị trí bắt đầu cụm 'Average = ':", vi_tri_bat_dau)

# Bước 2: tính vị trí ký tự ngay sau cụm đó
vi_tri_sau_cum = vi_tri_bat_dau + len("Average = ")
print("Vị trí bắt đầu của số:", vi_tri_sau_cum)

# Bước 3: tìm vị trí chữ "ms" xuất hiện SAU vị trí đó
vi_tri_ms = output.find("ms", vi_tri_sau_cum)
print("Vị trí chữ 'ms':", vi_tri_ms)

# Bước 4: lấy phần nằm giữa 2 vị trí đó, rồi chuyển sang số
chuoi_so = output[vi_tri_sau_cum:vi_tri_ms]
print("Chuỗi số lấy được:", repr(chuoi_so))

latency = float(chuoi_so)
print("Latency (số thật, dùng để tính toán):", latency)