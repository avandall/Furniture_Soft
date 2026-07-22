import pytest
from app.domain.models import QuotedItem, CategoryPricing, WorkshopPricingConfig
from app.infrastructure.ai_services.vision_service import MockVisionService, GeminiVisionService


def test_mock_vision_service_default():
    config = WorkshopPricingConfig(workshop_id="ws_test")
    service = MockVisionService()
    items = service.extract_quoted_items("dummy_image_data", config)

    assert len(items) == 3
    assert items[0].category == "Tủ áo"
    assert items[1].category == "Tủ bếp dưới"
    assert items[2].category == "Giường ngủ"


def test_mock_vision_service_custom_items():
    custom = [
        QuotedItem(
            name="Vách ốp trang trí",
            length=3000,
            width=2800,
            wood_type="mdf_melamine",
            category="Vách ốp",
        )
    ]
    service = MockVisionService(mock_items=custom)
    config = WorkshopPricingConfig(workshop_id="ws_test")
    items = service.extract_quoted_items("dummy_image_data", config)

    assert len(items) == 1
    assert items[0].name == "Vách ốp trang trí"


def test_gemini_vision_service_missing_api_key_raises_error():
    config = WorkshopPricingConfig(workshop_id="ws_test")
    service = GeminiVisionService(api_key=None)
    
    # Không truyền API key -> Yêu cầu raise ValueError rõ ràng thay vì trả về dữ liệu giả hardcoded
    with pytest.raises(ValueError, match="Gemini API key chưa được cấu hình"):
        service.extract_quoted_items("dummy_image_data", config)
