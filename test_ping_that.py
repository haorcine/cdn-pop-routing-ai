import subprocess

# Chạy lệnh: ping -n 4 1.1.1.1  (giống hệt lệnh bạn gõ tay ở Bước 1)
ket_qua = subprocess.run(
    ["ping", "-n", "4", "1.1.1.1"],
    capture_output=True,
    text=True
)

output = ket_qua.stdout
print("----- OUTPUT THAT TU LENH PING -----")
print(output)
print("-------------------------------------")

# Áp dụng lại đúng logic 4 bước đã làm ở Bước 3
vi_tri_bat_dau = output.find("Average = ")
vi_tri_sau_cum = vi_tri_bat_dau + len("Average = ")
vi_tri_ms = output.find("ms", vi_tri_sau_cum)
chuoi_so = output[vi_tri_sau_cum:vi_tri_ms]
latency = float(chuoi_so)

print("Latency đo được thực tế:", latency, "ms")