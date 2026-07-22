# BÁO CÁO KẾ HOẠCH TÀI CHÍNH & MÔ HÌNH KINH DOANH (P0 -> P3)

**Kính gửi:** Ban Lãnh Đạo / Quản Lý Dự Án  
**Người lập:** Đội ngũ Kỹ thuật & Phát triển Sản phẩm  
**Ngày báo cáo:** 22/07/2026  
**Cập nhật:** Tối ưu hóa giá bán bình dân (SME Sweet-Spot Pricing) để triệt tiêu rào cản mua hàng.

---

## TỔNG QUAN HỆ SINH THÁI SẢN PHẨM

Bộ giải pháp phần mềm dành cho các xưởng sản xuất nội thất gỗ tại Việt Nam gồm 4 sản phẩm chính:
* **P0 (Quick-Quote AI)**: Báo giá mộc nhanh trong 30 giây từ ảnh 3D/PDF.
* **P1 (Zalo Office & Inventory)**: Quản lý luồng việc qua Zalo OA & Tự động bóc hóa đơn nhập kho.
* **P2 (Mobile Showroom)**: Catalog mẫu mộc di động trên Tablet & Báo giá nhảy tức thì.
* **P3 (AI Auto-Staging)**: Chụp ảnh phòng thô -> AI lót mẫu mộc xưởng -> Chốt cọc VietQR tại chỗ.

Để kinh doanh hiệu quả và dễ dàng tiếp cận mọi xưởng mộc (từ xưởng nhỏ 3 thợ đến xưởng vừa), hệ thống áp dụng chiến lược **Giá Rẻ Bình Dân (No-Brainer Pricing)**:

---

## PHẦN 1: GÓI BASIC — PHÙ HỢP XƯỞNG VỪA & NHỎ

Gói dịch vụ tập trung vào **Khâu Báo giá nhanh và Vận hành Zalo / Kho**.

### 1. Giá Bán Tối Ưu (Đầu Ra)
* **Giá gói theo tháng**: **199.000 VNĐ / tháng** *(Chỉ ~ 6.600 VNĐ / ngày - rẻ hơn 1 ly trà đá!)*
* **Giá gói theo năm**: **1.990.000 VNĐ / năm** *(Đã chiết khấu 2 tháng)*

### 2. Tính Năng Khách Hàng Nhận Được
* Sử dụng không giới hạn **P0 (Quick-Quote AI Báo giá nhanh)**.
* Sử dụng **P1 (Zalo Workflow & AI Bóc hóa đơn nhập kho)** cho tối đa 3 nhân sự.

### 3. Chi Phí Cố Định Hàng Tháng Của App (Nếu Không Bán Được Cho Ai)
Dù chưa có bất kỳ khách hàng nào mua gói, hệ thống vẫn duy trì chi phí cố định hạ tầng và Zalo Doanh nghiệp:
* Chi phí Máy chủ VPS Backend (4 vCPU, 8GB RAM): **630.000 VNĐ / tháng**.
* Chi phí Database PostgreSQL & Redis Cloud: **380.000 VNĐ / tháng**.
* Chi phí Lưu trữ hệ thống Cloud S3: **250.000 VNĐ / tháng**.
* Chi phí Duy trì **Tài khoản Zalo OA Doanh Nghiệp** (Gói Nâng cao duy trì Webhook API & Zalo Portal): **399.000 VNĐ / tháng**.
* 👉 **TỔNG CHI PHÍ CỐ ĐỊNH VẬN HÀNH APP (0 KHÁCH HÀNG)**: **1.659.000 VNĐ / tháng** *(~ 1,66 triệu VNĐ / tháng)*.

### 4. Chi Phí Biến Đổi Phát Sinh Thêm Cho Mỗi Khách Hàng Mua Gói BASIC
Khi có 1 khách hàng mua gói BASIC, hệ thống phát sinh thêm các khoản chi phí biến đổi:
* Chi phí API AI bóc tách ảnh 3D/PDF (Gemini Flash): **5.000 VNĐ / tháng** *(cho 100 lần bóc ảnh)*.
* Chi phí Gửi tin nhắn thông báo Zalo ZNS (Zalo Notification Service) xác nhận tiến độ/báo giá: **15.000 VNĐ / tháng**.
* Chi phí Lưu trữ thêm ảnh phối cảnh Cloud S3: **5.000 VNĐ / tháng**.
* 👉 **TỔNG CHI PHÍ PHÁT SINH THÊM PER KHÁCH HÀNG (BASIC)**: **25.000 VNĐ / tháng / xưởng**.

### 5. Lợi Nhuận & Điểm Hòa Vốn Gói BASIC
* **Lợi nhuận gộp thu về trên 1 xưởng**: **174.000 VNĐ / tháng** *(Biên lợi nhuận gộp vẫn đạt mức cực cao **87,4%**)*.
* **Điểm hòa vốn hạ tầng & Zalo Doanh nghiệp**: Chỉ cần **10 xưởng đăng ký gói BASIC** là doanh thu ($10 \times 199k = 1.990k$) đã đủ trả toàn bộ $1,66$ triệu tiền duy trì hệ thống + Zalo OA Doanh nghiệp hàng tháng.

---

## PHẦN 2: GÓI PRO — TRỌN BỘ CAO CẤP CHỐT CỌC TẠI CÔNG TRÌNH

Gói dịch vụ cao cấp nhất giúp chủ xưởng **Tư vấn di động, Chốt cọc & Nhận tiền chuyển khoản VietQR ngay tại công trình**.

