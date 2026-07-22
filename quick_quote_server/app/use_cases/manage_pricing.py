from typing import Optional, Dict
from app.domain.models import WorkshopPricingConfig, CategoryPricing
from app.infrastructure.repositories.pricing_repository import WorkshopPricingRepository


class ManagePricingUseCase:
    """
    Use Case quản lý bảng giá xưởng & cung cấp các Mẫu Preset Onboarding (Bình dân, Phổ thông, Cao cấp).
    """

    PRESET_TEMPLATES: Dict[str, Dict] = {
        "binh_dan": {
            "name": "Bình dân (Ván chợ giá rẻ)",
            "default_profit_margin_percentage": 25.0,
            "categories": [
                CategoryPricing(
                    category="Tủ áo",
                    unit="m2",
                    prices={"mdf_melamine": 1800000},
                    board_sheet_price=280000,
                    labor_cost_per_unit=250000,
                    keywords=["tủ áo", "quần áo", "tủ đồ"],
                ),
                CategoryPricing(
                    category="Tủ bếp dưới",
                    unit="md",
                    prices={"mdf_melamine": 1900000},
                    board_sheet_price=280000,
                    labor_cost_per_unit=280000,
                    keywords=["tủ bếp dưới", "bếp dưới"],
                ),
                CategoryPricing(
                    category="Giường ngủ",
                    unit="cái",
                    prices={"mdf_melamine": 3500000},
                    board_sheet_price=280000,
                    labor_cost_per_unit=400000,
                    keywords=["giường", "giường ngủ"],
                ),
            ],
            "default_unit_prices": {"md": 1900000, "m2": 1800000, "cái": 3500000},
        },
        "pho_thong": {
            "name": "Phổ thông (Ván phủ Melamine Thái Lan / Minh Long)",
            "default_profit_margin_percentage": 35.0,
            "categories": [
                CategoryPricing(
                    category="Tủ áo",
                    unit="m2",
                    prices={"mdf_melamine": 2200000, "mdf_acrylic": 2800000},
                    board_sheet_price=350000,
                    labor_cost_per_unit=300000,
                    keywords=["tủ áo", "quần áo", "tủ đồ"],
                ),
                CategoryPricing(
                    category="Tủ bếp dưới",
                    unit="md",
                    prices={"mdf_melamine": 2400000, "mdf_acrylic": 3200000},
                    board_sheet_price=350000,
                    labor_cost_per_unit=350000,
                    keywords=["tủ bếp dưới", "bếp dưới"],
                ),
                CategoryPricing(
                    category="Giường ngủ",
                    unit="cái",
                    prices={"mdf_melamine": 5000000},
                    board_sheet_price=350000,
                    labor_cost_per_unit=500000,
                    keywords=["giường", "giường ngủ"],
                ),
            ],
            "default_unit_prices": {"md": 2400000, "m2": 2200000, "cái": 5000000},
        },
        "cao_cap": {
            "name": "Cao cấp (Ván MDF/HDF chống ẩm An Cường)",
            "default_profit_margin_percentage": 45.0,
            "categories": [
                CategoryPricing(
                    category="Tủ áo",
                    unit="m2",
                    prices={"mdf_melamine_an_cuong": 2600000, "mdf_acrylic_an_cuong": 3500000},
                    board_sheet_price=450000,
                    labor_cost_per_unit=400000,
                    keywords=["tủ áo", "quần áo", "tủ đồ"],
                ),
                CategoryPricing(
                    category="Tủ bếp dưới",
                    unit="md",
                    prices={"mdf_melamine_an_cuong": 2800000, "mdf_acrylic_an_cuong": 3900000},
                    board_sheet_price=450000,
                    labor_cost_per_unit=450000,
                    keywords=["tủ bếp dưới", "bếp dưới"],
                ),
                CategoryPricing(
                    category="Giường ngủ",
                    unit="cái",
                    prices={"mdf_melamine_an_cuong": 7000000},
                    board_sheet_price=450000,
                    labor_cost_per_unit=700000,
                    keywords=["giường", "giường ngủ"],
                ),
            ],
            "default_unit_prices": {"md": 2800000, "m2": 2600000, "cái": 7000000},
        },
    }

    def __init__(self, repo: WorkshopPricingRepository):
        self.repo = repo

    def create_preset_pricing(self, workshop_id: str, template_key: str) -> WorkshopPricingConfig:
        """
        Tạo cấu hình bảng giá xưởng dựa trên mẫu Preset (binh_dan, pho_thong, cao_cap).
        """
        template = self.PRESET_TEMPLATES.get(template_key)
        if not template:
            template = self.PRESET_TEMPLATES["pho_thong"]

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
