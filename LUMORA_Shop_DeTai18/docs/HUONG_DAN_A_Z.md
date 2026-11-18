# HƯỚNG DẪN A-Z CHẠY WEBSITE & TRIỂN KHAI RENDER

**Đề tài 18 - ứng dụng web động thương mại điện tử trên Render.com**

## PHẦN A. CHẠY Ở MÁY CÁ NHÂN - WINDOWS 11

### Bước 1. Chuẩn bị

- Máy tính Windows 10/11, mạng Internet.
- Cài Python 3.11/3.12, chọn `Add python.exe to PATH` khi cài.
- Cài VSCode (nếu muốn đọc/sửa code) và Git (để đẩy mã nguồn lên GitHub).
- Kiểm tra `py --version` và `git --version` trong PowerShell hoặc Terminal VSCode.

**[ẢNH CẦN CHỤP 01]** Terminal phiên bản Python và thư mục source.

### Bước 2. Giải nén và chạy ứng dụng

1. Tải và giải nén file `LUMORA_Shop_DeTai18_Full_Source.zip`.
2. Mở thư mục `LUMORA_Shop_DeTai18`.
3. Nhấp đúp `CHAY_NHANH_WINDOWS.bat`.
4. Lần đầu máy sẽ tải thư viện; nếu thấy `Uvicorn running on http://127.0.0.1:8000` là thành công.
5. Mở `http://127.0.0.1:8000`. Nếu trình duyệt mở hơi sớm, F5 để tải lại.
6. Giữ terminal mở khi thực hành. Nhấn Ctrl+C khi muốn dừng.

**[ẢNH CẦN CHỤP 02]** Terminal Uvicorn chạy và URL `127.0.0.1:8000`.
**[ẢNH CẦN CHỤP 03]** Trang chủ LUMORA trên localhost.

Nếu muốn chạy thủ công, dùng lệnh ở README phần 3. Nếu cổng 8000 đã sử dụng, dừng ứng dụng khác hoặc đổi 8000 sang 8001 trong `.bat` và URL truy cập.

### Bước 3. Kiểm tra tính năng dành cho khách hàng

**3.1. Xem sản phẩm**
- Mở menu `Khám phá sản phẩm`.
- Gõ `Aurora`, nhấn Tìm kiếm.
- Chọn `Âm thanh`, rồi chọn sắp xếp `Giá: thấp đến cao`.
- Mở chi tiết một sản phẩm và quan sát giá/tồn kho.

**[ẢNH CẦN CHỤP 04]** Danh sách sản phẩm với bộ lọc/tìm kiếm.

**3.2. Tài khoản khách hàng**
- Đăng nhập `khach@demo.local` / `Demo@123456` (tài khoản chỉ tồn tại bản local) hoặc tự đăng ký mới.

**[ẢNH CẦN CHỤP 05]** Giao diện đăng nhập và tài khoản đã đăng nhập.

**3.3. Giỏ hàng và đặt hàng**
- Ở sản phẩm Aurora Wireless Pro, chọn số lượng `2` và nhấn `Thêm vào giỏ hàng`.
- Mở `Giỏ hàng`, kiểm tra số lượng và tổng tiền.
- Nhấn `Tiến hành đặt hàng`.
- Nhập họ tên, số điện thoại giả lập, địa chỉ giao hàng giả lập (không dùng thông tin cá nhân thật khi ghi hình).
- Chọn COD (mặc định) và nhấn `Xác nhận đặt hàng`.
- Ghi lại mã đơn hàng (ví dụ `#00001`, mã thực tế tùy CSDL).
- Mở `Đơn hàng của tôi` → chọn đơn vừa tạo. Trạng thái đầu: `Chờ xác nhận`.

**[ẢNH CẦN CHỤP 06]** Giỏ hàng có sản phẩm và tổng tiền.
**[ẢNH CẦN CHỤP 07]** Trang nhập thông tin giao hàng và hình thức COD.
**[ẢNH CẦN CHỤP 08]** Đơn hàng tạo thành công cùng trạng thái.

### Bước 4. Kiểm tra chức năng quản trị

