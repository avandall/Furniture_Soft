import os
import sys
import pytest

sys.path.insert(0, os.path.abspath("quick_quote_server"))

from app.domain.models import QuotedItem, WorkshopPricingConfig, CategoryPricing
from app.use_cases.recalculate_quotation import RecalculateQuotationUseCase
from app.infrastructure.export.export_service import QuotationExportService


def test_recalculate_quotation_use_case():
    config = WorkshopPricingConfig(
        workshop_id="ws_recalc",
        categories=[
            CategoryPricing(
                category="Tủ áo",
                unit="m2",
                prices={"mdf_melamine": 2000000},
                keywords=["tủ áo"]
            )
        ]
    )

    items = [
        QuotedItem(
            name="Tủ áo kịch trần",
            length=2000,
            width=2000,
            wood_type="mdf_melamine",
            quantity=1,
            category="Tủ áo"
        )
    ]

    use_case = RecalculateQuotationUseCase()
    result = use_case.execute(items=items, config=config)

    assert len(result.items) == 1
    # 2.0m x 2.0m = 4.0 m2 @ 2,000,000 = 8,000,000 VND
    assert result.total_amount == 8000000


def test_quotation_export_service():
    config = WorkshopPricingConfig(
        workshop_id="ws_export",
        categories=[
            CategoryPricing(category="Giường ngủ", unit="cái", prices={"mdf_melamine": 5000000})
        ]
    )

    items = [
        QuotedItem(name="Giường ngủ đôi", length=2000, width=1800, wood_type="mdf_melamine", quantity=1, category="Giường ngủ")
    ]

    recalc = RecalculateQuotationUseCase()
    quotation = recalc.execute(items=items, config=config)

    export_service = QuotationExportService()
    html_report = export_service.generate_html_report(quotation, "Xưởng Mộc Nam Việt")
    assert "Xưởng Mộc Nam Việt" in html_report
    assert "Giường ngủ đôi" in html_report
    assert "5,000,000 VNĐ" in html_report

    zalo_text = export_service.generate_zalo_summary(quotation, "Xưởng Mộc Nam Việt")
    assert "BẢNG BÁO GIÁ NỘI THẤT" in zalo_text
    assert "Giường ngủ đôi" in zalo_text
    assert "5,000,000 VNĐ" in zalo_text
