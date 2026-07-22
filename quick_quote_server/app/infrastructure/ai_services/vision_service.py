import io
import json
from abc import ABC, abstractmethod
from typing import List, Union
from pydantic import TypeAdapter
from app.domain.models import QuotedItem, WorkshopPricingConfig
from app.infrastructure.ai_services.prompt_builder import DynamicPromptBuilder

try:
    import google.generativeai as genai
    from PIL import Image
    HAS_GENAI_SDK = True
except ImportError:
    HAS_GENAI_SDK = False


class BaseVisionService(ABC):
    """
    Interface trừu tượng cho các dịch vụ AI Vision LLM (Gemini 1.5 Flash, GPT-4o, Mock).
    """

    @abstractmethod
    def extract_quoted_items(
        self, image_data: Union[bytes, str], config: WorkshopPricingConfig
    ) -> List[QuotedItem]:
        """
        Bóc tách danh sách QuotedItem từ hình ảnh (Base64/URL/Bytes) và cấu hình xưởng.
        """
        pass


class MockVisionService(BaseVisionService):
    """
    Dịch vụ Mock Vision dùng để test offline, tích hợp CI/CD và phát triển không tốn API key.
    """

    def __init__(self, mock_items: List[QuotedItem] = None):
        self.mock_items = mock_items

    def extract_quoted_items(
        self, image_data: Union[bytes, str], config: WorkshopPricingConfig
    ) -> List[QuotedItem]:
        if self.mock_items is not None:
            return self.mock_items

        # Trả về kết quả mẫu thực tế nếu không truyền mock_items
        return [
            QuotedItem(
                name="Tủ quần áo 4 cánh kịch trần",
                length=2000,
                width=2400,
                depth=600,
                wood_type="mdf_melamine",
                quantity=1,
                category="Tủ áo",
            ),
            QuotedItem(
                name="Tủ bếp dưới phủ Acrylic",
                length=3000,
                width=0,
                depth=600,
                wood_type="mdf_acrylic",
                quantity=1,
                category="Tủ bếp dưới",
            ),
            QuotedItem(
                name="Giường ngủ đôi 1.8m",
                length=1800,
                width=2000,
                depth=400,
                wood_type="mdf_melamine",
                quantity=1,
                category="Giường ngủ",
            ),
        ]


class GeminiVisionService(BaseVisionService):
    """
    Dịch vụ tích hợp với Gemini 1.5 Flash API bằng Structured Output JSON Schema.
    ĐÂY CHÍNH LÀ NƠI GỌI AI THỰC TẾ ĐỂ BÓC TÁCH THỰC THỂ TỪ ẢNH.
    """

    def __init__(self, api_key: str = None):
        self.api_key = api_key

    def _prepare_image(self, image_data: Union[bytes, str]):
        """
        Chuyển đổi dữ liệu ảnh (Bytes hoặc File path) sang định dạng PIL Image cho Gemini SDK.
        """
        if isinstance(image_data, bytes):
            return Image.open(io.BytesIO(image_data))
        elif isinstance(image_data, str) and not image_data.startswith("http"):
            return Image.open(image_data)
        return image_data

    def extract_quoted_items(
        self, image_data: Union[bytes, str], config: WorkshopPricingConfig
    ) -> List[QuotedItem]:
        """
        Gửi Ảnh + System Prompt cá nhân hóa cho Gemini 1.5 Flash API
        và nhận về JSON Structured Output khớp 100% Pydantic Schema List[QuotedItem].
        """
        if not self.api_key:
            raise ValueError(
                "Gemini API key chưa được cấu hình. Vui lòng cung cấp api_key hoặc sử dụng MockVisionService khi testing/phát triển offline."
            )

        if not HAS_GENAI_SDK:
            raise ImportError(
                "Thư viện 'google-generativeai' chưa được cài đặt. Vui lòng chạy 'pip install google-generativeai pillow'."
            )

        # 1. Dựng System Prompt cá nhân hóa theo danh mục xưởng
        prompt = DynamicPromptBuilder.build_system_prompt(config)

        # 2. Chuẩn bị hình ảnh
        pil_image = self._prepare_image(image_data)

        # 3. Cấu hình Gemini SDK & Model Gemini 1.5 Flash
        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        # 4. Gọi Gemini API với Structured Output JSON Schema
        response = model.generate_content(
            contents=[pil_image, prompt],
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=List[QuotedItem],
                temperature=0.1,  # Đặt nhiệt độ thấp để AI bóc tách chính xác không sáng tạo lung tung
            ),
        )

        # 5. Parse dữ liệu JSON từ Gemini thành danh sách Pydantic QuotedItem
        adapter = TypeAdapter(List[QuotedItem])
        quoted_items = adapter.validate_json(response.text)

        return quoted_items
