from typing import List, Optional
from app.domain.models import QuotedItem, WorkshopPricingConfig, QuotationResult
from app.domain.rule_engine import QuotationRuleEngine


class RecalculateQuotationUseCase:
    """
    Use Case tính toán lại báo giá khi chủ xưởng chỉnh sửa thông tin kích thước,
    đơn giá hoặc số lượng trên bảng tính Excel-like giao diện UI.
    """

    def execute(
        self,
        items: List[QuotedItem],
        config: WorkshopPricingConfig,
        custom_profit_margin: Optional[float] = None,
        custom_labor_cost: Optional[int] = None,
    ) -> QuotationResult:
        rule_engine = QuotationRuleEngine(config)
        return rule_engine.calculate_quotation(
            items=items,
            custom_profit_margin=custom_profit_margin,
            custom_labor_cost=custom_labor_cost,
        )
