---
trigger: always_on
description: Quy tắc phát triển cho dự án Furniture Soft / Quick-Quote AI
---

# Quy tắc Phát triển Dự án Furniture Soft (Quick-Quote AI)

## 1. Tổng quan Dự án
- **Dự án**: Furniture Soft / Quick-Quote AI - Hệ thống bóc tách bản vẽ 3D/2D & lập bảng báo giá nhanh cho các xưởng mộc nội thất tại Việt Nam.
- **Mô hình**: "AI-assisted, Human-approved" (AI bóc tách danh mục thô, Python Rule Engine tính tiền chính xác 100%, chủ xưởng phê duyệt và xuất báo giá).

## 2. Quy tắc Nghiệp vụ Bắt buộc (Strict Business Rules)

### 🚫 KHÔNG DÙNG GIÁ MẶC ĐỊNH (No Default Price Fallback)
- **Quy tắc**: Khi xử lý tính giá (Rule Engine, Pricing Service, API, DTOs,...), **tuyệt đối KHÔNG viết code fallback về đơn giá mặc định** (ví dụ: `price = price or 2000000`, `.get("price", default_price)`, `price || DEFAULT_PRICE`, v.v.).
- **Nguyên nhân**: Mỗi xưởng gỗ và vật liệu có cấu hình bảng giá riêng. Khách hàng/Chủ xưởng phải tự nhập đơn giá hoặc tra cứu chính xác từ bảng giá xưởng (`workshop_pricing`). Giá mặc định không có ý nghĩa thực tế và sẽ gây sai lệch báo giá nghiêm trọng.
- **Cách xử lý chuẩn khi chưa có giá**:
  - Khi thiếu đơn giá, hệ thống phải gắn cờ báo thiếu giá (e.g., `price = None` hoặc status `PENDING_PRICE`), yêu cầu người dùng nhập trên giao diện (UI).
  - Trả về 0 nếu thực hiện lệnh tính tổng tiền khi đơn giá chưa được nhập.

### 🖥️ QUY TẮC HIỂN THỊ UI & GIAO DIỆN (Frontend Next.js Specification)
- **Khi xưởng chưa cài đặt bảng giá**:
  - Màn hình bảng tính báo giá hiển thị tổng tiền **0 VND**, các ô nhập đơn giá từng hạng mục bỏ trống (`empty input`).
  - Hiển thị Banner/Dialog hướng dẫn chọn 1 trong 3 bảng giá mẫu (`binh_dan`, `pho_thong`, `cao_cap`) hoặc tự nhập giá.
  - Khi chủ xưởng click chọn 1 Preset, gọi API `POST /api/v1/workshops/{workshop_id}/pricing/preset?template_key=...` để nạp tự động dữ liệu mẫu vào các ô giá trên UI.
- **Cảnh báo thiếu giá trên UI**:
  - Hạng mục nào có `is_warning = True` hoặc đơn giá = 0 VND sẽ được đánh dấu viền đỏ/thẻ cảnh báo ("Vui lòng nhập đơn giá") để chủ xưởng kiểm tra và gõ tay trực tiếp trên bảng tính Excel-like trước khi xuất PDF/Excel.