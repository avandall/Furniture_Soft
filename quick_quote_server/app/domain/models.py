from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class QuotedItem(BaseModel):
    """
    Dữ liệu mộc thô do Vision LLM bóc tách hoặc người dùng nhập/sửa trên UI.
    Tương ứng với JSON Schema nhận từ Gemini API và bảng kê BOM thô.
    """
    name: str = Field(..., description="Tên thực thể, e.g. 'Tủ quần áo kịch trần'")
    length: float = Field(..., ge=0, description="Kích thước chiều dài/cao (mm)")
    width: float = Field(default=0.0, ge=0, description="Kích thước chiều rộng/ngang (mm)")
    depth: float = Field(default=0.0, ge=0, description="Kích thước chiều sâu (mm)")
    wood_type: str = Field(default="", description="Cốt gỗ/bề mặt mộc, e.g. 'mdf_melamine', 'mdf_acrylic'")
    quantity: int = Field(default=1, ge=1, description="Số lượng sản phẩm")
    category: str = Field(default="Khác", description="Phân loại hạng mục để map bảng giá")


class CategoryPricing(BaseModel):
    """
    Cấu hình đơn giá theo từng loại vật liệu của 1 danh mục xưởng.
    """
    category: str = Field(..., description="Tên danh mục mộc, e.g. 'Tủ áo', 'Tủ bếp dưới'")
    unit: str = Field(..., description="Đơn vị tính toán: 'md' (mét dài), 'm2' (mét vuông), 'cái', 'bộ'")
    prices: Dict[str, int] = Field(
        default_factory=dict,
        description="Bảng giá bán theo từng loại vật liệu (VND), e.g. {'mdf_melamine': 2200000, 'mdf_acrylic': 2800000}"
    )
    board_sheet_price: int = Field(
        default=0,
        ge=0,
        description="Đơn giá nhập gốc 1 tấm ván tiêu chuẩn 1220x2440mm (VND)"
    )
    labor_cost_per_unit: int = Field(
        default=0,
        ge=0,
        description="Đơn giá công thợ sản xuất/lắp đặt theo đơn vị m2 hoặc md (VND)"
    )
    keywords: List[str] = Field(
        default_factory=list,
        description="Từ khóa tiếng Việt để so khớp tên item tự động (Fuzzy matching)"
    )


class WorkshopPricingConfig(BaseModel):
    """
    Cấu hình bảng giá toàn bộ của xưởng gỗ (lưu dưới dạng JSONB trong DB).
    """
    workshop_id: str = Field(..., description="Mã xưởng gỗ")
    categories: List[CategoryPricing] = Field(default_factory=list, description="Danh sách cấu hình danh mục")
    default_profit_margin_percentage: float = Field(
        default=0.0,
        ge=0,
        le=300,
        description="Tỷ lệ phần trăm lợi nhuận mặc định của xưởng (%)"
    )

    default_unit_prices: Dict[str, int] = Field(
        default_factory=dict,
        description="Giá dự phòng theo đơn vị khi vật liệu hoặc danh mục chưa được định nghĩa"
    )


class CostBreakdown(BaseModel):
    """
    Bóc tách giá vốn gốc dành riêng cho giao diện quản trị chủ xưởng (Owner Cost Panel).
    Ẩn hoàn toàn trên giao diện báo giá gửi cho khách hàng.
    """
    board_sheets_estimated: float = Field(default=0.0, description="Số tấm ván tiêu chuẩn 1220x2440mm ước tính (kèm 15% hao hụt)")
    board_material_cost: int = Field(default=0, description="Tổng tiền ván mộc gốc nhập vào (VND)")
    labor_cost: int = Field(default=0, description="Tiền công thợ bổ ván, dán cạnh & lắp ráp (VND)")
    hardware_cost: int = Field(default=0, description="Tiền phụ kiện & vật tư phụ ước tính (VND)")
    total_base_cost: int = Field(default=0, description="Tổng giá vốn gốc của hạng mục (VND)")


class CalculatedItemQuote(BaseModel):
    """
    Kết quả tính giá chính xác cho một hạng mục sau khi đi qua Rule Engine.
    """
    quoted_item: QuotedItem
    matched_category: str = Field(..., description="Tên danh mục khớp được trong cấu hình xưởng")
    unit: str = Field(..., description="Đơn vị tính áp dụng ('md', 'm2', 'cái')")
    dimension_value: float = Field(..., description="Giá trị kích thước quy đổi (m hoặc m2 hoặc số lượng)")
    unit_price: int = Field(..., description="Đơn giá bán / đơn vị áp dụng cho khách hàng (VND)")
    total_price: int = Field(..., description="Thành tiền bán cho khách hàng đã làm tròn về số nguyên (VND)")
    price_source: str = Field(
        ...,
        description="Nguồn gốc đơn giá: 'exact_material_match', 'category_default', 'default_unit_fallback'"
    )
    is_warning: bool = Field(default=False, description="Cờ cảnh báo nếu vật liệu hoặc danh mục lạ cần người dùng duyệt/sửa")
    warning_message: Optional[str] = Field(default=None, description="Chi tiết nội dung cảnh báo để hiển thị trên UI")
    cost_breakdown: Optional[CostBreakdown] = Field(
        default=None,
        description="Bóc tách giá vốn chi tiết (CHỈ hiển thị ở bảng tính riêng của chủ xưởng)"
    )


class QuotationResult(BaseModel):
    """
    Báo giá tổng hợp toàn bộ các hạng mục, tổng tiền bán, tổng giá vốn và tiền lợi nhuận gộp.
    """
    items: List[CalculatedItemQuote] = Field(default_factory=list, description="Danh sách báo giá chi tiết từng item")
    total_amount: int = Field(default=0, description="Tổng số tiền bán báo giá cho khách hàng (VND)")
    total_base_cost: int = Field(default=0, description="Tổng giá vốn gốc toàn bộ dự án (VND)")
    applied_profit_margin_percentage: float = Field(default=35.0, description="Tỷ lệ % lợi nhuận được áp dụng cho báo giá này")
    gross_profit_amount: int = Field(default=0, description="Tiền lợi nhuận gộp xưởng thu về = Total Amount - Total Base Cost (VND)")
    has_warnings: bool = Field(default=False, description="Đánh dấu báo giá có chứa hạng mục cần duyệt tay hay không")
    warning_count: int = Field(default=0, description="Số lượng hạng mục có cảnh báo cần kiểm tra")
