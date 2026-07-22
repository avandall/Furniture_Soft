import pytest
from app.domain.models import (
    QuotedItem,
    CategoryPricing,
    WorkshopPricingConfig,
)
from app.domain.rule_engine import QuotationRuleEngine, remove_vietnamese_accents


@pytest.fixture
def workshop_config():
    return WorkshopPricingConfig(
        workshop_id="workshop_demo",
        default_profit_margin_percentage=35.0,
        categories=[
            CategoryPricing(
                category="Tủ áo",
                unit="m2",
                prices={
                    "mdf_melamine": 2200000,
                    "mdf_acrylic": 2800000,
                },
                board_sheet_price=350000,
                labor_cost_per_unit=300000,
                keywords=["tủ áo", "quần áo", "tủ đồ"],
            ),
            CategoryPricing(
                category="Tủ bếp dưới",
                unit="md",
                prices={
                    "mdf_melamine": 2400000,
                    "mdf_acrylic": 3200000,
                },
                board_sheet_price=400000,
                labor_cost_per_unit=350000,
                keywords=["tủ bếp dưới", "bếp dưới"],
            ),
            CategoryPricing(
                category="Giường ngủ",
                unit="cái",
                prices={
                    "mdf_melamine": 5000000,
                },
                board_sheet_price=350000,
                labor_cost_per_unit=500000,
                keywords=["giường", "giường ngủ"],
            ),
        ],
        default_unit_prices={
            "md": 2000000,
            "m2": 2200000,
            "cái": 3000000,
        },
    )


def test_remove_vietnamese_accents():
    raw_text = "Tủ quần áo cánh kính 1800x2000mm"
    normalized = remove_vietnamese_accents(raw_text)
    assert normalized == "tu quan ao canh kinh 1800x2000mm"


def test_calculate_m2_tu_ao(workshop_config):
    engine = QuotationRuleEngine(workshop_config)
    item = QuotedItem(
        name="Tủ quần áo kịch trần 4 cánh",
        length=2000,  # 2.0 m
        width=2400,   # 2.4 m
        depth=600,
        wood_type="mdf_melamine",
        quantity=1,
        category="Tủ áo",
    )

    quote = engine.calculate_item_quote(item)
    assert quote.matched_category == "Tủ áo"
    assert quote.unit == "m2"
    assert quote.dimension_value == 4.8  # 2.0 * 2.4
    assert quote.unit_price == 2200000
    assert quote.total_price == 10560000  # 4.8 * 2,200,000
    assert quote.price_source == "exact_material_match"
    assert quote.is_warning is False
    assert quote.warning_message is None

    # Kiểm tra Giá vốn chi tiết (Cost Breakdown)
    assert quote.cost_breakdown is not None
    assert quote.cost_breakdown.board_sheets_estimated > 0
    assert quote.cost_breakdown.total_base_cost > 0


def test_cost_breakdown_and_profit_margin(workshop_config):
    engine = QuotationRuleEngine(workshop_config)
    items = [
        QuotedItem(
            name="Tủ áo 4 cánh",
            length=2000,
            width=2400,
            wood_type="mdf_melamine",
            category="Tủ áo",
        ),
    ]

    result = engine.calculate_quotation(items)
    assert result.total_amount == 10560000
    assert result.total_base_cost > 0
    assert result.gross_profit_amount == result.total_amount - result.total_base_cost
    assert result.applied_profit_margin_percentage == 35.0


def test_custom_profit_margin_override(workshop_config):
    engine = QuotationRuleEngine(workshop_config)
    items = [
        QuotedItem(
            name="Tủ bếp dưới",
            length=3000,
            wood_type="mdf_acrylic",
            category="Tủ bếp dưới",
        ),
    ]

    # Chủ xưởng chỉnh % lợi nhuận lên 40% trên UI
    result = engine.calculate_quotation(items, custom_profit_margin=40.0)
    assert result.applied_profit_margin_percentage == 40.0
    assert result.gross_profit_amount == result.total_amount - result.total_base_cost


def test_warning_on_unknown_wood_type(workshop_config):
    engine = QuotationRuleEngine(workshop_config)
    item = QuotedItem(
        name="Tủ quần áo ván siêu chống ẩm",
        length=2000,
        width=2000,
        wood_type="gỗ_tự_nhiên_xoan_đào",
        quantity=1,
        category="Tủ áo",
    )

    quote = engine.calculate_item_quote(item)
    assert quote.matched_category == "Tủ áo"
    assert quote.is_warning is True
    assert quote.warning_message is not None
    assert "gỗ_tự_nhiên_xoan_đào" in quote.warning_message


def test_warning_on_unmatched_category(workshop_config):
    engine = QuotationRuleEngine(workshop_config)
    item = QuotedItem(
        name="Kệ ti vi treo tường độc lạ",
        length=1500,
        wood_type="unknown",
        quantity=1,
        category="Kệ trang trí",
    )

    quote = engine.calculate_item_quote(item)
    assert quote.matched_category == "Không xác định"
    assert quote.is_warning is True
    assert quote.warning_message is not None
    assert quote.unit == "md"


def test_warning_on_missing_width_for_m2(workshop_config):
    engine = QuotationRuleEngine(workshop_config)
    item = QuotedItem(
        name="Tủ áo thiếu chiều cao/rộng",
        length=2000,
        width=0,  # width = 0
        wood_type="mdf_melamine",
        category="Tủ áo",
    )

    quote = engine.calculate_item_quote(item)
    assert quote.is_warning is True
    assert quote.warning_message is not None
    assert "thiếu kích thước chiều rộng/cao" in quote.warning_message
