# 📡 CDN PoP Routing AI

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Status](https://img.shields.io/badge/status-in%20progress-yellow.svg)
![License](https://img.shields.io/badge/license-academic-lightgrey.svg)

Đồ án cuối kỳ môn Dịch vụ mạng Internet — xây dựng mô hình AI/ML định tuyến động
chọn PoP CDN tối ưu theo vùng địa lý, khung giờ và điều kiện hạ tầng mạng tại Việt Nam.

## 📁 Cấu trúc thư mục

- `config.py` — cấu hình, **mỗi thành viên sửa file này** trước khi chạy
- `run_collector.py` — file chạy chính để thu thập dữ liệu
- `src/collector/` — logic đo latency, throughput, ghi dữ liệu
- `scripts/merge_data.py` — gộp dữ liệu CSV của cả nhóm
- `data/` — dữ liệu CSV thu thập được (không đẩy lên Git)
- `logs/` — log lỗi trong quá trình thu thập (không đẩy lên Git)

## ⚙️ Cài đặt

Yêu cầu: Python 3.8+, đã cài `curl`.

```bash
git clone https://github.com/haorcine/cdn-pop-routing-ai.git
cd cdn-pop-routing-ai
```

## 🔧 Trước khi chạy — bắt buộc

Mở `config.py`, sửa đúng 3 dòng theo thực tế của bạn:

```python
VUNG_DIA_LY = "Nam"      # "Bac", "Trung", hoac "Nam"
ISP = "VNPT"               # ISP THAT dang dung
TEN_THANH_VIEN = "Hao"     # Ten cua ban
```

**Không sửa** phần `POPS` trong `config.py` — danh sách này cần giống nhau cho cả nhóm.

## 🚀 Chạy thu thập dữ liệu

```bash
python run_collector.py
```

Để nguyên terminal chạy liên tục, không tắt máy. Dừng bằng `Ctrl+C`.

## 🔗 Gộp dữ liệu cả nhóm

Sau khi có đủ file CSV của các thành viên trong thư mục `data/`:

```bash
python scripts/merge_data.py
```
