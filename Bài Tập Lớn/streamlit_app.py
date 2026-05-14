import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    roc_curve,
    precision_recall_curve,
    f1_score,
    accuracy_score,
)
from generate_pdf_report import create_pdf_report
import warnings
from pathlib import Path
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Phân Tích Dữ Liệu Tín Dụng", layout="wide")

# Load data
@st.cache_data
def load_data():
    base_dir = Path(__file__).resolve().parent
    file_path = base_dir / 'default of credit card clients.xlsx'
    if not file_path.exists():
        st.error(f"❌ Không tìm thấy file dữ liệu: {file_path}")
        return pd.DataFrame()
    df = pd.read_excel(file_path, sheet_name='Data')
    return df

df = load_data()
if df.empty:
    st.stop()

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

# ==================== TIÊU ĐỀ ====================
st.title("🏦 Phân Tích Dữ Liệu Tín Dụng & CSV")
st.markdown("---")

# ==================== UPLOAD CSV ====================
st.sidebar.header("📤 Upload File CSV")
uploaded_file = st.sidebar.file_uploader("Chọn file CSV để phân tích", type=['csv'])

if uploaded_file is not None:
    st.sidebar.success("✅ File đã được upload thành công!")
    
    # Thử các encoding khác nhau
    encodings_to_try = ['utf-8', 'latin1', 'cp1252']
    df_csv = None
    successful_encoding = None
    
    for encoding in encodings_to_try:
        try:
            df_csv = pd.read_csv(uploaded_file, encoding=encoding)
            successful_encoding = encoding
            break
        except UnicodeDecodeError:
            continue
    
    if df_csv is not None:
        st.sidebar.info(f"📊 Đọc thành công với encoding: {successful_encoding}")
        st.sidebar.write(f"Shape: {df_csv.shape}")
        
        # Thêm tab phân tích CSV
        tab_names = ["📊 Tổng Quan", "📈 Phân Tích Dữ Liệu", "🤖 Mô Hình Máy Học", "📋 Báo Cáo", "📄 Phân Tích CSV"]
        section = st.sidebar.radio("Chọn mục để xem:", tab_names)
    else:
        st.sidebar.error("❌ Không thể đọc file CSV. Vui lòng kiểm tra encoding.")
        section = st.sidebar.radio("Chọn mục để xem:", ["📊 Tổng Quan", "📈 Phân Tích Dữ Liệu", "🤖 Mô Hình Máy Học", "📋 Báo Cáo"])
else:
    section = st.sidebar.radio("Chọn mục để xem:", ["📊 Tổng Quan", "📈 Phân Tích Dữ Liệu", "🤖 Mô Hình Máy Học", "📋 Báo Cáo"])

# ==================== 1. TỔNG QUAN ====================
if section == "📊 Tổng Quan":
    st.header("📊 Tổng Quan Dữ Liệu")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📌 Tổng Số Khách Hàng", f"{len(df):,}")
    with col2:
        st.metric("💳 Tổng Hạn Mức Tín Dụng", f"${df['LIMIT_BAL'].sum()/1e6:.2f}M")
    with col3:
        default_rate = (df['DEFAULT'].sum() / len(df) * 100)
        st.metric("⚠️ Tỷ Lệ Mặc Định", f"{default_rate:.2f}%")
    with col4:
        avg_age = df['AGE'].mean()
        st.metric("👤 Tuổi Trung Bình", f"{avg_age:.1f}")
    
    st.markdown("---")
    st.subheader("📋 Thông Tin Tập Dữ Liệu")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Số hàng:** {len(df):,}")
        st.write(f"**Số cột:** {len(df.columns)}")
        st.write(f"**Kiểu dữ liệu:** {df.dtypes.value_counts().to_dict()}")
    
    with col2:
        st.write(f"**Khách hàng không mặc định:** {(df['DEFAULT']==0).sum():,}")
        st.write(f"**Khách hàng mặc định:** {(df['DEFAULT']==1).sum():,}")
        st.write(f"**Dữ liệu bị thiếu:** {df.isnull().sum().sum()}")

