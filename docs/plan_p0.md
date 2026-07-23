# Kế Hoạch Phát Triển Dự Án Quick-Quote AI (P0)

Tài liệu này chi tiết hóa kiến trúc, nguyên lý hoạt động, kế hoạch xây dựng và lộ trình triển khai module **Quick-Quote AI (P0)** - hệ thống báo giá nhanh dành cho chủ xưởng gỗ nội thất tại Việt Nam dựa trên thảo luận và thống nhất.

---

## 1. Tổng Quan & Luồng Nghiệp Vụ Tối Ưu

Để triệt tiêu các hạn chế về độ chính xác của AI và sự nhiễu loạn thông tin trên bản vẽ phối cảnh 3D/mặt bằng, hệ thống áp dụng luồng nghiệp vụ **"AI-assisted, Human-approved" (AI hỗ trợ, Con người phê duyệt)**:

```mermaid
graph TD
    A[Chủ xưởng tải ảnh phối cảnh 3D/PDF] --> B(FastAPI Backend)
    B -->|Bơm danh mục xưởng + Prompt| C(Vision LLM - Gemini 1.5 Flash)
    C -->|Trích xuất JSON Schema| D[Bảng kê khối lượng BOM thô trên UI Next.js]
    D -->|Chủ xưởng hiệu chỉnh kích thước/vật liệu nhanh| E(Rule Engine - Python)
    E -->|Tra cứu PostgreSQL JSONB| F[Tính giá tiền chính xác 100%]
    F --> G[Xuất PDF/Excel báo giá gửi Zalo cho khách]
```

### Tại sao quy trình này tối ưu?
*   **Tốc độ cực nhanh**: Thay vì mất 45 phút gõ tay Excel, chủ xưởng chỉ mất 30 giây để duyệt bảng BOM thô do AI tạo sẵn và xuất file báo giá.
*   **Chính xác tuyệt đối về số học**: AI chỉ bóc tách thực thể (đếm số lượng, ước lượng kích thước), việc tính tiền do code Python thuần đảm nhận.
*   **Tránh nhiễu**: Lọc bỏ các vật thể phụ (đèn trần, rèm cửa, thiết bị điện) không thuộc phạm vi sản xuất của xưởng.

---

## 2. Kiến Trúc & Thiết Kế Hệ Thống

### Tech Stack
*   **Backend Framework**: Python FastAPI (xử lý async bất đồng bộ).
*   **Database**: PostgreSQL (sử dụng trường `JSONB` để lưu cấu hình bảng giá động của từng xưởng).
*   **AI Layer**: Gemini 1.5 Flash API (ưu tiên số 1 vì chi phí rẻ, tốc độ cao, hỗ trợ tốt hình ảnh) kết hợp cấu hình mở rộng lên Claude 3.5 Sonnet / GPT-4o.
*   **Frontend**: Next.js + TailwindCSS + Shadcn/ui (thiết kế giao diện bảng Excel-like giúp chủ xưởng chỉnh sửa kích thước cực nhanh).

### Cơ chế Async tránh nghẽn I/O & HTTP Timeout
Thời gian phản hồi của Vision LLM khi xử lý ảnh dao động từ 5 - 15 giây. Hệ thống sẽ **không dùng** cơ chế Request-Response đồng bộ truyền thống.
1.  **Client gửi ảnh**: API tiếp nhận, đẩy file vào storage (AWS S3/MinIO), tạo một bản ghi Job trong PostgreSQL và trả về ngay mã trạng thái `202 Accepted` kèm `job_id`.
2.  **Xử lý ngầm (Background Task)**: Backend chạy tác vụ gọi LLM bóc tách ảnh và cập nhật kết quả vào Job.
3.  **Client kiểm tra (Polling/SSE)**: Frontend thực hiện gửi request check trạng thái Job mỗi 2 giây hoặc nhận cập nhật qua Server-Sent Events (SSE). Khi Job hoàn thành, UI tự động hiển thị bảng kết quả.

---

## 3. Thiết Kế AI Layer & Phòng Ngừa Sai Lệch

Để khắc phục việc AI không có kiến thức chuyên sâu ngành mộc (Domain Knowledge) và tránh nhiễu thông tin, chúng ta áp dụng các giải pháp kỹ thuật sau:

### A. Dynamic Prompt Context (Bơm cấu hình xưởng vào Prompt)
Trước khi gọi API LLM, hệ thống sẽ lấy danh sách danh mục sản phẩm mà xưởng đó làm được từ PostgreSQL (`PriceConfig`) và chèn vào prompt:
> *"Bạn là AI hỗ trợ bóc tách mộc. Xưởng này chỉ sản xuất các đồ nội thất gỗ sau: `[Tủ áo, Giường, Kệ tivi, Tủ bếp]`. Hãy bỏ qua tất cả thiết bị điện, đèn trần, rèm cửa, đồ decor trang trí. Nếu có hạng mục gỗ khác nằm ngoài danh sách, phân loại vào mục 'Khác' và cảnh báo."*

