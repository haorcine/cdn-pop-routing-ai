import os
import pandas as pd
import matplotlib.pyplot as plt

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

radar = pd.read_csv(os.path.join(GOC, "data", "radar_latency_vn.csv"), parse_dates=["thoi_diem"])
minh = pd.read_csv(os.path.join(GOC, "data", "data_pivot.csv"), parse_dates=["timestamp"])

pops = ["cloudflare", "vultr_singapore", "vultr_seoul", "linode_singapore"]
minh["latency_tb"] = minh[[f"latency_ms_{p}" for p in pops]].mean(axis=1)
minh["gio_lam_tron"] = minh["timestamp"].dt.floor("h")
minh_theo_gio = minh.groupby("gio_lam_tron")["latency_tb"].mean().reset_index()

fig, ax1 = plt.subplots(figsize=(10, 4.5))
ax1.plot(radar["thoi_diem"], radar["latency_p50_ms"], color="tab:blue", label="Radar VN (p50)")
ax1.set_ylabel("Latency Radar (ms)", color="tab:blue")
ax1.set_xlabel("Thời gian")

ax2 = ax1.twinx()
ax2.plot(minh_theo_gio["gio_lam_tron"], minh_theo_gio["latency_tb"], color="tab:orange", label="Dữ liệu tự đo")
ax2.set_ylabel("Latency tự đo, TB 4 PoP (ms)", color="tab:orange")

fig.suptitle("Đối chiếu xu hướng latency: Cloudflare Radar (VN) và dữ liệu tự đo")
fig.tight_layout()
plt.savefig(os.path.join(GOC, "analysis", "hinh_anh", "hinh_4_5_doi_chieu_radar.png"), dpi=200)
print("Da luu hinh 4.5")