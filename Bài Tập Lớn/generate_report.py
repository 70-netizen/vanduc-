"""
Script phân tích dữ liệu tín dụng - Tạo báo cáo txt
Chạy: python generate_report.py
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    accuracy_score,
    f1_score,
)
import warnings
from pathlib import Path
warnings.filterwarnings('ignore')

# ==================== LOAD DỮ LIỆU ====================
print("📂 Đang tải dữ liệu...")
base_dir = Path(__file__).resolve().parent
file_path = base_dir / 'default of credit card clients.xlsx'
if not file_path.exists():
    raise FileNotFoundError(f"Không tìm thấy file dữ liệu: {file_path}")
df = pd.read_excel(file_path, sheet_name='Data')

# Xử lý dữ liệu
df = df.iloc[1:]  # Bỏ hàng header thứ 2
df.columns = ['ID', 'LIMIT_BAL', 'SEX', 'EDUCATION', 'MARRIAGE', 'AGE', 
              'PAY_1', 'PAY_2', 'PAY_3', 'PAY_4', 'PAY_5', 'PAY_6',
              'BILL_AMT1', 'BILL_AMT2', 'BILL_AMT3', 'BILL_AMT4', 'BILL_AMT5', 'BILL_AMT6',
              'PAY_AMT1', 'PAY_AMT2', 'PAY_AMT3', 'PAY_AMT4', 'PAY_AMT5', 'PAY_AMT6', 'DEFAULT']

# Chuyển đổi kiểu dữ liệu
for col in df.columns:
    if col != 'ID':
        df[col] = pd.to_numeric(df[col], errors='coerce')

df = df.dropna()
print(f"✅ Đã tải {len(df):,} hàng, {len(df.columns)} cột")

# ==================== XỬ LÝ DỮ LIỆU ====================
print("\n📊 Đang xử lý dữ liệu...")
X = df.drop(['ID', 'DEFAULT'], axis=1)
y = df['DEFAULT']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ==================== HUẤN LUYỆN MÔ HÌNH ====================
print("🤖 Đang huấn luyện mô hình...")

# Logistic Regression
lr_model = LogisticRegression(max_iter=1000, random_state=42)
lr_model.fit(X_train_scaled, y_train)
lr_pred = lr_model.predict(X_test_scaled)
lr_prob = lr_model.predict_proba(X_test_scaled)[:, 1]

# Random Forest
rf_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
rf_model.fit(X_train, y_train)
rf_pred = rf_model.predict(X_test)
rf_prob = rf_model.predict_proba(X_test)[:, 1]

print("✅ Huấn luyện hoàn thành")

# ==================== TẠO BÁO CÁO ====================
report = f"""
{'='*80}
                    BÁO CÁO PHÂN TÍCH DỮ LIỆU THANH TOÁN THẺ TÍN DỤNG
{'='*80}