### B. Structured Outputs (Ép kiểu JSON Schema)
Sử dụng tính năng **Structured Outputs** của OpenAI/Gemini hoặc Claude Tool Use để ép mô hình trả về đúng định dạng JSON được định nghĩa qua Pydantic ở Backend. AI không được phép trả về chữ tự do (free-form text).

```python
class QuotedItem(BaseModel):
    name: str          # e.g., "Tủ quần áo kịch trần"
    length: float      # Kích thước dài (mm)
    width: float       # Kích thước rộng/cao (mm)
    depth: float       # Chiều sâu (mm)
    wood_type: str     # Cốt gỗ/bề mặt thô nhận diện được
    quantity: int = 1
    category: str      # Phân loại để map bảng giá
```

### C. Quy tắc mộc chuẩn Việt Nam (Carpentry Rules Prompting)
Dạy AI các kích thước tiêu chuẩn ngầm định trong Prompt để điền vào chỗ trống khi ảnh không hiển thị góc khuất:
*   Độ sâu mặc định của tủ áo, tủ bếp dưới là $600\text{mm}$.
*   Độ sâu tủ bếp trên mặc định là $350\text{mm}$.
*   Giường ngủ đôi mặc định kích thước $1800\text{mm} \times 2000\text{mm}$.
*   Mọi kích thước ước lượng phải làm tròn chia hết cho $50\text{mm}$ hoặc $100\text{mm}$.

---

## 4. Thiết Kế Rule Engine & Lưu Trữ PostgreSQL JSONB

### Thiết kế Cơ sở dữ liệu Bảng giá động
Mỗi xưởng gỗ có bảng giá vật tư hoàn toàn khác nhau. Chúng ta lưu trữ cấu hình này dưới dạng một trường `JSONB` trong bảng `workshop_pricing`:

