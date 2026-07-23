from typing import Optional, Dict
from app.domain.models import WorkshopPricingConfig
from app.infrastructure.repositories.pricing_repository import WorkshopPricingRepository
from app.config.preset_templates import load_preset_templates


class ManagePricingUseCase:
    """
    Use Case quản lý bảng giá xưởng & cung cấp các Mẫu Preset Onboarding (Bình dân, Phổ thông, Cao cấp).
    """

    def __init__(
        self,
        repo: WorkshopPricingRepository,
        preset_templates: Optional[Dict[str, Dict]] = None,
    ):
        self.repo = repo
        self.preset_templates = (
            preset_templates if preset_templates is not None else load_preset_templates()
        )

    def create_preset_pricing(self, workshop_id: str, template_key: str) -> WorkshopPricingConfig:
        """
        Tạo cấu hình bảng giá xưởng dựa trên mẫu Preset (binh_dan, pho_thong, cao_cap).
        Nếu template_key không hợp lệ hoặc rỗng, trả về cấu hình bảng giá rỗng (0 VND) mà không báo lỗi.
        """
        template = self.preset_templates.get(template_key)
        if not template:
            config = WorkshopPricingConfig(
                workshop_id=workshop_id,
                categories=[],
                default_profit_margin_percentage=0.0,
                default_unit_prices={},
            )
            return self.repo.save_pricing(config)

        config = WorkshopPricingConfig(
            workshop_id=workshop_id,
            categories=template["categories"],
            default_profit_margin_percentage=template["default_profit_margin_percentage"],
            default_unit_prices=template["default_unit_prices"],
        )
        return self.repo.save_pricing(config)

    def save_custom_pricing(self, config: WorkshopPricingConfig) -> WorkshopPricingConfig:
        """
        Lưu/Cập nhật bảng giá tự định nghĩa của xưởng.
        """
        return self.repo.save_pricing(config)

    def get_pricing(self, workshop_id: str) -> Optional[WorkshopPricingConfig]:
        """
        Lấy bảng giá xưởng.
        """
        return self.repo.get_pricing(workshop_id)
