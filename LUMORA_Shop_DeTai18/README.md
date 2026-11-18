# LUMORA Shop - Website bán hàng online | Đề tài 18 - Điện toán đám mây

**Bản demo học tập có xử lý nghiệp vụ thật**, triển khai được lên [Render.com](https://render.com). Không thực hiện thu tiền hoặc giao hàng thật.

## 1. Đúng trọng tâm của đề tài 18

> “Triển khai ứng dụng web động (dynamic web app) thuộc 1 lĩnh vực nào đó, gồm nghiệp vụ xử lý của lĩnh vực đó lên nền tảng Render.com.”

Lĩnh vực chọn: **thương mại điện tử / cửa hàng phụ kiện công nghệ**. LUMORA Shop gồm giao diện khách hàng + quản trị viên, cơ sở dữ liệu, nghiệp vụ quản lý bán hàng và cấu hình triển khai Render.

### Công nghệ
- Backend: **Python 3.11+ / FastAPI** (web application, HTML server-side).
- Frontend: **HTML / Jinja2 / CSS / JavaScript**, responsive.
- ORM: **SQLAlchemy 2.x**.
- Database: **SQLite** khi chạy local, **PostgreSQL** khi triển khai Render.
- Cloud: **Render Web Service + Render Postgres**.
- Kiểm thử: **pytest + FastAPI TestClient**.

## 2. Chức năng đã hiện thực

| Người dùng | Quản trị viên |
|---|---|
| Đăng ký, đăng nhập, đăng xuất | Đăng nhập riêng qua vai trò admin |
| Xem danh mục/sản phẩm, tìm kiếm, sắp xếp | Xem dashboard tổng số đơn, doanh thu đã giao, số đơn chờ |
| Xem chi tiết, giá, tồn kho | Thêm, sửa, ẩn/hiện sản phẩm; cập nhật giá và tồn kho |
| Thêm giỏ hàng, sửa số lượng, xóa khỏi giỏ | Xem tất cả đơn hàng, lọc trạng thái |
| Đặt hàng COD với địa chỉ, điện thoại | Xác nhận → đang giao → hoàn thành; hoặc hủy |
| Xem lịch sử, chi tiết, timeline của đơn | Hủy đơn trước khi giao và hoàn kho |
| Hủy đơn đang chờ xác nhận | Cảnh báo sản phẩm tồn kho thấp |

**Lưu ý:** Không có tích hợp ví điện tử, tài khoản ngân hàng, phí vận chuyển thực, bên giao hàng hay email/SMS thực. Dữ liệu & thương hiệu là mô phỏng dùng cho học tập.

## 3. Chạy local nhanh trên Windows 11

1. Giải nén ZIP.
2. Cài **Python 3.11 hoặc 3.12** từ python.org, đánh dấu **Add Python to PATH** khi cài.
3. Kết nối Internet để pip tải thư viện lần đầu.
4. Nhấp đúp **`CHAY_NHANH_WINDOWS.bat`**.
5. Khi terminal báo `Uvicorn running on http://127.0.0.1:8000`, mở trình duyệt **http://127.0.0.1:8000**.
6. Để dừng web, nhấn `Ctrl + C` trong terminal.

Lần đầu script tạo `.venv/`, cài thư viện, sinh `.local-secret`, tạo SQLite `lumora.db` và dữ liệu mẫu. Các file này được loại khỏi ZIP và `.gitignore` khi upload GitHub.

### Tài khoản demo local
| Vai trò | Email | Mật khẩu |
|---|---|---|
| Quản trị viên | `admin@demo.local` | `Demo@123456` |
| Khách hàng | `khach@demo.local` | `Demo@123456` |

**Chỉ dùng tài khoản này ở LOCAL.** Bản Render mặc định `ENABLE_DEMO_ACCOUNTS=0`, không tạo hai tài khoản demo này. Đặt ADMIN_EMAIL & ADMIN_PASSWORD riêng trên Render.

### Cách chạy thủ công qua VSCode / terminal
```powershell
cd <duong-dan-toi-thu-muc-LUMORA_Shop_DeTai18>
py -3 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
$env:DATABASE_URL='sqlite:///./lumora.db'
$env:ENABLE_DEMO_ACCOUNTS='1'
$env:SECRET_KEY='local-only-long-secret'
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## 4. Kiểm thử tự động

- Bản Windows: mở **`CHAY_TEST_WINDOWS.bat`** (sau khi đã chạy script lần đầu).
- Terminal (khi venv active): `pip install pytest httpx` rồi chạy `python -m pytest -q`.
- Các test tạo database tạm riêng, không ảnh hưởng database demo.

Các trường hợp: lọc/tìm kiếm, thêm giỏ-đặt đơn-hủy hoàn kho, CRUD sản phẩm, quyền admin/CSRF/XSS, vòng đời đơn hàng.

## 5. Đưa lên Render.com

Có sẵn **`render.yaml`** tại thư mục gốc, dùng Render **Blueprint** tạo Web Service + PostgreSQL. Chi tiết trong [docs/HUONG_DAN_A_Z.md](docs/HUONG_DAN_A_Z.md).

Bắt buộc thêm biến môi trường trong Render Web Service:
- `ADMIN_EMAIL`: địa chỉ email admin riêng (ví dụ của bạn, không dùng demo.local).
- `ADMIN_PASSWORD`: mật khẩu riêng **ít nhất 10 ký tự**.

`SECRET_KEY` được tự sinh trong Blueprint, `DATABASE_URL` tự liên kết với PostgreSQL, `APP_ENV=production`, `ENABLE_DEMO_ACCOUNTS=0`. Sau khi đặt ADMIN_EMAIL/PASSWORD, **Redeploy** Web Service; app tạo tài khoản admin nếu email chưa tồn tại. Khi muốn đổi mật khẩu tài khoản đã tạo, sửa trong CSDL theo quy trình quản trị, vì thay environment variable không tự đổi mật khẩu hiện tại.

> **Lưu ý dịch vụ:** Render Postgres Free hết hạn sau **30 ngày**, Render Free Web Service có thể ngủ khi không có traffic; đừng trông đợi dịch vụ miễn phí chạy ổn định như production. Cần xuất/sao lưu dữ liệu khi cần. Tham khảo https://render.com/docs/free

## 6. Sơ đồ thư mục
```
LUMORA_Shop_DeTai18/
├── app/
│   ├── main.py                 # Endpoint + nghiệp vụ website
│   ├── db.py                   # SQLite/PostgreSQL config
│   ├── models.py               # 5+ bảng cơ sở dữ liệu
│   ├── security.py             # Băm & kiểm tra mật khẩu PBKDF2
│   ├── seed.py                 # Danh mục/sản phẩm/tài khoản local mẫu
│   ├── templates/             # Jinja2 HTML
│   └── static/css,static/js/   # Giao diện responsive & tương tác
├── tests/test_store.py        # Kiểm thử tự động
├── docs/                      # Hướng dẫn, kịch bản demo, ảnh preview
├── render.yaml                # Blueprint Render Cloud
├── requirements.txt           # Thư viện Python
├── CHAY_NHANH_WINDOWS.bat     # Tự chạy local A-Z
├── CHAY_TEST_WINDOWS.bat      # Chạy test
└── .env.example               # Mẫu biến môi trường
```

## 7. Bảo mật / giới hạn mô hình
- Password hash PBKDF2-HMAC-SHA256 có salt riêng, không lưu plaintext.
- Session signed cookie, `HttpOnly`, `SameSite=Lax`, `Secure` khi production.
- Token CSRF ở các form ghi dữ liệu, chống sửa yêu cầu trái phép.
- Quản trị viên bị giới hạn theo vai trò; khách chỉ xem đơn của mình.
- Tính lại giá, kiểm tra tồn kho tại server; bản PostgreSQL khóa hàng khi checkout.
- Đơn hàng lưu bản chụp tên/giá để không bị sai khi quản trị thay đổi giá.
- Không lưu số thẻ ngân hàng, không xử lý tiền thật.
- **Đây là demo**, chưa có email xác thực, quên mật khẩu, cổng thanh toán, vận chuyển thật, migration production, chống spam/rate limiting, hệ thống sao lưu định kỳ. Không dùng nguyên trạng để kinh doanh thật.

## 8. Tài liệu
- [HƯỚNG DẪN A-Z](docs/HUONG_DAN_A_Z.md)
- [KỊCH BẢN DEMO VÀ ẢNH CẦN CHỤP](docs/KICH_BAN_DEMO.md)
- [KIẾN TRÚC + ERD + NGHIỆP VỤ](docs/KIEN_TRUC_VA_NGHIEP_VU.md)

## 9. Nguồn tham khảo chính thức
- Render: https://render.com/docs/deploy-flask (mẫu triển khai Python, nguyên lý tương tự với FastAPI + Uvicorn)
- Render: https://render.com/docs/infrastructure-as-code
- Render: https://render.com/docs/blueprint-spec
- Render: https://render.com/docs/free
- FastAPI: https://fastapi.tiangolo.com/
- SQLAlchemy: https://docs.sqlalchemy.org/en/20/
