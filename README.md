# 📡 CDN PoP Routing AI

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Status](https://img.shields.io/badge/status-in%20progress-yellow.svg)
![Project](https://img.shields.io/badge/project-academic-purple.svg)
![License](https://img.shields.io/badge/license-academic-lightgrey.svg)

Đồ án cuối kỳ môn **Dịch vụ mạng Internet** - xây dựng hệ thống thu thập dữ liệu mạng và nghiên cứu mô hình **AI/ML định tuyến động**, nhằm lựa chọn **CDN Point of Presence (PoP)** phù hợp dựa trên khu vực địa lý, ISP, thời gian và điều kiện mạng.

---

## 🎯 Mục tiêu

Hệ thống hướng tới việc:

* 📊 Thu thập **latency** và **throughput** từ nhiều PoP.
* 🌐 So sánh chất lượng kết nối theo **khu vực và ISP**.
* ⏱️ Theo dõi sự thay đổi hiệu năng theo thời gian.
* 🤖 Sử dụng dữ liệu để xây dựng mô hình **AI/ML lựa chọn PoP**.
* 🚨 Phát hiện tình trạng suy giảm/bất thường của PoP.
* 🔄 Mô phỏng cơ chế **chuyển đổi sang PoP phù hợp hơn**.

### 🔄 Pipeline

```text
Network Measurement
        ↓
   Data Collection
        ↓
 Data Processing
        ↓
 Data Analysis
        ↓
   AI / ML Model
        ↓
   PoP Selection
        ↓
 PoP Switching
```

---

## 🏗️ Kiến trúc

```text
┌──────────────┐
│    User      │
└──────┬───────┘
       ↓
┌──────────────┐
│   Collector  │
└──────┬───────┘
       ↓
┌────────────────────────┐
│ Latency + Throughput   │
└───────────┬────────────┘
            ↓
┌────────────────────────┐
│      CSV Dataset       │
└───────────┬────────────┘
            ↓
┌────────────────────────┐
│ Data Processing /      │
│ Analysis               │
└───────────┬────────────┘
            ↓
┌────────────────────────┐
│       AI / ML           │
└───────────┬────────────┘
            ↓
┌────────────────────────┐
│     PoP Selection       │
└────────────────────────┘
```

---

## 📁 Cấu trúc thư mục

```text
cdn-pop-routing-ai/
│
├── analysis/                  # Phân tích và trực quan hóa dữ liệu
├── data/                     # CSV dữ liệu thu thập
├── logs/                     # Log lỗi
├── model/                    # Thành phần mô hình AI/ML
├── scripts/
│   └── merge_data.py         # Gộp dữ liệu của cả nhóm
├── src/
│   └── collector/
│       ├── latency.py        # Đo latency
│       ├── throughput.py     # Đo throughput
│       └── storage.py        # Lưu dữ liệu và log
│
├── web_data/                 # Dữ liệu phục vụ mô phỏng/web
├── config.py                 # Cấu hình cá nhân
├── run_collector.py          # Chạy collector
├── Mo_phong_chuyen_doi_POP.html
└── README.md
```
---

## ⚙️ Cài đặt

### Yêu cầu

* 🐍 Python **3.8+**
* 🔗 `curl`
* 💻 Windows / Linux / macOS

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

Mỗi bản ghi gồm các thông tin chính:

| Trường            | Ý nghĩa           |
| ----------------- | ----------------- |
| `timestamp`       | Thời điểm đo      |
| `vung_dia_ly`     | Khu vực           |
| `isp`             | Nhà mạng          |
| `pop_id`          | PoP được đo       |
| `latency_ms`      | Độ trễ            |
| `throughput_mbps` | Tốc độ truyền tải |

```

---

## 🔗 Gộp dữ liệu cả nhóm

Sau khi các thành viên hoàn thành việc thu thập, đặt các file CSV vào:

```text
data/
```

Sau đó chạy:

```bash
python scripts/merge_data.py
```

Script sẽ:

* 🔍 Kiểm tra cấu trúc dữ liệu.
* 🧹 Chuẩn hóa khu vực, ISP và PoP.
* 🔗 Gộp dữ liệu của các thành viên.
* 🗑️ Loại bỏ bản ghi trùng hoàn toàn.
* 📈 Thống kê dữ liệu sau khi gộp.

Dataset tổng hợp:

```text
data/data_tong_hop.csv
```

---

## 🤖 AI / ML

Dữ liệu sau khi thu thập và xử lý sẽ được sử dụng để nghiên cứu bài toán:

> **Với điều kiện mạng hiện tại, PoP nào phù hợp nhất?**

Các feature có thể bao gồm:

```text
Region
ISP
Time
Latency
Throughput
Historical Network Metrics
```

Mô hình AI/ML hướng tới:

```text
Network Conditions
        ↓
     ML Model
        ↓
 Predicted PoP
        ↓
 Routing Decision
```

Ngoài lựa chọn PoP, project cũng hướng tới **anomaly detection** để phát hiện khi chất lượng của PoP hiện tại suy giảm.

---

## 🔄 Mô phỏng chuyển đổi PoP

File:

```text
Mo_phong_chuyen_doi_POP.html
```

được sử dụng để mô phỏng quá trình:

```text
Current PoP
     ↓
Monitor
     ↓
Detect Degradation
     ↓
Evaluate Other PoPs
     ↓
Select Candidate
     ↓
Switch PoP
```

Mục đích là minh họa cơ chế **dynamic PoP routing** của hệ thống.

---

## 📈 Các chỉ số đánh giá

Hệ thống có thể được đánh giá dựa trên:

### Network Performance

* ⚡ Latency
* 🚀 Throughput
* 📉 Latency variation
* 📊 Throughput variation

### Routing Performance

* 🎯 PoP selection accuracy
* ⚡ Average latency sau routing
* 🚀 Average throughput sau routing
* 🔄 Số lần chuyển PoP
* ⏱️ Thời gian phục hồi khi PoP suy giảm

---

## 📌 Trạng thái dự án

| Thành phần               |     Status     |
| ------------------------ | :------------: |
| PoP Configuration        |     🟢 Done    |
| Latency Collector        |     🟢 Done    |
| Throughput Collector     |     🟢 Done    |
| CSV Storage              |     🟢 Done    |
| Error Logging            |     🟢 Done    |
| Continuous Collection    |     🟢 Done    |
| Data Merge               |     🟢 Done    |
| Data Normalization       |     🟢 Done    |
| Data Analysis            | 🟡 In Progress |
| Feature Engineering      | 🟡 In Progress |
| AI / ML Model            | 🟡 In Progress |
| Anomaly Detection        | 🟡 In Progress |
| Dynamic Routing          | 🟡 In Progress |
| PoP Switching Simulation |  🟢 Available  |

---

## 🛣️ Roadmap

```text
✅ Network Data Collection
        ↓
✅ Data Aggregation
        ↓
🔄 Exploratory Data Analysis
        ↓
🔄 Feature Engineering
        ↓
🔄 AI / ML Model
        ↓
🔄 Anomaly Detection
        ↓
🔄 Dynamic PoP Selection
        ↓
🔄 Routing Simulation & Evaluation
```

---

## 🎓 Academic Project

**Course:** Dịch vụ mạng Internet
**Project:** CDN PoP Routing AI
**Scope:** CDN · Network Measurement · Data Analysis · AI/ML
**Target:** Vietnam

> 📚 Project được phát triển phục vụ mục đích **học tập và nghiên cứu**.
