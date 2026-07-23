import json
from pathlib import Path
from typing import Dict, Optional
from app.domain.models import CategoryPricing


DEFAULT_CONFIG_PATH = Path(__file__).parent / "preset_templates.json"


def load_preset_templates(config_path: Optional[str] = None) -> Dict[str, Dict]:
    """
    Nạp dữ liệu cấu hình các bảng giá mẫu Preset từ file JSON.
    Nếu không truyền `config_path`, nạp mặc định từ file `preset_templates.json`.
    """
    target_path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
    
    if not target_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file cấu hình preset pricing tại: {target_path}")

    with open(target_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Parse danh sách categories trong mỗi template sang danh sách các đối tượng CategoryPricing
    parsed_templates: Dict[str, Dict] = {}
    for key, template in data.items():
        categories = [
            CategoryPricing.model_validate(cat_data)
            for cat_data in template.get("categories", [])
        ]
        parsed_templates[key] = {
            "name": template.get("name", key),
            "default_profit_margin_percentage": template.get("default_profit_margin_percentage", 35.0),
            "categories": categories,
            "default_unit_prices": template.get("default_unit_prices", {}),
        }

    return parsed_templates
