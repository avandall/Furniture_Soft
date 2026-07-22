from typing import List
from app.domain.models import WorkshopPricingConfig


class DynamicPromptBuilder:
    """
    Xây dựng Prompt động bơm danh mục xưởng và các Quy tắc mộc chuẩn Việt Nam
    cho Vision LLM (Gemini / OpenAI).
    """

    CARPENTRY_RULES_VIETNAM = """
QUY TẮC MỘC TIÊU CHUẨN VIỆT NAM (DÙNG ĐỂ ƯỚC LƯỢNG KHI ẢNH KHÔNG HIỂN THỊ GÓC KHUẤT):
1. Chiều sâu (depth) mặc định của Tủ quần áo và Tủ bếp dưới là 600mm.
2. Chiều sâu (depth) mặc định của Tủ bếp trên là 350mm.
3. Kích thước mặc định của Giường ngủ đôi là 1800mm (dài/rộng) x 2000mm.
4. Mọi kích thước chiều dài, chiều rộng, chiều sâu ước lượng phải được làm tròn chia hết cho 50mm hoặc 100mm (ví dụ: 1800, 2400, 2500).
5. KHÔNG bóc tách các thiết bị điện, đèn trần, rèm cửa, đồ decor trang trí, chậu cây.
6. Chỉ tập trung bóc tách các đồ nội thất mộc (tủ, giường, bàn, kệ, vách ốp).
7. Nếu có đồ mộc không nằm trong danh sách danh mục xưởng, hãy đặt category là "Khác".
"""

    @classmethod
    def build_system_prompt(cls, config: WorkshopPricingConfig) -> str:
        """
        Tạo system prompt cá nhân hóa theo cấu hình danh mục của từng xưởng.
        """
        allowed_categories: List[str] = [cat.category for cat in config.categories]
        if allowed_categories:
            categories_str = ", ".join(f"'{cat}'" for cat in allowed_categories)
            category_instruction = f"DANH MỤC SẢN PHẨM XƯỞNG NÀY CHỈ ĐỊNH:\n[{categories_str}]\nHãy ưu tiên chọn 1 danh mục khớp nhất trong danh sách ở trên. Nếu đồ mộc nằm ngoài danh sách, đặt category là 'Khác'."
        else:
            category_instruction = "DANH MỤC SẢN PHẨM: Xưởng chưa giới hạn danh mục. Hãy tự do nhận diện phân loại mộc thực tế trong ảnh (e.g. 'Tủ áo', 'Tủ bếp', 'Giường ngủ', 'Kệ tivi', 'Bàn làm việc', 'Vách ốp')."

        prompt = f"""Bạn là chuyên gia AI hỗ trợ bóc tách mộc nội thất tại Việt Nam từ hình ảnh phối cảnh 3D hoặc bản vẽ thiết kế.

{category_instruction}


{cls.CARPENTRY_RULES_VIETNAM}

NHIỆM VỤ CỦA BẠN:
1. Phân tích hình ảnh được cung cấp.
2. Nhận diện danh sách tất cả các thực thể nội thất mộc có trong ảnh.
3. Với mỗi thực thể, xác định:
   - name: Tên mô tả ngắn gọn (e.g. "Tủ quần áo 4 cánh kịch trần")
   - length: Kích thước dài/cao chính (mm)
   - width: Kích thước rộng/ngang (mm, mặc định 0 nếu không áp dụng)
   - depth: Kích thước chiều sâu (mm, tuân theo quy tắc mộc)
   - wood_type: Loại ván mộc nhận diện được (e.g. "mdf_melamine", "mdf_acrylic", "plywood")
   - quantity: Số lượng thực thể (mặc định 1)
   - category: Chọn 1 danh mục khớp nhất trong danh sách danh mục xưởng ở trên.

YÊU CẦU ĐỊNH DẠNG:
Trả về duy nhất danh sách JSON tuân thủ đúng định dạng JSON Schema của Pydantic QuotedItem. Không trả về văn bản tự do ngoài JSON.
"""
        return prompt.strip()
