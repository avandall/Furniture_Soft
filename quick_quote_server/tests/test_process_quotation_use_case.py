from app.domain.models import (
    QuotedItem,
    CategoryPricing,
    WorkshopPricingConfig,
)
from app.infrastructure.ai_services.vision_service import MockVisionService
from app.use_cases.process_quotation import ProcessQuotationUseCase


def test_process_quotation_use_case_success():
    config = WorkshopPricingConfig(
        workshop_id="ws_demo",
        categories=[
            CategoryPricing(
                category="Tủ áo",
                unit="m2",
                prices={"mdf_melamine": 2200000},
                keywords=["tủ áo"],
            ),
            CategoryPricing(
                category="Tủ bếp dưới",
                unit="md",
                prices={"mdf_acrylic": 3200000},
                keywords=["tủ bếp dưới"],
            ),
            CategoryPricing(
                category="Giường ngủ",
                unit="cái",
                prices={"mdf_melamine": 5000000},
                keywords=["giường"],
            ),
        ],
    )

    # Sử dụng MockVisionService trả về 3 item chuẩn
    vision_service = MockVisionService()
    use_case = ProcessQuotationUseCase(vision_service=vision_service)

    result = use_case.execute("dummy_image_data_or_base64", config)

    assert len(result.items) == 3
    # Item 1: Tủ áo 2.0m x 2.4m @ 2,200,000 = 10,560,000 VND
    # Item 2: Tủ bếp 3.0m @ 3,200,000 = 9,600,000 VND
    # Item 3: Giường ngủ 1 cái @ 5,000,000 = 5,000,000 VND
    # Total: 25,160,000 VND
    assert result.total_amount == 25160000
    assert result.has_warnings is False
    assert result.warning_count == 0


def test_process_quotation_use_case_with_warnings():
    config = WorkshopPricingConfig(
        workshop_id="ws_demo",
        categories=[
            CategoryPricing(
                category="Tủ áo",
                unit="m2",
                prices={"mdf_melamine": 2200000},
            )
        ],
    )

    # Dữ liệu từ Vision LLM có 1 item gỗ lạ không có trong bảng giá
    mock_items = [
        QuotedItem(
            name="Tủ áo ván xoan đào",
            length=2000,
            width=2000,
            wood_type="gỗ_xoan_đào",
            category="Tủ áo",
        )
    ]
    vision_service = MockVisionService(mock_items=mock_items)
    use_case = ProcessQuotationUseCase(vision_service=vision_service)

    result = use_case.execute("dummy_image", config)

    assert len(result.items) == 1
    assert result.has_warnings is True
    assert result.warning_count == 1
    assert result.items[0].is_warning is True
    assert "gỗ_xoan_đào" in result.items[0].warning_message
