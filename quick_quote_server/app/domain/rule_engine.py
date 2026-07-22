import re
from typing import Tuple, Optional, List
from app.domain.models import (
    QuotedItem,
    CategoryPricing,
    WorkshopPricingConfig,
    CalculatedItemQuote,
    CostBreakdown,
    QuotationResult,
)


def remove_vietnamese_accents(text: str) -> str:
    """
    Hàm bỏ dấu tiếng Việt phục vụ so khớp chuỗi không phân biệt chữ hoa/thường và dấu.
    """
    text = text.lower()
    patterns = {
        '[àáảãạăằắẳẵặâầấẩẫậ]': 'a',
        '[đ]': 'd',
        '[èéẻẽẹêềếểễệ]': 'e',
        '[ìíỉĩị]': 'i',
        '[òóỏõọôồốổỗộơờớởỡợ]': 'o',
        '[ùúủũụưừứửữự]': 'u',
        '[ỳýỷỹỵ]': 'y',
    }
    for pattern, replace in patterns.items():
        text = re.sub(pattern, replace, text)
    return text.strip()


class QuotationRuleEngine:
    """
    Rule Engine tính giá mộc m2, md, cái/bộ kèm Bóc tách Giá Vốn Gốc & Biên Lợi Nhuận cho chủ xưởng.
    Bảo đảm tính toán số học chính xác 100%, không tự tiện gán giá giả định (Nếu xưởng chưa nhập giá -> Cost sum = 0).
    """

    STANDARD_SHEET_AREA_M2 = 2.9768  # Kích thước 1 tấm ván mộc tiêu chuẩn 1220mm x 2440mm
    WASTE_COEFFICIENT = 1.15  # 15% hệ số hao hụt cắt ván (Nesting waste)

    def __init__(self, config: WorkshopPricingConfig):
        self.config = config

    def normalize_string(self, text: str) -> str:
        """Thường hóa chuỗi văn bản và loại bỏ dấu tiếng Việt."""
        return remove_vietnamese_accents(text)

    def match_category(self, item: QuotedItem) -> Optional[CategoryPricing]:
        """
        So khớp tự động (Fuzzy Matching) tên hoặc phân loại của item mộc
        với danh mục bài viết trong cấu hình của xưởng.
        """
        norm_item_category = self.normalize_string(item.category)
        norm_item_name = self.normalize_string(item.name)

        # 1. So khớp chính xác tên phân loại
        for cat in self.config.categories:
            norm_cat_name = self.normalize_string(cat.category)
            if norm_item_category == norm_cat_name or norm_item_name == norm_cat_name:
                return cat

        # 2. So khớp từ khóa (keywords) trong danh mục xưởng
        for cat in self.config.categories:
            for kw in cat.keywords:
                norm_kw = self.normalize_string(kw)
                if norm_kw and (norm_kw in norm_item_name or norm_kw in norm_item_category):
                    return cat

        return None

    def calculate_dimension(self, item: QuotedItem, unit: str) -> Tuple[float, bool, Optional[str]]:
        """
        Tính toán kích thước mộc theo đơn vị đo:
        - Mét dài (md): Dài (m)
        - Mét vuông (m2): Dài (m) x Rộng (m). Nếu Rộng = 0 -> Cảnh báo thiếu kích thước.
        - Cái/Bộ: 1.0 (Số lượng nhân riêng ở bước sau)
        """
        length_m = item.length / 1000.0
        width_m = item.width / 1000.0

        if unit == "md":
            return round(length_m, 4), False, None
        elif unit == "m2":
            if width_m <= 0:
                return round(length_m, 4), True, f"Cảnh báo: Hạng mục '{item.name}' tính theo m2 nhưng thiếu kích thước chiều rộng/cao. Vui lòng bổ sung."
            return round(length_m * width_m, 4), False, None
        else:  # cái, bộ
            return 1.0, False, None

    def calculate_cost_breakdown(
        self,
        item: QuotedItem,
        unit: str,
        dimension_val: float,
        matched_cat: Optional[CategoryPricing],
        custom_labor_cost: Optional[int] = None,
    ) -> CostBreakdown:
        """
        Tính toán giá vốn gốc (COGS) cho chủ xưởng:
        Nếu xưởng chưa thiết lập đơn giá ván hay công thợ -> Tổng giá vốn (total_base_cost) = 0.
        """
        sheet_price = matched_cat.board_sheet_price if matched_cat else 0
        labor_rate = matched_cat.labor_cost_per_unit if matched_cat else 0

        # Ước tính diện tích m2 ván sử dụng
        length_m = item.length / 1000.0
        width_m = item.width / 1000.0 if item.width > 0 else (0.6 if unit == "md" else 1.0)
        estimated_area_m2 = (length_m * width_m) * item.quantity

        # Số tấm ván mộc ước tính
        sheets_needed = (estimated_area_m2 / self.STANDARD_SHEET_AREA_M2) * self.WASTE_COEFFICIENT
        board_sheets_estimated = round(sheets_needed, 2)

        # 1. Tiền mua ván mộc gốc (nếu xưởng chưa nhập giá ván -> = 0)
        board_material_cost = int(round(board_sheets_estimated * sheet_price)) if sheet_price > 0 else 0

        # 2. Tiền công thợ sản xuất / lắp ráp (nếu chưa có giá công thợ -> = 0)
        if custom_labor_cost is not None:
            labor_cost = custom_labor_cost
        elif labor_rate > 0:
            if unit in ("m2", "md"):
                labor_cost = int(round(dimension_val * labor_rate * item.quantity))
            else:
                labor_cost = int(round(labor_rate * item.quantity))
        else:
            labor_cost = 0

        # 3. Tiền phụ kiện & vật tư phụ ước tính (chỉ tính 15% trên ván nếu có giá ván)
        hardware_cost = int(round(board_material_cost * 0.15)) if board_material_cost > 0 else 0

        # 4. Tổng giá vốn gốc (nếu xưởng chưa nhập dữ liệu -> sum = 0)
        total_base_cost = board_material_cost + labor_cost + hardware_cost

        return CostBreakdown(
            board_sheets_estimated=board_sheets_estimated,
            board_material_cost=board_material_cost,
            labor_cost=labor_cost,
            hardware_cost=hardware_cost,
            total_base_cost=total_base_cost,
        )

    def resolve_unit_price(
        self, item: QuotedItem, matched_cat: Optional[CategoryPricing]
    ) -> Tuple[str, int, str, bool, Optional[str]]:
        """
        Xác định đơn vị đo, đơn giá bán cho khách hàng, nguồn giá và CỜ CẢNH BÁO.
        """
        norm_wood = item.wood_type.lower().strip()

        if matched_cat:
            unit = matched_cat.unit
            # Match đơn giá bán theo loại gỗ chính xác
            if norm_wood and norm_wood in matched_cat.prices:
                return unit, matched_cat.prices[norm_wood], "exact_material_match", False, None

            # Tìm match tương đối trong bảng giá (e.g. "mdf" trong "mdf_melamine")
            if norm_wood:
                for mat_key, price in matched_cat.prices.items():
                    if mat_key in norm_wood or norm_wood in mat_key:
                        return unit, price, "exact_material_match", False, None

            # CẢNH BÁO: Tìm thấy danh mục nhưng loại ván chưa có giá hoặc chưa chọn ván
            if matched_cat.prices:
                first_price = next(iter(matched_cat.prices.values()))
                wood_msg = f" '{item.wood_type}'" if item.wood_type else ""
                msg = f"Cảnh báo: Loại ván{wood_msg} chưa có bảng giá trong danh mục '{matched_cat.category}'. Đã tạm lấy đơn giá bán {first_price:,} đ/{unit}, vui lòng kiểm tra lại."
                return unit, first_price, "category_default", True, msg

            # CẢNH BÁO: Danh mục chưa thiết lập giá bán
            fallback_price = self.config.default_unit_prices.get(unit, 0)
            if fallback_price > 0:
                msg = f"Cảnh báo: Danh mục '{matched_cat.category}' chưa có bảng giá bán. Đã lấy giá dự phòng đơn vị {fallback_price:,} đ/{unit}."
                return unit, fallback_price, "default_unit_fallback", True, msg

            msg = f"Cảnh báo: Danh mục '{matched_cat.category}' chưa được cấu hình đơn giá bán. Vui lòng nhập giá thủ công."
            return unit, 0, "default_unit_fallback", True, msg

        # CẢNH BÁO: Không match được danh mục nào
        norm_name = self.normalize_string(item.name)
        if any(k in norm_name for k in ["bep", "ke", "phao"]):
            inferred_unit = "md"
        elif any(k in norm_name for k in ["ao", "vach", "op", "tu"]):
            inferred_unit = "m2"
        else:
            inferred_unit = "cái"

        default_price = self.config.default_unit_prices.get(inferred_unit, 0)
        if default_price > 0:
            msg = f"Cảnh báo: Hạng mục '{item.name}' không khớp với danh mục nào của xưởng. Đã áp dụng giá dự phòng đơn vị {default_price:,} đ/{inferred_unit}."
            return inferred_unit, default_price, "default_unit_fallback", True, msg

        msg = f"Cảnh báo: Hạng mục '{item.name}' không khớp với danh mục nào và chưa có giá dự phòng. Vui lòng nhập giá thủ công."
        return inferred_unit, 0, "default_unit_fallback", True, msg

    def calculate_item_quote(
        self,
        item: QuotedItem,
        custom_profit_margin: Optional[float] = None,
        custom_labor_cost: Optional[int] = None,
    ) -> CalculatedItemQuote:
        """
        Tính giá bán cho khách hàng & Bóc tách giá vốn chi tiết cho chủ xưởng.
        """
        matched_cat = self.match_category(item)
        matched_cat_name = matched_cat.category if matched_cat else "Không xác định"

        unit, unit_price, price_source, price_warning, price_warn_msg = self.resolve_unit_price(item, matched_cat)
        dimension_val, dim_warning, dim_warn_msg = self.calculate_dimension(item, unit)

        # 1. Tính giá vốn chi tiết (Cost Breakdown)
        cost_breakdown = self.calculate_cost_breakdown(
            item=item,
            unit=unit,
            dimension_val=dimension_val,
            matched_cat=matched_cat,
            custom_labor_cost=custom_labor_cost,
        )

        # 2. Nếu đơn giá bán bị 0 (danh mục lạ), tự động tính giá bán theo % Lợi nhuận từ Giá vốn (nếu có giá vốn)
        profit_margin_pct = custom_profit_margin if custom_profit_margin is not None else self.config.default_profit_margin_percentage
        if unit_price == 0 and cost_breakdown.total_base_cost > 0 and profit_margin_pct > 0:
            calculated_selling_total = int(round(cost_breakdown.total_base_cost * (1 + profit_margin_pct / 100)))
            unit_price = int(round(calculated_selling_total / (dimension_val * item.quantity))) if dimension_val > 0 else calculated_selling_total

        # Tổng hợp cảnh báo nếu thiếu chiều rộng hoặc sai vật liệu/danh mục
        is_warning = price_warning or dim_warning
        messages = [m for m in [price_warn_msg, dim_warn_msg] if m]
        warning_msg = " | ".join(messages) if messages else None

        # Tính tổng tiền bán cho item: Kích thước x Đơn giá x Số lượng
        raw_total = dimension_val * unit_price * item.quantity
        total_price_vnd = int(round(raw_total))

        return CalculatedItemQuote(
            quoted_item=item,
            matched_category=matched_cat_name,
            unit=unit,
            dimension_value=dimension_val,
            unit_price=unit_price,
            total_price=total_price_vnd,
            price_source=price_source,
            is_warning=is_warning,
            warning_message=warning_msg,
            cost_breakdown=cost_breakdown,
        )

    def calculate_quotation(
        self,
        items: List[QuotedItem],
        custom_profit_margin: Optional[float] = None,
        custom_labor_cost: Optional[int] = None,
    ) -> QuotationResult:
        """
        Tính giá toàn bộ dự án: Tổng tiền bán cho khách, Tổng giá vốn & Tiền lợi nhuận gộp xưởng.
        """
        calculated_items = []
        total_amount = 0
        total_base_cost = 0
        warning_count = 0

        applied_margin = custom_profit_margin if custom_profit_margin is not None else self.config.default_profit_margin_percentage

        for item in items:
            quote = self.calculate_item_quote(
                item=item,
                custom_profit_margin=applied_margin,
                custom_labor_cost=custom_labor_cost,
            )
            calculated_items.append(quote)
            total_amount += quote.total_price
            if quote.cost_breakdown:
                total_base_cost += quote.cost_breakdown.total_base_cost
            if quote.is_warning:
                warning_count += 1

        gross_profit_amount = total_amount - total_base_cost

        return QuotationResult(
            items=calculated_items,
            total_amount=total_amount,
            total_base_cost=total_base_cost,
            applied_profit_margin_percentage=applied_margin,
            gross_profit_amount=gross_profit_amount,
            has_warnings=(warning_count > 0),
            warning_count=warning_count,
        )