# ==================== 2. PHÂN TÍCH DỮ LIỆU ====================
elif section == "📈 Phân Tích Dữ Liệu":
    st.header("📈 Phân Tích Thống Kê Chi Tiết")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Phân Bố", "Mối Quan Hệ", "Thống Kê", "Giới Tính"])
    
    with tab1:
        st.subheader("Phân Bố Dữ Liệu")
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.histogram(df, x='AGE', nbins=30, title='Phân Bố Tuổi',
                             labels={'AGE': 'Tuổi', 'count': 'Số Lượng'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.histogram(df, x='LIMIT_BAL', nbins=30, title='Phân Bố Hạn Mức Tín Dụng',
                             labels={'LIMIT_BAL': 'Hạn Mức', 'count': 'Số Lượng'})
            st.plotly_chart(fig, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            default_counts = df['DEFAULT'].value_counts()
            fig = px.pie(values=default_counts.values, names=['Không Mặc Định', 'Mặc Định'],
                        title='Tỷ Lệ Mặc Định Thanh Toán')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            education_counts = df['EDUCATION'].value_counts()
            edu_map = {1: 'Sau Đại Học', 2: 'Đại Học', 3: 'Trung Học', 4: 'Khác'}
            fig = px.bar(x=[edu_map.get(k, 'Unknown') for k in education_counts.index],
                        y=education_counts.values, title='Phân Bố Trình Độ Học Vấn',
                        labels={'x': 'Trình Độ', 'y': 'Số Lượng'})
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Mối Quan Hệ Giữa Các Biến")
        col1, col2 = st.columns(2)
        
        with col1:
            # Mối quan hệ giữa tuổi và mặc định
            avg_default_by_age = df.groupby('AGE')['DEFAULT'].mean() * 100
            fig = px.line(x=avg_default_by_age.index, y=avg_default_by_age.values,
                         title='Tỷ Lệ Mặc Định Theo Tuổi',
                         labels={'x': 'Tuổi', 'y': 'Tỷ Lệ Mặc Định (%)'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Mối quan hệ giữa hạn mức và mặc định
            df_sorted = df.sort_values('LIMIT_BAL')
            avg_default_by_limit = df_sorted.groupby(pd.cut(df_sorted['LIMIT_BAL'], bins=10))['DEFAULT'].mean() * 100
            fig = px.bar(x=range(len(avg_default_by_limit)), y=avg_default_by_limit.values,
                        title='Tỷ Lệ Mặc Định Theo Hạn Mức Tín Dụng',
                        labels={'x': 'Nhóm Hạn Mức', 'y': 'Tỷ Lệ Mặc Định (%)'})
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("Thống Kê Mô Tả")
        st.dataframe(df.describe(), use_container_width=True)
    
    with tab4:
        st.subheader("Phân Tích Theo Giới Tính")
        sex_default = df.groupby('SEX')['DEFAULT'].agg(['count', 'sum', 'mean'])
        sex_default.columns = ['Tổng Số', 'Mặc Định', 'Tỷ Lệ Mặc Định']
        sex_default.index = ['Nữ', 'Nam']
        sex_default['Tỷ Lệ Mặc Định'] = sex_default['Tỷ Lệ Mặc Định'] * 100
        st.dataframe(sex_default, use_container_width=True)
        
        fig = px.bar(x=['Nữ', 'Nam'], y=sex_default['Tỷ Lệ Mặc Định'],
                    title='Tỷ Lệ Mặc Định Theo Giới Tính',
                    labels={'x': 'Giới Tính', 'y': 'Tỷ Lệ Mặc Định (%)'})
        st.plotly_chart(fig, use_container_width=True)

# ==================== 3. MÔ HÌNH MÁY HỌC ====================
elif section == "📄 Phân Tích CSV":
    if uploaded_file is None or df_csv is None:
        st.error("Vui lòng upload file CSV hợp lệ trước khi sử dụng chức năng này.")
    else:
        st.header("📄 Phân Tích CSV Tải Lên")
        st.write(f"**Shape:** {df_csv.shape[0]:,} hàng, {df_csv.shape[1]:,} cột")
        st.write("**Danh sách cột:**")
        st.write(df_csv.columns.tolist())
        st.markdown("---")
        st.subheader("Dữ liệu mẫu")
        st.dataframe(df_csv.head(), use_container_width=True)
        
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Thông tin dữ liệu")
            st.write(df_csv.dtypes.to_frame('dtype'))
            st.write("**Missing values:**")
            st.write(df_csv.isnull().sum())
        with col2:
            st.subheader("Thống kê số")
            st.dataframe(df_csv.describe(), use_container_width=True)
        
        numeric_cols = df_csv.select_dtypes(include=np.number).columns.tolist()
        cat_cols = df_csv.select_dtypes(include=['object', 'category']).columns.tolist()
        
        if numeric_cols:
            st.markdown("---")
            st.subheader("Phân tích biến số")
            col1, col2 = st.columns(2)
            with col1:
                fig = px.histogram(df_csv, x=numeric_cols[0], nbins=30, title=f'Phân Bố {numeric_cols[0]}')
                st.plotly_chart(fig, use_container_width=True)
            if len(numeric_cols) > 1:
                with col2:
                    fig = px.scatter(df_csv, x=numeric_cols[0], y=numeric_cols[1], title=f'{numeric_cols[0]} vs {numeric_cols[1]}')
                    st.plotly_chart(fig, use_container_width=True)
            if len(numeric_cols) > 2:
                fig = px.imshow(df_csv[numeric_cols].corr(), text_auto=True, aspect='auto', title='Ma trận tương quan')
                st.plotly_chart(fig, use_container_width=True)
        
        if cat_cols:
            st.markdown("---")
            st.subheader("Phân tích biến phân loại")
            for col in cat_cols[:3]:
                counts = df_csv[col].value_counts().reset_index()
                counts.columns = [col, 'count']
                fig = px.bar(counts, x=col, y='count', title=f'Phân Bố {col}')
                st.plotly_chart(fig, use_container_width=True)

elif section == "🤖 Mô Hình Máy Học":
    st.header("🤖 Xây Dựng Mô Hình Dự Đoán")
    
    # Chuẩn bị dữ liệu
    X = df.drop(['ID', 'DEFAULT'], axis=1)
    y = df['DEFAULT']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    st.info("🔄 Đang huấn luyện mô hình...")
    
    # Huấn luyện các mô hình
    lr_model = LogisticRegression(max_iter=1000, random_state=42)
    lr_model.fit(X_train_scaled, y_train)
    lr_pred = lr_model.predict(X_test_scaled)
    lr_prob = lr_model.predict_proba(X_test_scaled)[:, 1]
    
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    rf_model.fit(X_train, y_train)
    rf_pred = rf_model.predict(X_test)
    rf_prob = rf_model.predict_proba(X_test)[:, 1]
    
    st.success("✅ Huấn luyện mô hình thành công!")
    
    # Hiển thị kết quả
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Logistic Regression")
        lr_acc = accuracy_score(y_test, lr_pred)
        lr_f1 = f1_score(y_test, lr_pred)
        lr_auc = roc_auc_score(y_test, lr_prob)
        
        st.metric("Độ Chính Xác", f"{lr_acc:.4f}")
        st.metric("F1 Score", f"{lr_f1:.4f}")
        st.metric("ROC AUC", f"{lr_auc:.4f}")
        
        st.write("**Báo Cáo Chi Tiết:**")
        st.text(classification_report(y_test, lr_pred, target_names=['Không Mặc Định', 'Mặc Định']))
    
    with col2:
        st.subheader("🌳 Random Forest")
        rf_acc = accuracy_score(y_test, rf_pred)
        rf_f1 = f1_score(y_test, rf_pred)
        rf_auc = roc_auc_score(y_test, rf_prob)
        
        st.metric("Độ Chính Xác", f"{rf_acc:.4f}")
        st.metric("F1 Score", f"{rf_f1:.4f}")
        st.metric("ROC AUC", f"{rf_auc:.4f}")
        
        st.write("**Báo Cáo Chi Tiết:**")
        st.text(classification_report(y_test, rf_pred, target_names=['Không Mặc Định', 'Mặc Định']))
    
    st.markdown("---")
    
    # Confusion Matrix
    col1, col2 = st.columns(2)
    
    with col1:
        cm_lr = confusion_matrix(y_test, lr_pred)
        fig = go.Figure(data=go.Heatmap(z=cm_lr, x=['Không Mặc Định', 'Mặc Định'], 
                                         y=['Không Mặc Định', 'Mặc Định'], text=cm_lr, texttemplate="%{text}"))
        fig.update_layout(title='Ma Trận Nhầm Lẫn - Logistic Regression')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        cm_rf = confusion_matrix(y_test, rf_pred)
        fig = go.Figure(data=go.Heatmap(z=cm_rf, x=['Không Mặc Định', 'Mặc Định'], 
                                         y=['Không Mặc Định', 'Mặc Định'], text=cm_rf, texttemplate="%{text}"))
        fig.update_layout(title='Ma Trận Nhầm Lẫn - Random Forest')
        st.plotly_chart(fig, use_container_width=True)
    
    # ROC Curve
    col1, col2 = st.columns(2)
    
    with col1:
        fpr_lr, tpr_lr, _ = roc_curve(y_test, lr_prob)
        fig = px.line(x=fpr_lr, y=tpr_lr, title='ROC Curve - Logistic Regression',
                     labels={'x': 'False Positive Rate', 'y': 'True Positive Rate'})
        fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode='lines', name='Random', 
                                line=dict(dash='dash', color='red')))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fpr_rf, tpr_rf, _ = roc_curve(y_test, rf_prob)
        fig = px.line(x=fpr_rf, y=tpr_rf, title='ROC Curve - Random Forest',
                     labels={'x': 'False Positive Rate', 'y': 'True Positive Rate'})
        fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode='lines', name='Random', 
                                line=dict(dash='dash', color='red')))
        st.plotly_chart(fig, use_container_width=True)
    
    # Feature Importance (Random Forest)
    st.subheader("⭐ Tầm Quan Trọng Của Các Đặc Trưng (Random Forest)")
    feature_importance = pd.DataFrame({
        'Feature': X.columns,
        'Importance': rf_model.feature_importances_
    }).sort_values('Importance', ascending=False).head(15)
    
    fig = px.bar(feature_importance, x='Importance', y='Feature', orientation='h',
                title='15 Đặc Trưng Quan Trọng Nhất')
    st.plotly_chart(fig, use_container_width=True)

# ==================== 4. BÁO CÁO ====================
else:  # section == "📋 Báo Cáo"
    st.header("📋 Báo Cáo Kết Quả Phân Tích")
    
    # Chuẩn bị dữ liệu cho báo cáo
    X = df.drop(['ID', 'DEFAULT'], axis=1)
    y = df['DEFAULT']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Huấn luyện cả 2 mô hình
    lr_model = LogisticRegression(max_iter=1000, random_state=42)
    lr_model.fit(X_train_scaled, y_train)
    lr_pred = lr_model.predict(X_test_scaled)
    lr_auc = roc_auc_score(y_test, lr_model.predict_proba(X_test_scaled)[:, 1])
    lr_f1 = f1_score(y_test, lr_pred)
    lr_acc = accuracy_score(y_test, lr_pred)
    cm_lr = confusion_matrix(y_test, lr_pred)
    
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    rf_model.fit(X_train, y_train)
    rf_pred = rf_model.predict(X_test)
    rf_auc = roc_auc_score(y_test, rf_model.predict_proba(X_test)[:, 1])
    rf_f1 = f1_score(y_test, rf_pred)
    rf_acc = accuracy_score(y_test, rf_pred)
    cm_rf = confusion_matrix(y_test, rf_pred)
    
    report_text = f"""
    # 📋 BÁO CÁO PHÂN TÍCH DỮ LIỆU TÍN DỤNG

    ## 1. TỔNG QUAN DỰ ÁN
    - **Tên dự án:** Phân Tích Dữ Liệu Mặc Định Thanh Toán Thẻ Tín Dụng
    - **Ngày báo cáo:** {pd.Timestamp.now().strftime('%d/%m/%Y')}
    - **Số khách hàng:** {len(df):,}
    - **Số lượng đặc trưng:** {len(X.columns)}

    ## 2. PHÂN TÍCH DỮ LIỆU

    ### 2.1 Thống Kê Cơ Bản
    - **Tỷ lệ mặc định thanh toán:** {(df['DEFAULT'].sum() / len(df) * 100):.2f}%
    - **Tỷ lệ không mặc định:** {((1 - df['DEFAULT'].mean()) * 100):.2f}%
    - **Tuổi trung bình:** {df['AGE'].mean():.1f} tuổi
    - **Hạn mức tín dụng trung bình:** ${df['LIMIT_BAL'].mean():,.0f}
    - **Hạn mức tín dụng tối đa:** ${df['LIMIT_BAL'].max():,.0f}
    - **Hạn mức tín dụng tối thiểu:** ${df['LIMIT_BAL'].min():,.0f}

    ### 2.2 Phân Tích Nhân Khẩu Học
    - **Tỷ lệ nữ giới:** {(df['SEX'] == 2).sum() / len(df) * 100:.2f}%
    - **Tỷ lệ nam giới:** {(df['SEX'] == 1).sum() / len(df) * 100:.2f}%
    - **Tỷ lệ mặc định nữ giới:** {(df[df['SEX'] == 2]['DEFAULT'].mean() * 100):.2f}%
    - **Tỷ lệ mặc định nam giới:** {(df[df['SEX'] == 1]['DEFAULT'].mean() * 100):.2f}%

    ### 2.3 Phân Tích Trình Độ Học Vấn
    """
    
    edu_map = {1: 'Sau Đại Học', 2: 'Đại Học', 3: 'Trung Học', 4: 'Khác'}
    for edu_level, edu_name in edu_map.items():
        count = (df['EDUCATION'] == edu_level).sum()
        default_rate = df[df['EDUCATION'] == edu_level]['DEFAULT'].mean() * 100
        report_text += f"\n    - **{edu_name}:** {count:,} khách hàng, Tỷ lệ mặc định: {default_rate:.2f}%"

    report_text += f"""

    ## 3. MÔ HÌNH MÁY HỌC

    ### 3.1 Kết Quả Mô Hình Random Forest
    - **Độ chính xác (Accuracy):** {accuracy_score(y_test, rf_pred):.4f}
    - **F1 Score:** {f1_score(y_test, rf_pred):.4f}
    - **ROC AUC Score:** {rf_auc:.4f}
    
    ### 3.2 Phân Tích Chi Tiết
    - **Precision (Mặc Định):** {(confusion_matrix(y_test, rf_pred)[1,1] / (confusion_matrix(y_test, rf_pred)[1,1] + confusion_matrix(y_test, rf_pred)[0,1])):.4f}
    - **Recall (Mặc Định):** {(confusion_matrix(y_test, rf_pred)[1,1] / (confusion_matrix(y_test, rf_pred)[1,1] + confusion_matrix(y_test, rf_pred)[1,0])):.4f}

    ## 4. KHUYẾN NGHỊ

    1. **Quản lý rủi ro:** Tập trung vào các khách hàng có hạn mức cao hơn và có dấu hiệu thanh toán bất thường
    2. **Phân khúc khách hàng:** Phát triển các chính sách khác nhau dựa trên trình độ học vấn và tuổi
    3. **Giám sát sớm:** Sử dụng mô hình để phát hiện khách hàng có nguy cơ cao trước khi xảy ra mặc định
    4. **Nâng cao tỷ lệ thu hồi:** Tăng cường các biện pháp ngăn chặn và thu hồi nợ

    ## 5. KẾT LUẬN

    Phân tích cho thấy mô hình Random Forest có hiệu suất tốt với ROC AUC = {rf_auc:.4f}. 
    Các yếu tố như lịch sử thanh toán, số tiền hóa đơn và tuổi là những chỉ báo quan trọng 
    để dự đoán khả năng mặc định thanh toán của khách hàng. Cần tiếp tục cải thiện mô hình 
    và áp dụng các biện pháp quản lý rủi ro phù hợp.

    ---
    _Báo cáo được tạo tự động từ hệ thống phân tích dữ liệu_
    """
    
    st.markdown(report_text)
    
    # Nút tải báo cáo
    st.markdown("---")
    st.subheader("📥 Tải Báo Cáo")
    
    report_data = {
        'Metric': [
            'Tổng Khách Hàng',
            'Tỷ Lệ Mặc Định (%)',
            'Tuổi Trung Bình',
            'Hạn Mức Trung Bình',
            'Logistic Accuracy',
            'Logistic ROC AUC',
            'Random Forest Accuracy',
            'Random Forest ROC AUC'
        ],
        'Value': [
            f"{len(df):,}",
            f"{(df['DEFAULT'].sum() / len(df) * 100):.2f}",
            f"{df['AGE'].mean():.1f}",
            f"{df['LIMIT_BAL'].mean():,.0f}",
            f"{lr_acc:.4f}",
            f"{lr_auc:.4f}",
            f"{rf_acc:.4f}",
            f"{rf_auc:.4f}"
        ]
    }
    
    report_df = pd.DataFrame(report_data)
    st.dataframe(report_df, use_container_width=True)
    
    # Tạo PDF
    model_results = {
        'lr_acc': lr_acc,
        'lr_f1': lr_f1,
        'lr_auc': lr_auc,
        'rf_acc': rf_acc,
        'rf_f1': rf_f1,
        'rf_auc': rf_auc,
        'cm_lr': cm_lr,
        'cm_rf': cm_rf
    }
    
    pdf_bytes = create_pdf_report(df, model_results)
    st.download_button(
        label="📄 Tải PDF",
        data=pdf_bytes,
        file_name="credit_analysis_report.pdf",
        mime="application/pdf",
        icon="📄"
    )

st.markdown("---")
st.caption("🔐 Ứng dụng Streamlit - Phân Tích Dữ Liệu Tín Dụng © 2026")
