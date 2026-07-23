from typing import Dict
from app.domain.models import QuotationResult


class QuotationExportService:
    """
    Dịch vụ hỗ trợ định dạng báo giá thành văn bản xem trước, file HTML in ấn/PDF
    và tin nhắn tóm tắt tối ưu gửi qua Zalo cho khách hàng.
    """

    def generate_html_report(self, quotation: QuotationResult, workshop_name: str = "Xưởng Mộc Nội Thất") -> str:
        """
        Tạo trang HTML báo giá chuyên nghiệp sẵn sàng cho việc xem trước và in ấn (Print to PDF).
        """
        items_rows = ""
        for idx, item in enumerate(quotation.items, 1):
            dim_str = f"{item.quoted_item.length/1000:.2f}m"
            if item.quoted_item.width > 0:
                dim_str += f" x {item.quoted_item.width/1000:.2f}m"
            
            wood_name = item.quoted_item.wood_type or "MDF Melamine"

            items_rows += f"""
            <tr>
                <td style="text-align: center;">{idx}</td>
                <td>
                    <strong>{item.quoted_item.name}</strong><br/>
                    <small style="color: #666;">KT: {dim_str} | Loại ván: {wood_name}</small>
                </td>
                <td style="text-align: center;">{item.unit}</td>
                <td style="text-align: center;">{item.quoted_item.quantity}</td>
                <td style="text-align: right;">{item.unit_price:,} đ</td>
                <td style="text-align: right; font-weight: bold;">{item.total_price:,} đ</td>
            </tr>
            """

        html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Bảng Báo Giá Nội Thất - {workshop_name}</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 30px; color: #2d3748; line-height: 1.6; }}
        .header {{ display: flex; justify-content: space-between; border-bottom: 2px solid #3182ce; padding-bottom: 15px; margin-bottom: 20px; }}
        .title {{ font-size: 24px; font-weight: bold; color: #2b6cb0; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        th {{ background-color: #ebf8ff; color: #2b6cb0; border: 1px solid #cbd5e0; padding: 10px; font-size: 14px; }}
        td {{ border: 1px solid #e2e8f0; padding: 10px; font-size: 14px; }}
        .total-box {{ margin-top: 25px; float: right; width: 320px; border: 1px solid #3182ce; border-radius: 8px; padding: 15px; background-color: #f7fafc; }}
        .total-row {{ display: flex; justify-content: space-between; font-size: 16px; margin-bottom: 5px; }}
        .grand-total {{ font-size: 20px; font-weight: bold; color: #c53030; border-top: 1px solid #cbd5e0; padding-top: 10px; }}
        .footer {{ margin-top: 80px; text-align: center; font-size: 12px; color: #718096; border-top: 1px solid #e2e8f0; padding-top: 15px; }}
    </style>
</head>
<body>
    <div class="header">
        <div>
            <div class="title">{workshop_name}</div>
            <div>Hệ thống Báo giá Nhanh Quick-Quote AI</div>
        </div>
        <div style="text-align: right;">
            <div><strong>BẢNG BÁO GIÁ NỘI THẤT</strong></div>
            <div style="font-size: 12px; color: #718096;">Áp dụng cho đơn hàng mộc</div>
        </div>
    </div>

    <table>
        <thead>
            <tr>
                <th style="width: 40px;">STT</th>
                <th>Hạng Mục Sản Phẩm</th>
                <th style="width: 70px;">ĐVT</th>
                <th style="width: 60px;">SL</th>
                <th style="width: 120px;">Đơn Giá</th>
                <th style="width: 140px;">Thành Tiền</th>
            </tr>
        </thead>
        <tbody>
            {items_rows}
        </tbody>
    </table>

    <div class="total-box">
        <div class="total-row grand-total">
            <span>TỔNG CỘNG:</span>
            <span>{quotation.total_amount:,} VNĐ</span>
        </div>
    </div>

    <div style="clear: both;"></div>

    <div class="footer">
        Cảm ơn Quý khách hàng đã tin tưởng dịch vụ sản xuất mộc nội thất của chúng tôi!
    </div>
</body>
</html>
"""
        return html_content

    def generate_zalo_summary(self, quotation: QuotationResult, workshop_name: str = "Xưởng Mộc Nội Thất") -> str:
        """
        Tạo đoạn văn bản tóm tắt tối ưu để chép & gửi nhanh qua Zalo cho khách hàng.
        """
        lines = [
            f"📋 *BẢNG BÁO GIÁ NỘI THẤT - {workshop_name.upper()}*",
            "--------------------------------",
        ]

        for idx, item in enumerate(quotation.items, 1):
            dim_str = f"{item.quoted_item.length/1000:.2f}m"
            if item.quoted_item.width > 0:
                dim_str += f"x{item.quoted_item.width/1000:.2f}m"

            lines.append(
                f"{idx}. {item.quoted_item.name} ({dim_str})"
            )
            lines.append(
                f"   👉 SL: {item.quoted_item.quantity} {item.unit} | Đơn giá: {item.unit_price:,}đ -> {item.total_price:,}đ"
            )

        lines.append("--------------------------------")
        lines.append(f"💰 *TỔNG CỘNG BÁO GIÁ: {quotation.total_amount:,} VNĐ*")
        lines.append("\nKính gửi Quý khách tham khảo. Vui lòng phản hồi nếu cần điều chỉnh!")

        return "\n".join(lines)