### 1. Giá Bán Tối Ưu (Đầu Ra)
* **Giá gói theo tháng**: **499.000 VNĐ / tháng** *(Chỉ ~ 16.000 VNĐ / ngày - rẻ hơn 1 tô phở bình dân!)*
* **Giá gói theo năm**: **4.990.000 VNĐ / năm** *(Đã chiết khấu 2 tháng)*

### 2. Tính Năng Khách Hàng Nhận Được
* Bao gồm toàn bộ tính năng của gói BASIC (P0 + P1 không giới hạn).
* Thư viện **P2 (Mobile Showroom & Catalog mẫu mộc tham số hóa)**.
* Chức năng **P3 (AI Auto-Staging)**: Chụp ảnh phòng -> AI lót mẫu mộc xưởng vào không gian *(Hạn ngạch 300 lượt render/tháng)*.
* Tự động xuất **Hợp đồng cọc PDF & Mã VietQR** chuyển khoản ngân hàng tại chỗ.

### 3. Chi Phí Cố Định Hàng Tháng Của App (Nếu Không Bán Được Cho Ai)
Tương tự gói BASIC, chi phí hạ tầng dùng chung cố định để duy trì ứng dụng khi 0 khách hàng:
* Chi phí Máy chủ VPS Backend: **630.000 VNĐ / tháng**.
* Chi phí Database PostgreSQL & Redis Cloud: **380.000 VNĐ / tháng**.
* Chi phí Cloud Storage S3 duy trì hệ thống: **250.000 VNĐ / tháng**.
* Chi phí Duy trì **Tài khoản Zalo OA Doanh Nghiệp**: **399.000 VNĐ / tháng**.
* 👉 **TỔNG CHI PHÍ CỐ ĐỊNH VẬN HÀNH APP (0 KHÁCH HÀNG)**: **1.659.000 VNĐ / tháng**.

### 4. Chi Phí Biến Đổi Phát Sinh Thêm Cho Mỗi Khách Hàng Mua Gói PRO
Khi có 1 khách hàng mua gói PRO, hệ thống phát sinh các khoản chi phí biến đổi:
* Chi phí API AI bóc tách ảnh (P0 + P1): **5.000 VNĐ / tháng**.
* Chi phí AI GPU Render Staging ảnh phòng (P3): **30.000 VNĐ / tháng** *(cho 150 ảnh render)*.
* Chi phí Gửi tin nhắn thông báo Zalo ZNS xác nhận hợp đồng cọc: **15.000 VNĐ / tháng**.
* Chi phí Lưu trữ thêm ảnh phối cảnh Cloud S3: **5.000 VNĐ / tháng**.
* 👉 **TỔNG CHI PHÍ PHÁT SINH THÊM PER KHÁCH HÀNG (PRO)**: **55.000 VNĐ / tháng / xưởng**.

### 5. Lợi Nhuận & Điểm Hòa Vốn Gói PRO
* **Lợi nhuận gộp thu về trên 1 xưởng**: **444.000 VNĐ / tháng** *(Biên lợi nhuận gộp đạt **89,0%**)*.
* **Điểm hòa vốn hạ tầng & Zalo Doanh nghiệp**: Chỉ cần **4 xưởng đăng ký gói PRO** là doanh thu ($4 \times 499k = 1.996k$) đã thừa trang trải 100% tiền cố định máy chủ + Zalo OA Doanh nghiệp!

---

## TỔNG KẾT BÀI TOÁN TÀI CHÍNH TOÀN DỰ ÁN (GIÁ MỚI 199K / 499K)

Giả định tỷ lệ khách chọn gói: **30% Gói BASIC (199k)** và **70% Gói PRO (499k)**.  
Doanh thu bình quân mỗi xưởng (ARPU) = **409.000 VNĐ / tháng**.

| Chỉ Số Tài Chính | 10 Xưởng Sử Dụng | 50 Xưởng Sử Dụng | 100 Xưởng Sử Dụng |
| :--- | :---: | :---: | :---: |
| **Tổng Doanh Thu Hàng Tháng (MRR)** | **4.090.000 VNĐ** | **20.450.000 VNĐ** | **40.900.000 VNĐ** |
| Chi phí Đầu vào Biến đổi (COGS) | 460.000 VNĐ | 2.300.000 VNĐ | 4.600.000 VNĐ |
| Chi phí Cố định (Server + Zalo OA) | 1.659.000 VNĐ | 1.659.000 VNĐ | 9.399.000 VNĐ *(Thuê GPU riêng)* |
| **LỢI NHUẬN GỘP HÀNG THÁNG** | **1.971.000 VNĐ** | **16.491.000 VNĐ** | **26.841.000 VNĐ** |
| **Biên Lợi Nhuận Gộp (%)** | **48.2%** | **80.6%** | **65.6%** |

### 🎯 Điểm Hòa Vốn Đáng Chú Ý (Giá Bình Dân):
1. **Hòa vốn hạ tầng kỹ thuật & Zalo Doanh nghiệp** (1,66 triệu VNĐ / tháng):
   * Chỉ cần **4 xưởng gói PRO** hoặc **10 xưởng gói BASIC** là dự án tự nuôi tiền Server & Zalo OA.
2. **Hòa vốn toàn bộ dự án** *(Tính cả 15.000.000 VNĐ tiền lương nhân sự vận hành/tháng)*:
   * Tổng chi phí cần thu: $1,66 \text{ triệu} + 15 \text{ triệu} = 16,66 \text{ triệu VNĐ / tháng}$.
   * Chỉ cần đạt mốc **46 xưởng đăng ký** là dự án tạo ra lợi nhuận ròng dương! Với mức giá 199k - 499k/tháng, việc tìm 46 xưởng mộc tại Việt Nam là cực kỳ khả thi.
