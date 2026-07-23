import os
import sys
import pytest

sys.path.insert(0, os.path.abspath("quick_quote_server"))

from app.config.preset_templates import load_preset_templates
from app.use_cases.manage_pricing import ManagePricingUseCase
from app.infrastructure.repositories.pricing_repository import WorkshopPricingRepository


def test_load_preset_templates():
    templates = load_preset_templates()
    assert "binh_dan" in templates
    assert "pho_thong" in templates
    assert "cao_cap" in templates

    pho_thong = templates["pho_thong"]
    assert len(pho_thong["categories"]) == 3
    assert pho_thong["default_profit_margin_percentage"] == 35.0


def test_create_preset_pricing_success(db_session):
    repo = WorkshopPricingRepository(db_session)
    use_case = ManagePricingUseCase(repo)

    config = use_case.create_preset_pricing("ws_preset_test", "binh_dan")
    assert config is not None
    assert config.workshop_id == "ws_preset_test"
    assert config.default_profit_margin_percentage == 25.0
    assert len(config.categories) == 3


def test_create_preset_pricing_invalid_key_returns_empty_config(db_session):
    repo = WorkshopPricingRepository(db_session)
    use_case = ManagePricingUseCase(repo)

    config = use_case.create_preset_pricing("ws_invalid_test", "invalid_key")
    assert config is not None
    assert config.workshop_id == "ws_invalid_test"
    assert len(config.categories) == 0
    assert config.default_profit_margin_percentage == 0.0
