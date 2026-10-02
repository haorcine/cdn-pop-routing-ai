# 📡 CDN PoP Routing AI

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Status](https://img.shields.io/badge/status-in%20progress-yellow.svg)
![Project](https://img.shields.io/badge/project-academic-purple.svg)
![License](https://img.shields.io/badge/license-academic-lightgrey.svg)

Đồ án cuối kỳ môn **Dịch vụ mạng Internet** - xây dựng hệ thống đo lường hạ tầng mạng và mô hình **AI/ML định tuyến động** để tự động chọn **CDN Point of Presence (PoP)** tối ưu theo vùng địa lý, ISP, khung giờ, đồng thời **tự phát hiện và tự chuyển đổi** khi một PoP suy giảm hiệu năng (mô phỏng bối cảnh đứt cáp quang biển tại Việt Nam).

---

## 🎯 Mục tiêu

* 📊 Thu thập **latency** và **throughput** thật tới 4 PoP đại diện (Cloudflare, Vultr Singapore, Vultr Seoul, Linode Singapore), theo 3 vùng địa lý và 3 ISP (Bắc–FPT, Trung–Viettel, Nam–VNPT).
* 🧠 Xây dựng mô hình phân loại (**Tầng 1**) dự đoán PoP tối ưu theo ngữ cảnh vùng/ISP/giờ/thứ.
* 🚨 Xây dựng cơ chế giám sát nền (**Tầng 2**) phát hiện bất thường và tự động chuyển PoP, không cần can thiệp thủ công.
* ⚖️ So sánh định lượng với 2 Baseline định tuyến tĩnh (kiểu GeoDNS, và theo latency trung bình lịch sử).
* 🧪 Mô phỏng 2 dạng sự cố (ngắn hạn và kéo dài) và chạy demo thật bằng công cụ giả lập độ trễ mạng.
* 🗺️ Trực quan hóa toàn bộ quy trình và kết quả bằng các trang web tương tác.

---

## 🏗️ Kiến trúc 2 tầng

```text
┌───────────────────────────────────────────────┐
│  Dữ liệu đo: latency + throughput             │
│  theo vùng, ISP, khung giờ, thứ trong tuần    │
└───────────────────────┬───────────────────────┘
                        ↓
┌───────────────────────────────────────────────┐
│  TẦNG 1 — Mô hình phân loại chọn PoP          │
│  Decision Tree / Random Forest                │
│  (chọn PoP ban đầu + xếp hạng ứng viên)       │
└───────────────────────┬───────────────────────┘
                        ↓
┌───────────────────────────────────────────────┐
│  TẦNG 2 — Giám sát nền & tự chuyển đổi        │
│  Isolation Forest (riêng từng PoP)            │
│       AND  ngưỡng thống kê (TB + 3σ)          │
│  → trigger gọi lại Tầng 1 khi cả 2 đồng thuận │
└───────────────────────┬───────────────────────┘
                        ↓
┌───────────────────────────────────────────────┐
│         PoP đang dùng (tự cập nhật)           │
└───────────────────────────────────────────────┘
```

---

## 📁 Cấu trúc thư mục

```text
cdn-pop-routing-ai/
│
├── analysis/
│   └── hinh_anh/              # Biểu đồ EDA (latency/throughput theo PoP, giờ, vùng-ISP, tương quan)
├── data/
│   ├── data_tong_hop.csv      # Dữ liệu gộp từ cả nhóm (dạng dài)
│   ├── data_sach.csv          # Dữ liệu đã làm sạch
│   └── data_pivot.csv         # Dữ liệu pivot (1 dòng = 1 thời điểm, đủ 4 PoP) dùng để train
├── logs/                      # Log lỗi thu thập + log các lần chạy demo thật
├── model/
│   ├── train_tier1.py         # Huấn luyện Decision Tree / Random Forest (Tầng 1)
│   ├── dinh_tuyen.py          # BoDinhTuyen: bộ điều khiển trung tâm 2 tầng
│   ├── tier2_anomaly.py       # Isolation Forest + ngưỡng thống kê (Tầng 2)
│   ├── baseline.py            # 2 baseline định tuyến tĩnh để đối chiếu
│   ├── so_sanh_baseline.py    # So sánh latency AI vs baseline trên tập kiểm tra
│   ├── mo_phong_su_co_ngan_han.py   # Kịch bản sự cố ngắn hạn (trích hình dạng thật)
│   ├── mo_phong_su_co_keo_dai.py    # Kịch bản sự cố kéo dài (dựng có căn cứ)
│   ├── tong_hop_ket_qua.py    # Tổng hợp bảng kết quả cuối cùng (Chương VI)
│   ├── demo_thuc_te.py        # Demo thật: ping trực tiếp + Clumsy giả lập nghẽn mạng
│   └── xuat_du_lieu_trang.py  # Xuất JSON/JS cho các trang trực quan hóa
├── scripts/
│   ├── clean_data.py          # Làm sạch, xử lý thiếu/outlier, tính ngưỡng bất thường
│   ├── merge_data.py          # Gộp dữ liệu CSV của cả nhóm
│   ├── pivot_data.py          # Pivot dữ liệu dạng dài sang dạng rộng + gán nhãn pop_toi_uu
│   └── eda.py                 # Vẽ biểu đồ phân tích khám phá dữ liệu
├── src/
│   └── collector/
│       ├── latency.py         # Đo latency (ping)
│       ├── throughput.py      # Đo throughput (curl)
│       └── storage.py         # Lưu dữ liệu và log
├── web_data/
│   ├── du_lieu_that.json, su_co_ngan_han.json, su_co_keo_dai.json  # Dữ liệu cho trang mô phỏng động
│   └── report/
│       ├── report.html        # Trang báo cáo tổng hợp (đọc report-data.js, mở offline)
│       └── report-data.js     # Số liệu Chương IV–VI, do script Python xuất ra
├── Mo_phong_chuyen_doi_POP.html   # Trang mô phỏng động: bản đồ khu vực, phát lại + demo trực tiếp
├── config.py                  # Cấu hình cá nhân (vùng, ISP của từng thành viên)
├── run_collector.py           # Chạy collector thu thập liên tục
└── README.md
```

---

## ⚙️ Cài đặt

### Yêu cầu

* 🐍 Python **3.8+**
* 🔗 `curl`
* 💻 Windows / Linux / macOS
* (Tùy chọn, để chạy demo thật) [Clumsy](https://jagt.github.io/clumsy/) - công cụ giả lập độ trễ mạng trên Windows

Clone repository:

```bash
git clone https://github.com/haorcine/cdn-pop-routing-ai.git
cd cdn-pop-routing-ai
```

Kiểm tra môi trường:

```bash
python --version
curl --version
```

---

## 📊 Dữ liệu thu thập

Mỗi bản ghi gồm các trường chính:

| Trường              | Ý nghĩa                           |
| ------------------- | ----------------------------------|
| `timestamp`         | Thời điểm đo                      |
| `vung_dia_ly`       | Khu vực (Bắc/Trung/Nam)           |
| `isp`               | Nhà mạng (FPT/Viettel/VNPT)       |
| `pop_id`            | PoP được đo (4 PoP)               |
| `latency_ms`        | Độ trễ (ping)                     |
| `throughput_mbps`   | Tốc độ truyền tải (curl)          |

Sau khi gộp (`merge_data.py`), làm sạch (`clean_data.py`) và pivot (`pivot_data.py`), dữ liệu đã đạt **5180 dòng đo thô → 1294 bản ghi pivot**, mỗi dòng gồm latency/throughput của cả 4 PoP tại cùng thời điểm, kèm nhãn `pop_toi_uu` (PoP có latency thấp nhất).

---

## 🤖 Tầng 1 - Mô hình phân loại chọn PoP

Huấn luyện trên 4 đặc trưng ngữ cảnh (vùng, ISP, giờ, thứ trong tuần), nhãn là `pop_toi_uu`:

| Mô hình | Accuracy | Macro F1 | Weighted F1 |
| --- | --- | --- | --- |
| Decision Tree (`max_depth=5`) | 75,7% | 0,62 | 0,76 |
| Random Forest (`n_estimators=100`) | 75,3% | 0,63 | 0,75 |

Random Forest được chọn triển khai trong `BoDinhTuyen` (bộ điều khiển sản xuất) nhờ Macro F1 cao hơn và latency thực tế thấp hơn khi dự đoán, dù accuracy nhỉnh hơn thuộc về Decision Tree.

---

## 🚨 Tầng 2 - Phát hiện bất thường & tự chuyển đổi

* **Isolation Forest** huấn luyện riêng cho từng PoP trên latency + throughput lịch sử của chính nó.
* **Ngưỡng thống kê** (trung bình + 3 lần độ lệch chuẩn) tính sẵn ở bước làm sạch dữ liệu.
* Chỉ kích hoạt chuyển đổi khi **cả hai tín hiệu cùng đồng thuận** bất thường.
* Khi chuyển đổi: chỉ chấp nhận PoP thay thế có latency thấp hơn PoP đang lỗi tại thời điểm đó, ưu tiên theo thứ hạng của Tầng 1; nếu không có ứng viên nào tốt hơn, chọn PoP có latency thấp nhất hiện tại làm phương án tạm thời và đánh dấu rõ trong log.

**Kết quả kiểm chứng (12 kịch bản mô phỏng):**

| Chỉ số | Kết quả |
| --- | --- |
| Tỷ lệ phát hiện đúng PoP lỗi | 100% (12/12) |
| Số chu kỳ chờ để phát hiện | 0 chu kỳ |
| Thời gian xử lý thuật toán | ~8–27 ms |
| Cải thiện latency, sự cố ngắn hạn (sau chuyển đổi) | +4,7% / +0,5% so với 2 baseline |
| Cải thiện latency, sự cố kéo dài (sau chuyển đổi) | +92,5% / +87,7% so với 2 baseline |

> Luận điểm chính: giá trị của Tầng 2 **tỷ lệ thuận với độ dài sự cố** - baseline tĩnh không có cơ chế phản ứng nên chịu thiệt hại kéo dài suốt thời gian sự cố, trong khi hệ thống AI chuyển PoP ngay khi phát hiện.

---

## ⚖️ Baseline đối chiếu

| Baseline | Cách chọn | Latency TB (tập test) |
| --- | --- | --- |
| Khoảng cách (GeoDNS) | Luôn cố định `vultr_singapore` | 128,2 ms |
| Latency trung bình lịch sử | Luôn cố định `linode_singapore` | 70,6 ms |

---

## 🧪 Mô phỏng sự cố & Demo thật

* `mo_phong_su_co_ngan_han.py`: trích hình dạng từ một đợt sự cố thật, áp lên PoP được chọn làm nạn nhân (cú sốc thoáng qua).
* `mo_phong_su_co_keo_dai.py`: dựng dựa trên độ cao đỉnh sự cố thật, giữ trạng thái suy giảm trong nhiều lượt đo liên tiếp (mô phỏng đứt cáp biển).
* `demo_thuc_te.py`: chạy **thật** trên `BoDinhTuyen`, ping trực tiếp tới 4 PoP, kết hợp [Clumsy](https://jagt.github.io/clumsy/) để làm nghẽn mạng thật và quan sát hệ thống tự phát hiện, tự chuyển đổi theo thời gian thực.

---

## 🔄 Trực quan hóa

* **`Mo_phong_chuyen_doi_POP.html`** - bản đồ khu vực (Việt Nam, Singapore, Hàn Quốc, Hồng Kông), hiển thị trực quan quá trình chuyển đổi PoP: phát lại dữ liệu thật/kịch bản mô phỏng, hoặc tự bấm gây sự cố để xem hệ thống phản ứng ngay trên giao diện.
* **`web_data/report/report.html`** - trang báo cáo tổng hợp (EDA, kết quả Tầng 1/Tầng 2, so sánh baseline), đọc số liệu từ `report-data.js` do pipeline Python xuất ra, mở trực tiếp bằng trình duyệt không cần server.

---

## 📌 Trạng thái dự án

| Thành phần | Status |
| ------------------------ | :------------: |
| Thu thập dữ liệu (Latency/Throughput Collector) | 🟢 Done |
| Gộp & làm sạch dữ liệu (Merge, Clean, Pivot) | 🟢 Done |
| Phân tích khám phá dữ liệu (EDA) | 🟢 Done |
| Xây dựng đặc trưng (Feature Engineering) | 🟢 Done |
| Huấn luyện mô hình Tầng 1 (Decision Tree, Random Forest) | 🟢 Done |
| Tinh chỉnh siêu tham số & Feature importance | 🟡 Chưa làm |
| Cơ chế phát hiện bất thường & tự chuyển đổi (Tầng 2) | 🟢 Done |
| So sánh baseline định tuyến tĩnh | 🟢 Done |
| Mô phỏng sự cố (ngắn hạn & kéo dài) | 🟢 Done |
| Demo thật (ping trực tiếp + giả lập nghẽn mạng) | 🟢 Done |
| Trang trực quan hóa (bản đồ động + báo cáo tĩnh) | 🟢 Done |
| Viết báo cáo (Chương I-II-III-IV-V-VI-VII) | 🟢 Done |

---

## 🎓 Thông tin đồ án

**Môn học:** Dịch vụ mạng Internet
**Tên đề tài:** Xây dựng mô hình AI/ML định tuyến động chọn PoP CDN tối ưu theo vùng địa lý, khung giờ và điều kiện hạ tầng mạng tại Việt Nam
**Phạm vi:** Network Measurement · AI/ML · Anomaly Detection · Data Visualization
**Phạm vi khảo sát:** 3 vùng (Bắc/Trung/Nam) × 3 ISP (FPT/Viettel/VNPT) × 4 PoP (Cloudflare, Vultr Singapore, Vultr Seoul, Linode Singapore)

> 📚 Dự án được phát triển phục vụ mục đích học tập và nghiên cứu.
