from app.domain.models import CategoryPricing, WorkshopPricingConfig
from app.infrastructure.ai_services.prompt_builder import DynamicPromptBuilder


def test_build_system_prompt():
    config = WorkshopPricingConfig(
        workshop_id="ws_test",
        categories=[
            CategoryPricing(category="Tủ áo", unit="m2", prices={"mdf_melamine": 2200000}),
            CategoryPricing(category="Tủ bếp dưới", unit="md", prices={"mdf_acrylic": 3200000}),
        ],
    )

    prompt = DynamicPromptBuilder.build_system_prompt(config)

    # Kiểm tra prompt có chứa danh mục xưởng
    assert "'Tủ áo'" in prompt
    assert "'Tủ bếp dưới'" in prompt

    # Kiểm tra prompt có chứa các quy tắc mộc Việt Nam
    assert "Chi tiết chiều sâu (depth) mặc định" in prompt or "600mm" in prompt
    assert "350mm" in prompt
    assert "1800mm" in prompt
    assert "JSON Schema" in prompt
