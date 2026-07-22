import pytest
from pydantic import ValidationError
from app.domain.models import (
    QuotedItem,
    CategoryPricing,
    WorkshopPricingConfig,
    CalculatedItemQuote,
    QuotationResult,
)


def test_quoted_item_defaults_and_validation():
    item = QuotedItem(
        name="Tủ quần áo 4 cánh",
        length=2000,
        width=2400,
        depth=600,
    )
    assert item.name == "Tủ quần áo 4 cánh"
    assert item.length == 2000
    assert item.width == 2400
    assert item.depth == 600
    assert item.wood_type == ""  # Mặc định để trống nếu khách chưa chọn
    assert item.quantity == 1
    assert item.category == "Khác"


def test_quoted_item_invalid_dimensions():
    with pytest.raises(ValidationError):
        QuotedItem(name="Test invalid", length=-100)


def test_workshop_pricing_config_defaults():
    cat = CategoryPricing(
        category="Tủ áo",
        unit="m2",
        prices={"mdf_melamine": 2200000, "mdf_acrylic": 2800000},
        keywords=["tủ áo", "quần áo", "tủ đồ"],
    )
    config = WorkshopPricingConfig(
        workshop_id="ws_001",
        categories=[cat],
        default_unit_prices={"m2": 2200000},
    )
    assert config.workshop_id == "ws_001"
    assert len(config.categories) == 1
    assert config.categories[0].unit == "m2"
    assert config.default_unit_prices["m2"] == 2200000