```sql
CREATE TABLE workshop_pricing (
    id SERIAL PRIMARY KEY,
    workshop_id VARCHAR(50) NOT NULL UNIQUE,
    pricing_config JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Cấu trúc JSONB chuẩn:
```json
{
  "categories": [
    {
      "category": "Tủ áo",
      "unit": "m2",
      "prices": {
        "mdf_melamine": 2200000,
        "mdf_acrylic": 2800000
      },
      "keywords": ["tủ áo", "quần áo", "tủ đồ"]
    },
    {
      "category": "Tủ bếp dưới",
      "unit": "md",
      "prices": {
        "mdf_melamine": 2400000,
        "mdf_acrylic": 3200000
      },
      "keywords": ["tủ bếp dưới", "bếp dưới"]
    }
  ],
  "default_unit_prices": {
    "md": 2000000,
    "m2": 2200000,
    "cái": 3000000
  }
}
```

### Logic Tính Giá Bán & Giá Vốn của Rule Engine (Python thuần)
*   **Fuzzy Name Matching**: So khớp không phân biệt chữ hoa chữ thường và dựa trên bộ `keywords` để tự động map tên do AI bóc tách (e.g. *"Tủ quần áo cánh kính"*) vào nhóm danh mục của xưởng (e.g. *"Tủ áo"*).
*   **Phép tính theo đơn vị đo**:
    *   **Mét dài (`md`)**: $\text{Dài (m)} \times \text{Đơn giá} \times \text{Số lượng}$ (Dành cho tủ bếp, kệ trang trí dài).
    *   **Mét vuông (`m2`)**: $\text{Dài (m)} \times \text{Rộng (m)} \times \text{Đơn giá} \times \text{Số lượng}$ (Dành cho tủ quần áo, vách ốp đầu giường).
    *   **Cái/Bộ**: $\text{Đơn giá} \times \text{Số lượng}$ (Dành cho giường ngủ, bàn trang điểm, tab đầu giường).
*   **Bóc tách Giá Vốn Gốc & Biên Lợi Nhuận Xưởng (Owner Cost Breakdown)**:
    *   **Giá ván nhập gốc**: Tính toán số lượng tấm ván tiêu chuẩn ($1220 \times 2440\text{mm}$) ước tính $\times$ Đơn giá nhập 1 tấm ván của xưởng (kèm $15\%$ hao hụt).
    *   **Tiền công thợ**: Tùy chỉnh theo định mức $m^2/md$ hoặc xưởng tự gõ tay trực tiếp.
    *   **% Lợi nhuận xưởng (% Profit Margin)**: Xưởng có thể thiết lập % mặc định (e.g. $35\%$) hoặc điều chỉnh linh hoạt % lợi nhuận trực tiếp trên màn hình lúc ra báo giá.
    *   **Quy tắc bảo mật UI (Owner Privacy Mode)**: Bảng tính Giá Vốn và Lợi Nhuận Gộp chỉ hiển thị trong giao diện mở rộng dành riêng cho chủ xưởng (Owner Drawer/Tab). Giao diện gửi cho khách hàng CHỈ hiển thị Giá Bán Báo Giá công khai, tránh bị lộ giá vốn khi chủ xưởng ngồi cùng khách.
*   **Làm tròn tiền mặt**: Toàn bộ giá tiền làm tròn về số nguyên gần nhất (không sử dụng phần thập phân vì đơn vị tiền là VND).


---

## 5. Giải Pháp Onboarding Giảm Friction & Quy Tắc Hiển Thị UI

Chủ xưởng gỗ nhỏ không có sẵn bảng giá định hình tốt. Để giảm lực cản khi bắt đầu sử dụng và đảm bảo tính chính xác theo quy tắc nghiệp vụ:

1.  **Quy tắc Khởi tạo Bảng giá trên UI**:
    *   Khi xưởng mới chưa tạo bảng giá, UI báo giá mặc định hiển thị tổng tiền **0 VND**, các ô đơn giá để trống (`empty input`).
    *   UI hiển thị Banner / Dialog khuyến nghị: *"Bạn chưa có bảng giá. Hãy nhập trực tiếp hoặc chọn 1 trong 3 bảng giá mẫu dưới đây:"* kèm 3 nút chọn Preset:
        *   *Template Bình dân* (`binh_dan`): Ván chợ giá rẻ.
        *   *Template Phổ thông* (`pho_thong`): Ván phủ Melamine Thái Lan / Minh Long.
        *   *Template Cao cấp* (`cao_cap`): Ván MDF/HDF chống ẩm An Cường.
    *   Khi chủ xưởng bấm chọn 1 preset, UI gửi `POST /api/v1/workshops/{workshop_id}/pricing/preset?template_key=...` để nạp tự động dữ liệu mẫu vào các ô giá.

2. **Quy tắc Xử lý Cảnh báo Thiếu Giá (Unfilled Prices Handling)**:
    *   Hệ thống tuyệt đối **KHÔNG tự động điền giá mặc định** khi xưởng chưa thiết lập giá.
    *   Với các hạng mục có `is_warning = True` hoặc `unit_price = 0`, UI hiển thị viền đỏ / thẻ cảnh báo ("Chưa có đơn giá") để nhắc chủ xưởng gõ tay đơn giá trực tiếp trên bảng Excel-like trước khi xuất file PDF/Excel gửi khách hàng.

---

## 6. Lộ Trình Triển Khai Phát Triển (Lũy Tiến 4 Tuần)

### Tuần 1: Lõi tính toán (Domain & Rule Engine)
*   Định nghĩa thực thể Domain Model bằng Pydantic.
*   Lập trình Rule Engine tính giá m2, md, cái kèm logic so khớp chuỗi thông minh (Vietnamese fuzzy match).
*   Viết Unit Test kiểm thử tất cả các trường hợp làm tròn số, đảm bảo không fallback giá mặc định.

### Tuần 2: Tích hợp AI Layer (Vision LLM Integrations)
*   Xây dựng prompt tối ưu cho Gemini 1.5 Flash / GPT-4o.
*   Cấu hình cơ chế Structured Outputs đảm bảo dữ liệu thô trả về 100% khớp JSON Schema.
*   Lập trình cơ chế động: Lấy danh mục xưởng từ DB ghép vào System Prompt trước khi gọi AI.

### Tuần 3: Pipeline Xử lý Async & Database
*   Thiết kế bảng PostgreSQL lưu trữ bảng giá xưởng (`JSONB`) và lịch sử báo giá.
*   Viết API Endpoint nhận file, lưu trữ file lên cloud storage.
*   Triển khai cơ chế xử lý Job ngầm (FastAPI Background Tasks) và API Polling lấy trạng thái.

### Tuần 4: Giao Diện Frontend Next.js & Xuất Báo Giá
*   Phát triển UI kéo thả ảnh, màn hình chờ xử lý Job bất đồng bộ.
*   Xây dựng bảng Excel-like cho phép sửa trực tiếp số lượng, kích thước và đơn giá mộc do AI bóc tách.
*   Tích hợp UI chọn Preset pricing khi xưởng mới bắt đầu và hiển thị viền cảnh báo các ô giá bằng 0.
*   Tích hợp thư viện xuất báo giá PDF chuyên nghiệp gửi Zalo.
