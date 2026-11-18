# KỊCH BẢN DEMO 10-15 PHÚT - LUMORA SHOP

**Mục tiêu:** thuyết minh được *nghiệp vụ web động* và chứng minh website **thực sự chạy trên Render.com**.

## Mở đầu - 1 phút

Nêu yêu cầu đề tài 18: triển khai ứng dụng web động có xử lý nghiệp vụ thực tế lên Render.com. Nhóm lựa chọn lĩnh vực bán hàng online, triển khai LUMORA Shop. Người mua và quản trị viên là hai vai trò.

## Demo khách hàng - 4 phút

1. Mở URL Render, nhấn danh mục Sản phẩm.
2. Tìm kiếm sản phẩm `Aurora`, lọc `Âm thanh` và sắp xếp giá.
3. Đăng nhập/đăng ký khách hàng.
4. Chọn `Aurora Wireless Pro`, thêm 2 cái vào giỏ hàng.
5. Mở giỏ, xác nhận giá và vận chuyển.
6. Nhập thông tin **giả lập**, chọn COD và đặt hàng. Lưu mã đơn.
7. Mở `Đơn hàng của tôi` và xem trạng thái `Chờ xác nhận`.

**Điểm cần nói:** dữ liệu giỏ lưu trong phiên (session); dữ liệu sản phẩm và đơn lưu trong PostgreSQL; tổng tiền, tồn kho được backend tính, không tin số tiền từ trình duyệt.

## Demo quản trị - 3 phút

1. Đăng xuất khách, đăng nhập admin Cloud.
2. Mở dashboard, nêu số đơn, đơn chờ, tổng sản phẩm.
3. Vào Quản lý đơn, xử lý đúng thứ tự: `Chờ xác nhận → Đã xác nhận → Đang giao → Hoàn thành`.
4. Mở dashboard: doanh thu hoàn thành được cập nhật.
5. Thêm một sản phẩm, sửa giá hoặc tồn kho; mở giao diện khách hàng để kiểm tra.

**Điểm cần nói:** có phân quyền; người dùng không được tự vào trang quản trị. Dữ liệu sản phẩm cập nhật động từ DB.

## Demo nền tảng cloud - 2 phút

1. Mở trang Web Service trên Render, chỉ vào URL public.
2. Cho thấy mục Deploy trạng thái `Live` và `Logs`.
3. Mở Postgres dashboard, nói đây là CSDL lưu trữ quan hệ cloud.
4. Mở đường dẫn `/health` để minh chứng server đang hoạt động.
5. Nếu thuận tiện, restart/redeploy và kiểm tra lại đơn hàng trên Postgres (chỉ làm khi đủ thời gian).

## Đánh giá và kết luận - 2 phút

- Ưu: triển khai nhanh, có URL public, web động, tách dữ liệu khỏi instance ứng dụng, thay đổi code rồi redeploy qua GitHub.
- Nhược: Free plan ngủ khi không truy cập, Postgres Free hết hạn sau 30 ngày, chưa có thanh toán thật/giao hàng thật.
- Bảo mật: mật khẩu hash có salt, session ký số, CSRF, role admin, kiểm tra tồn kho ở server.
- Phân tích chi phí: demo dùng Free nếu tài khoản Render có khả năng dùng; khi vận hành thực tế phải tính chi phí máy chủ + DB trả phí + sao lưu + vận chuyển + cổng thanh toán.

## Gợi ý phân vai 3 thành viên (phân công theo đóng góp thực)

- Thành viên 1 (lý thuyết): khái niệm web động, nền tảng Render, so sánh local/cloud và kiến trúc.
- Thành viên 2 (thực hành): xây dựng source, demo khách, demo admin, ảnh ghi nhận triển khai.
- Thành viên 3 (báo cáo): ERD, kết quả kiểm thử, đánh giá ưu nhược, chi phí, trình chiếu.

Nhóm phải phân công và ghi nhận đúng người thực hiện, có ảnh/video/commit minh chứng, không đưa vai trò giả lập vào phiếu.

## Câu hỏi phản biện dự kiến

**Vì sao đây là website động?** Khi thêm sản phẩm, tạo đơn, cập nhật trạng thái, dữ liệu được lưu/truy vấn trong PostgreSQL và render HTML tùy dữ liệu & vai trò, không phải trang HTML tĩnh.

**Vì sao dùng PostgreSQL thay SQLite trên Render?** PostgreSQL là dịch vụ quản lý CSDL tách riêng, phù hợp việc thay đổi instance web. SQLite trên ổ local của Web Service Free không đáng tin cậy để giữ dữ liệu qua restart/redeploy.

**Nếu khách mua quá số lượng tồn?** Server kiểm tra số lượng dựa trên DB, khóa row khi checkout trên PostgreSQL và chỉ cho đặt số lượng đang còn.

**Nếu đơn bị hủy thì sao?** Đơn chuyển cancelled, số lượng sản phẩm được trả về kho và có bản ghi lịch sử.

**Có bán hàng thật không?** Không. Đây là bản demo có nghiệp vụ thật nhưng thanh toán COD và toàn bộ thông tin thương hiệu/sản phẩm giả lập; không thu tiền hay giao hàng.

**Làm sao đánh giá chi phí?** So sánh dịch vụ Free với gói trả phí Render bằng bảng giá chính thức ở thời điểm lập báo cáo, ghi rõ Free DB 30 ngày và hiệu năng giới hạn.