- Đăng xuất khách hàng.
- Đăng nhập `admin@demo.local` / `Demo@123456`.
- Nhấn `Quản trị` ở menu trên cùng.
- Quan sát KPI: đơn hàng, doanh thu các đơn đã hoàn thành, số đơn chờ và số sản phẩm.
- Chọn `Đơn hàng`, tìm đơn vừa tạo và nhấn lần lượt: **Xác nhận → Giao hàng → Hoàn thành**.
- Sau mỗi lần bấm, quan sát trạng thái thay đổi. Dashboard chỉ cộng doanh thu khi đơn được đánh dấu hoàn thành.
- Chọn `Sản phẩm` → `Thêm sản phẩm`. Thêm một mặt hàng demo với tên, danh mục, giá, tồn kho. Mở lại trang danh sách ngoài cửa hàng để kiểm tra.
- Chọn `Chỉnh sửa` của một sản phẩm để cập nhật tồn kho hoặc ẩn khỏi cửa hàng.

**[ẢNH CẦN CHỤP 09]** Dashboard quản trị và KPI.
**[ẢNH CẦN CHỤP 10]** Danh sách đơn hàng ở các trạng thái.
**[ẢNH CẦN CHỤP 11]** Form thêm/sửa sản phẩm.
**[ẢNH CẦN CHỤP 12]** Sản phẩm mới xuất hiện ở trang khách hàng.

### Bước 5. Kiểm thử các trường hợp đặc biệt

- **Đơn bị hủy**: tạo một đơn mới đang chờ xác nhận, nhấn Hủy trong trang đơn của khách. Xác nhận số lượng tồn kho tăng lại.
- **Phân quyền**: đăng nhập khách và thử mở `/quan-tri` → server trả lỗi 403.
- **Tồn kho**: nhập số lượng mua lớn hơn số lượng tồn, ứng dụng chỉ cho tối đa số còn trong kho ở giỏ; trước khi thanh toán server kiểm tra lại.
- **Kiểm thử tự động**: chạy `CHAY_TEST_WINDOWS.bat`, quan sát kết quả. Bản phát hành ban đầu có 5 bài kiểm thử.

**[ẢNH CẦN CHỤP 13]** Test pytest thành công.
**[ẢNH CẦN CHỤP 14]** Truy cập trái quyền bị chặn 403 hoặc kết quả hoàn kho.

---

## PHẦN B. TRIỂN KHAI CLOUD TRÊN RENDER.COM

### Bước 6. Đẩy mã nguồn lên GitHub

1. Đăng nhập https://github.com/ và tạo repo mới, ví dụ `lumora-shop-cloud-18`. Không tick tạo README vì project đã có.
2. Mở terminal VSCode ngay trong thư mục `LUMORA_Shop_DeTai18`.
3. Chạy:

```powershell
git init
git add .
git commit -m "Initial LUMORA shop for cloud computing topic 18"
git branch -M main
git remote add origin https://github.com/<ten-github>/lumora-shop-cloud-18.git
git push -u origin main
```

Thay `<ten-github>` bằng tài khoản GitHub của bạn. Nếu có vấn đề đăng nhập, làm theo giao diện xác thực trình duyệt của Git. **Không** đưa `.env`, `.local-secret`, `lumora.db`, `.venv/` hoặc thông tin thật lên GitHub (`.gitignore` đã được cấu hình).

**[ẢNH CẦN CHỤP 15]** Repo GitHub có `app/`, `render.yaml`, `requirements.txt`, `README.md`, `tests/`.

### Bước 7. Tạo Blueprint trên Render

1. Truy cập https://dashboard.render.com và đăng nhập bằng GitHub.
2. Chọn **New → Blueprint** (cách gọi có thể thay đổi theo UI Render).
3. Kết nối repo `lumora-shop-cloud-18`.
4. Render sẽ đọc file `render.yaml` và đề xuất tạo **Web Service `lumora-shop-18`** và **Postgres `lumora-shop-db-18`**.
5. Kiểm tra kế hoạch dịch vụ và chi phí hiển thị trước khi xác nhận. File mặc định chọn `free`; nếu Free không khả dụng với tài khoản của bạn, cần cân nhắc chi phí, không tự ý nâng cấp.
6. Render sẽ tự cài dependencies từ `requirements.txt` và khởi chạy `uvicorn app.main:app` qua `startCommand`.

**[ẢNH CẦN CHỤP 16]** Màn hình Blueprint/web service/database và trạng thái tạo thành công.

