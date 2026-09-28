import matplotlib.pyplot as plt
import numpy as np

ten = ["Baseline\nkhoảng cách", "Baseline\ntrung bình", "Decision\nTree", "Random\nForest"]
tb = [128.2, 70.6, 64.7, 61.7]
tv = [56.0, 56.0, 49.0, 49.0]

x = np.arange(len(ten)); w = 0.38
fig, ax = plt.subplots(figsize=(8, 4.5))
b1 = ax.bar(x - w/2, tb, w, label="Trung bình")
b2 = ax.bar(x + w/2, tv, w, label="Trung vị")
ax.bar_label(b1, fmt="%.1f"); ax.bar_label(b2, fmt="%.1f")
ax.set_xticks(x); ax.set_xticklabels(ten)
ax.set_ylabel("Latency (ms)")
ax.set_title("Latency của PoP được chọn trên tập kiểm tra (259 dòng)")
ax.legend()
plt.tight_layout()
plt.savefig("analysis/hinh_anh/hinh_6_1_so_sanh_latency.png", dpi=200)