from typing import Union, Optional
from app.domain.models import WorkshopPricingConfig, QuotationResult
from app.domain.rule_engine import QuotationRuleEngine
from app.infrastructure.ai_services.vision_service import BaseVisionService, MockVisionService


class ProcessQuotationUseCase:
    """
    Use Case xử lý luồng báo giá tự động cho Quick-Quote AI P0:
    Ảnh 3D/PDF -> Vision LLM Bóc tách BOM -> Rule Engine Tính tiền 100% & Bóc tách Giá Vốn / Lợi Nhuận Xưởng.
    """

    def __init__(self, vision_service: Optional[BaseVisionService] = None):
        # Nếu không truyền vision_service, sử dụng MockVisionService mặc định
        self.vision_service = vision_service or MockVisionService()

    def execute(
        self,
        image_data: Union[bytes, str],
        config: WorkshopPricingConfig,
        custom_profit_margin: Optional[float] = None,
        custom_labor_cost: Optional[int] = None,
    ) -> QuotationResult:
        """
        Thực thi luồng báo giá hoàn chỉnh.
        Cho phép chủ xưởng tùy chỉnh % Lợi nhuận (% Profit Margin) và Tiền công thợ trực tiếp trên UI lúc ra báo giá.
        """
        # Bước 1: Bóc tách danh sách QuotedItem thô từ Vision LLM
        extracted_items = self.vision_service.extract_quoted_items(image_data, config)

        # Bước 2: Đẩy qua Rule Engine để tính Giá bán cho khách & Giá vốn/Lợi nhuận gộp cho chủ xưởng
        rule_engine = QuotationRuleEngine(config)
        quotation_result = rule_engine.calculate_quotation(
            items=extracted_items,
            custom_profit_margin=custom_profit_margin,
            custom_labor_cost=custom_labor_cost,
        )

        return quotation_result