### Bước 8. Thiết lập admin cloud & bảo mật

Trong **Web Service → Environment**, thêm hai biến môi trường:

```text
ADMIN_EMAIL=<email-admin-cua-ban>
ADMIN_PASSWORD=<mat-khau-rieng-du-10-ky-tu>
```

Các biến còn lại được Blueprint khai báo:

```text
APP_ENV=production
ENABLE_DEMO_ACCOUNTS=0
SECRET_KEY=(Render tự sinh ngẫu nhiên)
DATABASE_URL=(Render tự liên kết từ PostgreSQL)
```

- Không bật `ENABLE_DEMO_ACCOUNTS=1` trên môi trường public.
- Sau khi thêm biến, redeploy/restart để ứng dụng khởi tạo tài khoản admin nếu địa chỉ email chưa tồn tại.
- Không chụp giá trị bí mật trong screenshot.
- Không chia sẻ công khai tài khoản admin thật.

**[ẢNH CẦN CHỤP 17]** Danh sách tên biến môi trường, che giá trị bí mật.

### Bước 9. Xác minh Cloud hoạt động

- Mở URL của Render dạng `https://ten-dich-vu.onrender.com` mà dashboard của bạn cung cấp (không tự đoán URL).
- Truy cập `https://<url-render-cua-ban>/health`, cần trả JSON `{"status":"ok","app":"lumora-shop"}`.
- Truy cập trang chủ, đăng ký tài khoản **mới trên Cloud**.
- Đăng nhập và tạo một đơn hàng thử bằng COD, kiểm tra danh sách đơn.
- Đăng nhập admin Cloud để xác nhận đơn.
- Mở **Logs** của Web Service trên Render và ghi nhận thời điểm có request.
- Đăng nhập lại sau khi reload/redeploy, xác nhận dữ liệu vẫn còn trên PostgreSQL (trong thời hạn DB còn hiệu lực).

**[ẢNH CẦN CHỤP 18]** Website trên URL Render (thanh địa chỉ thể hiện `onrender.com`).
**[ẢNH CẦN CHỤP 19]** Trang `/health` trên URL Render.
**[ẢNH CẦN CHỤP 20]** Logs deploy thành công và request web.
**[ẢNH CẦN CHỤP 21]** Dữ liệu đơn hàng còn sau restart web service.

### Bước 10. Lưu ý dịch vụ Free & sao lưu

- Render Free Web Service có thể ngủ khi không có hoạt động; request đầu sau khi ngủ có thể chậm.
- Render Free Postgres **hết hạn sau 30 ngày** tính từ khi tạo, không phù hợp dùng dữ liệu lâu dài và không có cam kết backup tương đương trả phí.
- Nếu chỉ cần trình diễn trước giảng viên, nên triển khai gần ngày thuyết trình, không đặt thông tin khách thật.
- Khi đến ngày thuyết trình, kiểm tra URL và đăng nhập trước buổi học.
- Nếu không có Free/Postgres khả dụng, không nên dùng SQLite trên Render Free vì filesystem dịch vụ có thể mất khi redeploy/restart. Dùng PostgreSQL hoặc phương án cloud CSDL bền vững phù hợp.

## PHẦN C. GỢI Ý CHO PHẦN BÁO CÁO

Dựa trên đề bài cấp độ 2, báo cáo cần thể hiện:
1. Nhu cầu bài toán & quy trình bán hàng.
2. Công nghệ web động, kiến trúc client-server, cơ sở dữ liệu cloud.
3. Thiết kế bảng dữ liệu & phân quyền.
4. Hướng dẫn triển khai, cấu hình GitHub + Render, ảnh truy cập website bằng URL public.
5. Kịch bản kiểm thử chức năng & kết quả.
6. Đánh giá hiệu năng mức cơ bản, bảo mật, chi phí và giới hạn Free plan.
7. Kết luận & phân công 2-3 thành viên theo phần thực hiện thực tế.

**Không trình bày screenshot local là minh chứng website đã chạy trên cloud.** Minh chứng Cloud phải chụp thật sau khi deploy thành công.

Nguồn chính thống: https://render.com/docs/infrastructure-as-code · https://render.com/docs/blueprint-spec · https://render.com/docs/free · https://fastapi.tiangolo.com/