NGÀY BÁO CÁO: {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M:%S')}

{'='*80}
1. TỔNG QUAN DỰ ÁN
{'='*80}

Tên dự án:              Phân Tích Dữ Liệu Mặc Định Thanh Toán Thẻ Tín Dụng
Nguồn dữ liệu:          default of credit card clients.xlsx
Số khách hàng (toàn bộ): {len(df):,}
Số khách hàng (sau xử lý): {len(df):,}
Số đặc trưng:           {len(X.columns)}
Tỉ lệ chia (train/test): 70% / 30%

{'='*80}
2. PHÂN TÍCH THỐNG KÊ CƠ BẢN
{'='*80}

2.1 Thống Kê Mặc Định Thanh Toán
────────────────────────────────
Tổng khách hàng không mặc định:  {(df['DEFAULT']==0).sum():,} ({(df['DEFAULT']==0).sum()/len(df)*100:.2f}%)
Tổng khách hàng mặc định:        {(df['DEFAULT']==1).sum():,} ({(df['DEFAULT']==1).sum()/len(df)*100:.2f}%)

2.2 Thống Kê Tuổi
─────────────────
Tuổi trung bình:        {df['AGE'].mean():.1f} tuổi
Tuổi tối thiểu:         {df['AGE'].min():.0f} tuổi
Tuổi tối đa:            {df['AGE'].max():.0f} tuổi
Độ lệch chuẩn:          {df['AGE'].std():.2f}

2.3 Thống Kê Hạn Mức Tín Dụng
──────────────────────────────
Hạn mức trung bình:     ${df['LIMIT_BAL'].mean():,.0f}
Hạn mức tối thiểu:      ${df['LIMIT_BAL'].min():,.0f}
Hạn mức tối đa:         ${df['LIMIT_BAL'].max():,.0f}
Tổng hạn mức:           ${df['LIMIT_BAL'].sum():,.0f}

2.4 Phân Tích Giới Tính
──────────────────────
Nữ giới:                {(df['SEX']==2).sum():,} ({(df['SEX']==2).sum()/len(df)*100:.2f}%)
Nam giới:               {(df['SEX']==1).sum():,} ({(df['SEX']==1).sum()/len(df)*100:.2f}%)
Tỷ lệ mặc định nữ:      {(df[df['SEX']==2]['DEFAULT'].mean()*100):.2f}%
Tỷ lệ mặc định nam:     {(df[df['SEX']==1]['DEFAULT'].mean()*100):.2f}%

2.5 Phân Tích Trình Độ Học Vấn
────────────────────────────────
"""

edu_map = {1: 'Sau Đại Học', 2: 'Đại Học', 3: 'Trung Học', 4: 'Khác'}
for edu_level, edu_name in edu_map.items():
    count = (df['EDUCATION'] == edu_level).sum()
    default_rate = df[df['EDUCATION'] == edu_level]['DEFAULT'].mean() * 100
    report += f"{edu_name:20} {count:,} khách hàng - Tỷ lệ mặc định: {default_rate:.2f}%\n"

# Tính toán metrics cho các mô hình
lr_acc = accuracy_score(y_test, lr_pred)
lr_f1 = f1_score(y_test, lr_pred)
lr_auc = roc_auc_score(y_test, lr_prob)

rf_acc = accuracy_score(y_test, rf_pred)
rf_f1 = f1_score(y_test, rf_pred)
rf_auc = roc_auc_score(y_test, rf_prob)

cm_lr = confusion_matrix(y_test, lr_pred)
cm_rf = confusion_matrix(y_test, rf_pred)

report += f"""

{'='*80}
3. KẾT QUẢ MÔ HÌNH MÁY HỌC
{'='*80}

3.1 Logistic Regression
──────────────────────
Accuracy:               {lr_acc:.4f}
F1 Score:               {lr_f1:.4f}
ROC AUC:                {lr_auc:.4f}

Ma Trận Nhầm Lẫn:
                    Dự Đoán Không    Dự Đoán Có
Thực Tế Không:          {cm_lr[0,0]:,}          {cm_lr[0,1]:,}
Thực Tế Có:             {cm_lr[1,0]:,}          {cm_lr[1,1]:,}

3.2 Random Forest
────────────────
Accuracy:               {rf_acc:.4f}
F1 Score:               {rf_f1:.4f}
ROC AUC:                {rf_auc:.4f}

Ma Trận Nhầm Lẫn:
                    Dự Đoán Không    Dự Đoán Có
Thực Tế Không:          {cm_rf[0,0]:,}          {cm_rf[0,1]:,}
Thực Tế Có:             {cm_rf[1,0]:,}          {cm_rf[1,1]:,}

3.3 So Sánh Mô Hình
──────────────────
"""

if rf_auc > lr_auc:
    report += f"Mô hình tốt nhất: Random Forest (ROC AUC: {rf_auc:.4f} > {lr_auc:.4f})\n"
else:
    report += f"Mô hình tốt nhất: Logistic Regression (ROC AUC: {lr_auc:.4f} > {rf_auc:.4f})\n"

# Tính tầm quan trọng của đặc trưng
feature_importance = pd.DataFrame({
    'Feature': X.columns,
    'Importance': rf_model.feature_importances_
}).sort_values('Importance', ascending=False).head(10)

report += f"""

3.4 Top 10 Đặc Trưng Quan Trọng (Random Forest)
─────────────────────────────────────────────────
"""

for idx, row in feature_importance.iterrows():
    report += f"{row['Feature']:15} {row['Importance']:.6f}\n"

report += f"""

{'='*80}
4. KHUYẾN NGHỊ
{'='*80}

1. QUẢN LÝ RỦI RO
   - Tập trung giám sát khách hàng có hạn mức tín dụng cao (>100,000)
   - Những khách hàng với lịch sử thanh toán bất thường cần được theo dõi chặt chẽ
   - Xây dựng mô hình cảnh báo sớm dựa trên các đặc trưng được xác định

2. PHÂN KHÚC KHÁCH HÀNG
   - Phát triển chiến lược khác nhau cho từng nhóm trình độ học vấn
   - Xem xét các yếu tố tuổi khi xây dựng chính sách tín dụng
   - Giá trị khách hàng nữ và nam có chênh lệch, cần chú ý

3. GIÁ TRỊ MÔ HÌNH
   - Mô hình hiện tại đạt độ chính xác {max(lr_acc, rf_acc):.2%}
   - ROC AUC {max(lr_auc, rf_auc):.4f} cho phép phân loại rủi ro tương đối tốt
   - Có thể triển khai vào quy trình phê duyệt tín dụng

4. CẢI THIỆN TIẾP THEO
   - Thu thập thêm dữ liệu để cải thiện độ chính xác
   - Xây dựng các đặc trưng mới dựa trên domain knowledge
   - Thử nghiệm các mô hình phức tạp hơn (XGBoost, Neural Networks)
   - Tuning hyperparameter chi tiết

{'='*80}
5. KẾT LUẬN
{'='*80}

Dựa trên phân tích chi tiết, chúng tôi nhận thấy:

1. Tỷ lệ mặc định thanh toán là {(df['DEFAULT'].sum() / len(df) * 100):.2f}%, cho thấy khoảng {(df['DEFAULT'].sum() / len(df) * 100):.0f} 
   trong số khách hàng có nguy cơ không thanh toán.

2. Mô hình Random Forest với ROC AUC = {rf_auc:.4f} là công cụ hữu ích 
   để dự đoán khách hàng mặc định.

3. Các yếu tố chính ảnh hưởng đến khả năng mặc định bao gồm:
   - Lịch sử thanh toán (PAY_1, PAY_2, v.v.)
   - Số tiền hóa đơn tích lũy
   - Tuổi khách hàng
   - Hạn mức tín dụng

4. Khuyến nghị áp dụng mô hình vào quy trình quản lý rủi ro 
   để giảm thiểu tổn thất từ mặc định thanh toán.

{'='*80}
ĐƯỢC TẠO BỞI: Hệ Thống Phân Tích Dữ Liệu Tự Động
PHIÊN BẢN: 1.0
NGÀY TẠO: {pd.Timestamp.now().strftime('%d/%m/%Y')}
{'='*80}
"""

# ==================== LƯU BÁO CÁO ====================
report_path = base_dir / 'BAOCAO_PHANTICHDULIEU.txt'
with open(report_path, 'w', encoding='utf-8') as f:
    f.write(report)

print(f"\n✅ Báo cáo đã được tạo: {report_path}")
print("\n" + "="*80)
print(report)
print("="*80)

# ==================== TÓSUM ====================
summary = f"""

📊 TÓSUM NHANH:
   • Khách hàng không mặc định: {(df['DEFAULT']==0).sum():,} ({(df['DEFAULT']==0).sum()/len(df)*100:.2f}%)
   • Khách hàng mặc định: {(df['DEFAULT']==1).sum():,} ({(df['DEFAULT']==1).sum()/len(df)*100:.2f}%)
   • Mô hình tốt nhất: {'Random Forest' if rf_auc > lr_auc else 'Logistic Regression'}
   • ROC AUC Score: {max(lr_auc, rf_auc):.4f}
"""

print(summary)
