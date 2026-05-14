# 🏦 Phân Tích Dữ Liệu Mặc Định Thanh Toán Thẻ Tín Dụng

## 📝 Mô Tả Dự Án

Ứng dụng Streamlit toàn diện để phân tích dữ liệu tín dụng, bao gồm:
- **Tổng Quan:** Thống kê cơ bản về khách hàng
- **Phân Tích Dữ Liệu:** Biểu đồ và phân tích thống kê chi tiết
- **Mô Hình Máy Học:** So sánh Logistic Regression và Random Forest
- **Báo Cáo:** Báo cáo chi tiết và có thể tải xuống

## 🚀 Cách Cài Đặt và Chạy

### 1. Cài Đặt Các Thư Viện

Mở PowerShell hoặc Command Prompt trong thư mục chứa file và chạy:

```bash
pip install -r requirements.txt
```

### 2. Chạy Ứng Dụng

```bash
streamlit run streamlit_app.py
```

Ứng dụng sẽ mở tại: `http://localhost:8501`

### 3. Dùng Ứng Dụng

**Thanh bên trái:** Chọn mục muốn xem:
- 📊 **Tổng Quan:** Thống kê nhanh
- 📈 **Phân Tích Dữ Liệu:** 4 tab phân tích chi tiết
- 🤖 **Mô Hình Máy Học:** 2 mô hình với đánh giá toàn diện
- 📋 **Báo Cáo:** Báo cáo hoàn chỉnh, có thể tải CSV

## 📊 Các Tính Năng Chính

### 1. Tổng Quan
- Metrics: Tổng khách hàng, hạn mức tín dụng, tỷ lệ mặc định, tuổi trung bình

### 2. Phân Tích Dữ Liệu
- **Tab Phân Bố:** Histogram tuổi, hạn mức; pie chart tỷ lệ mặc định; bar chart trình độ học vấn
- **Tab Mối Quan Hệ:** Tỷ lệ mặc định theo tuổi; theo hạn mức tín dụng
- **Tab Thống Kê:** Bảng thống kê mô tả đầy đủ
- **Tab Giới Tính:** Phân tích so sánh theo giới tính

### 3. Mô Hình Máy Học
- **Logistic Regression:** Mô hình tuyến tính
  - Accuracy, F1 Score, ROC AUC
  - Báo cáo chi tiết (Precision, Recall, Support)
  - Ma trận nhầm lẫn và ROC Curve

- **Random Forest:** Mô hình cây quyết định
  - Accuracy, F1 Score, ROC AUC
  - Báo cáo chi tiết (Precision, Recall, Support)
  - Ma trận nhầm lẫn và ROC Curve
  - Top 15 đặc trưng quan trọng nhất

### 4. Báo Cáo
- Báo cáo markdown chi tiết với:
  - Tổng quan dự án
  - Phân tích dữ liệu (thống kê, nhân khẩu, học vấn)
  - Kết quả mô hình
  - Khuyến nghị hành động
  - Kết luận
- Bảng kết quả tóm tắt
- Nút tải CSV

## 📂 Cấu Trúc Thư Mục

```
.\
├── default of credit card clients.xlsx  # Dữ liệu gốc
├── streamlit_app.py                     # Ứng dụng chính
├── generate_report.py                   # Script tạo báo cáo txt
├── generate_pdf_report.py               # Module tạo báo cáo PDF
├── requirements.txt                     # Danh sách thư viện
└── README.md                            # Hướng dẫn này
```

## 📊 Dữ Liệu Đầu Vào

**File:** `default of credit card clients.xlsx`

**Cấu Trúc:**
- 30,001 hàng (khách hàng)
- 25 cột bao gồm:
  - `ID`: ID khách hàng
  - `LIMIT_BAL`: Hạn mức tín dụng
  - `SEX`: Giới tính (1: Nam, 2: Nữ)
  - `EDUCATION`: Trình độ học vấn
  - `MARRIAGE`: Tình trạng hôn nhân
  - `AGE`: Tuổi
  - `PAY_1` đến `PAY_6`: Trạng thái thanh toán 6 tháng gần nhất
  - `BILL_AMT1` đến `BILL_AMT6`: Số tiền hóa đơn 6 tháng
  - `PAY_AMT1` đến `PAY_AMT6`: Số tiền thanh toán 6 tháng
  - `DEFAULT`: Mặc định thanh toán tháng tiếp theo (0: Không, 1: Có)

## 🔍 Kết Quả Phân Tích Dự Kiến

### Thống Kê Cơ Bản
- Tỷ lệ mặc định: ~22%
- Tỷ lệ không mặc định: ~78%
- Tuổi trung bình: ~35 tuổi

### Mô Hình Random Forest
- Accuracy: ~0.82
- F1 Score: ~0.60-0.65
- ROC AUC: ~0.75-0.78

## 💡 Khuyến Nghị

1. **Quản lý rủi ro:** Tập trung vào khách hàng có hạn mức cao
2. **Phân khúc khách hàng:** Chính sách khác theo trình độ học vấn
3. **Giám sát sớm:** Sử dụng mô hình để phát hiện rủi ro
4. **Nâng cao tỷ lệ thu hồi:** Tăng cường biện pháp ngăn chặn

## 🛠️ Troubleshooting

### Lỗi "Module not found"
```bash
pip install -r requirements.txt
```

### Lỗi "File not found"
- Đảm bảo file `default of credit card clients.xlsx` có trong cùng thư mục

### Ứng dụng chạy chậm
- Dữ liệu được cache, lần đầu tiên sẽ chậm hơn

## 📞 Hỗ Trợ

Nếu gặp vấn đề:
1. Kiểm tra Python >= 3.9
2. Cập nhật pip: `pip install --upgrade pip`
3. Cài đặt lại thư viện: `pip install -r requirements.txt --upgrade`

## 📄 License

Dự án phục vụ mục đích giáo dục và phân tích kinh doanh.

---

**Tạo ngày:** 2026  
**Phiên bản:** 1.0
