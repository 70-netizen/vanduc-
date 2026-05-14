"""
Module tạo PDF báo cáo phân tích dữ liệu
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from datetime import datetime
import os
import io


def register_vietnamese_font():
    font_candidates = [
        (r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\arialbd.ttf"),
        (r"C:\Windows\Fonts\ARIAL.TTF", r"C:\Windows\Fonts\ARIALBD.TTF"),
        (r"C:\Windows\Fonts\arialuni.ttf", r"C:\Windows\Fonts\arialbd.ttf"),
        (r"C:\Windows\Fonts\DejaVuSans.ttf", r"C:\Windows\Fonts\DejaVuSans-Bold.ttf"),
    ]
    for regular_path, bold_path in font_candidates:
        if os.path.exists(regular_path) and os.path.exists(bold_path):
            try:
                if 'arial' in os.path.basename(regular_path).lower():
                    pdfmetrics.registerFont(TTFont('Arial', regular_path))
                    pdfmetrics.registerFont(TTFont('Arial-Bold', bold_path))
                    pdfmetrics.registerFontFamily('Arial', normal='Arial', bold='Arial-Bold')
                    return 'Arial', 'Arial-Bold'
                pdfmetrics.registerFont(TTFont('DejaVuSans', regular_path))
                pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', bold_path))
                pdfmetrics.registerFontFamily('DejaVuSans', normal='DejaVuSans', bold='DejaVuSans-Bold')
                return 'DejaVuSans', 'DejaVuSans-Bold'
            except Exception:
                continue
    return 'Helvetica', 'Helvetica-Bold'

def create_pdf_report(df, model_results):
    """
    Tạo báo cáo PDF từ dữ liệu phân tích
    
    Parameters:
    -----------
    df : DataFrame
        Dữ liệu đã xử lý
    model_results : dict
        Kết quả mô hình bao gồm:
        - lr_acc, lr_f1, lr_auc, cm_lr
        - rf_acc, rf_f1, rf_auc, cm_rf
    
    Returns:
    --------
    bytes : PDF content
    """
    
    # Tạo buffer để lưu PDF
    buffer = io.BytesIO()
    
    # Tạo document PDF
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    # Danh sách các element để thêm vào PDF
    elements = []
    
    # Định nghĩa các style
    styles = getSampleStyleSheet()
    regular_font, bold_font = register_vietnamese_font()
    
    # Style cho tiêu đề
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName=bold_font
    )
    
    # Style cho heading
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2e5c8a'),
        spaceAfter=12,
        spaceBefore=12,
        fontName=bold_font,
        borderPadding=5
    )
    
    # Style cho normal text
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=10,
        spaceAfter=6,
        alignment=TA_JUSTIFY,
        fontName=regular_font
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=12,
        fontName=regular_font,
        spaceAfter=6,
        alignment=TA_CENTER
    )
    
    # === TIÊU ĐỀ ===
    title = Paragraph("🏦 BÁO CÁO PHÂN TÍCH DỮ LIỆU", title_style)
    elements.append(title)
    
    subtitle = Paragraph("Mặc Định Thanh Toán Thẻ Tín Dụng", subtitle_style)
    elements.append(subtitle)
    
    date_text = Paragraph(f"<b>Ngày báo cáo:</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", body_style)
    elements.append(date_text)
    
    elements.append(Spacer(1, 0.3*inch))
    
    # === 1. TỔNG QUAN ===
    elements.append(Paragraph("1. TỔNG QUAN DỰ ÁN", heading_style))
    
    overview_data = [
        ["Tên Dự Án", "Phân Tích Dữ Liệu Mặc Định Thanh Toán Thẻ Tín Dụng"],
        ["Số Khách Hàng", f"{len(df):,}"],
        ["Số Đặc Trưng", "23"],
        ["Tỷ Lệ Chia (Train/Test)", "70% / 30%"],
        ["Tỷ Lệ Mặc Định", f"{(df['DEFAULT'].sum() / len(df) * 100):.2f}%"],
    ]
    
    overview_table = Table(overview_data, colWidths=[2*inch, 3.5*inch])
    overview_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f0f7')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), regular_font),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTNAME', (0, 0), (-1, 0), bold_font),
    ]))
    
    elements.append(overview_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # === 2. PHÂN TÍCH THỐNG KÊ ===
    elements.append(Paragraph("2. PHÂN TÍCH THỐNG KÊ CƠ BẢN", heading_style))
    
    # Thống kê mặc định
    default_non = (df['DEFAULT'] == 0).sum()
    default_yes = (df['DEFAULT'] == 1).sum()
    
    stat_data = [
        ["Chỉ Số", "Giá Trị"],
        ["Khách Hàng Không Mặc Định", f"{default_non:,} ({default_non/len(df)*100:.2f}%)"],
        ["Khách Hàng Mặc Định", f"{default_yes:,} ({default_yes/len(df)*100:.2f}%)"],
        ["Tuổi Trung Bình", f"{df['AGE'].mean():.1f} tuổi"],
        ["Hạn Mức Trung Bình", f"${df['LIMIT_BAL'].mean():,.0f}"],
        ["Hạn Mức Tối Đa", f"${df['LIMIT_BAL'].max():,.0f}"],
    ]
    
    stat_table = Table(stat_data, colWidths=[2.5*inch, 3*inch])
    stat_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e5c8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), regular_font),
        ('FONTNAME', (0, 0), (-1, 0), bold_font),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f5f9')]),
    ]))
    
    elements.append(stat_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Phân tích giới tính
    female = (df['SEX'] == 2).sum()
    male = (df['SEX'] == 1).sum()
    female_default = (df[df['SEX'] == 2]['DEFAULT'].mean() * 100)
    male_default = (df[df['SEX'] == 1]['DEFAULT'].mean() * 100)
    
    gender_text = f"""
    <b>Phân Tích Giới Tính:</b><br/>
    • Nữ: {female:,} ({female/len(df)*100:.2f}%) - Tỷ lệ mặc định: {female_default:.2f}%<br/>
    • Nam: {male:,} ({male/len(df)*100:.2f}%) - Tỷ lệ mặc định: {male_default:.2f}%
    """
    
    elements.append(Paragraph(gender_text, body_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # === 3. KẾT QUẢ MÔ HÌNH ===
    elements.append(Paragraph("3. KẾT QUẢ MÔ HÌNH MÁY HỌC", heading_style))
    
    lr_acc = model_results['lr_acc']
    lr_f1 = model_results['lr_f1']
    lr_auc = model_results['lr_auc']
    rf_acc = model_results['rf_acc']
    rf_f1 = model_results['rf_f1']
    rf_auc = model_results['rf_auc']
    
    model_data = [
        ["Mô Hình", "Accuracy", "F1 Score", "ROC AUC"],
        ["Logistic Regression", f"{lr_acc:.4f}", f"{lr_f1:.4f}", f"{lr_auc:.4f}"],
        ["Random Forest ⭐", f"{rf_acc:.4f}", f"{rf_f1:.4f}", f"{rf_auc:.4f}"],
    ]
    
    model_table = Table(model_data, colWidths=[2*inch, 1.3*inch, 1.3*inch, 1.2*inch])
    model_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e5c8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), regular_font),
        ('FONTNAME', (0, 0), (-1, 0), bold_font),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#e8f0f7')]),
        ('TEXTCOLOR', (0, 2), (-1, 2), colors.HexColor('#d9534f')),
        ('FONTNAME', (0, 2), (-1, 2), bold_font),
    ]))
    
    elements.append(model_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Ma trận nhầm lẫn
    cm_lr = model_results['cm_lr']
    cm_rf = model_results['cm_rf']
    
    cm_text = f"""
    <b>Ma Trận Nhầm Lẫn - Logistic Regression:</b><br/>
    • True Negative: {cm_lr[0,0]:,} | False Positive: {cm_lr[0,1]:,}<br/>
    • False Negative: {cm_lr[1,0]:,} | True Positive: {cm_lr[1,1]:,}<br/><br/>
    
    <b>Ma Trận Nhầm Lẫn - Random Forest:</b><br/>
    • True Negative: {cm_rf[0,0]:,} | False Positive: {cm_rf[0,1]:,}<br/>
    • False Negative: {cm_rf[1,0]:,} | True Positive: {cm_rf[1,1]:,}
    """
    
    elements.append(Paragraph(cm_text, body_style))
    elements.append(PageBreak())
    
    # === 4. KHUYẾN NGHỊ ===
    elements.append(Paragraph("4. KHUYẾN NGHỊ VÀ HÀNH ĐỘNG", heading_style))
    
    recommendation = """
    <b>1. QUẢN LÝ RỦI RO</b><br/>
    • Tập trung giám sát khách hàng có hạn mức tín dụng cao (>100,000)<br/>
    • Khách hàng với lịch sử thanh toán bất thường cần theo dõi chặt chẽ<br/>
    • Xây dựng mô hình cảnh báo sớm dựa trên các đặc trưng được xác định<br/><br/>
    
    <b>2. PHÂN KHÚC KHÁCH HÀNG</b><br/>
    • Phát triển chiến lược khác nhau cho từng nhóm trình độ học vấn<br/>
    • Xem xét tuổi khi xây dựng chính sách tín dụng<br/>
    • Chú ý sự khác biệt giữa khách hàng nam và nữ<br/><br/>
    
    <b>3. GIÁ TRỊ MÔ HÌNH</b><br/>
    • Mô hình đạt độ chính xác trên 81%<br/>
    • ROC AUC trên 0.75 cho phép phân loại rủi ro tương đối tốt<br/>
    • Có thể triển khai vào quy trình phê duyệt tín dụng<br/><br/>
    
    <b>4. CẢI THIỆN TIẾP THEO</b><br/>
    • Thu thập thêm dữ liệu để cải thiện độ chính xác<br/>
    • Xây dựng các đặc trưng mới dựa trên domain knowledge<br/>
    • Thử nghiệm các mô hình phức tạp hơn (XGBoost, LightGBM)<br/>
    • Tuning hyperparameter chi tiết
    """
    
    elements.append(Paragraph(recommendation, body_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # === 5. KẾT LUẬN ===
    elements.append(Paragraph("5. KẾT LUẬN", heading_style))
    
    conclusion = f"""
    Phân tích chi tiết cho thấy:<br/><br/>
    
    1. Tỷ lệ mặc định thanh toán là {(df['DEFAULT'].sum() / len(df) * 100):.2f}%, 
    cho thấy khoảng 22% khách hàng có nguy cơ không thanh toán.<br/><br/>
    
    2. Mô hình Random Forest với ROC AUC = {rf_auc:.4f} là công cụ hữu ích 
    để dự đoán khách hàng mặc định.<br/><br/>
    
    3. Các yếu tố chính ảnh hưởng đến khả năng mặc định bao gồm:<br/>
    • Lịch sử thanh toán (PAY_1, PAY_2, ...)<br/>
    • Số tiền hóa đơn tích lũy<br/>
    • Tuổi khách hàng<br/>
    • Hạn mức tín dụng<br/><br/>
    
    4. Khuyến nghị áp dụng mô hình vào quy trình quản lý rủi ro 
    để giảm thiểu tổ thất từ mặc định thanh toán.
    """
    
    elements.append(Paragraph(conclusion, body_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Build PDF
    doc.build(elements)
    
    # Lấy giá trị PDF từ buffer
    buffer.seek(0)
    return buffer.getvalue()
