import os
from sqlalchemy import select
from .models import Category, Product, User
from .security import hash_password

CATEGORY_DATA = [
    ('Âm thanh','am-thanh','🎧'), ('Thiết bị thông minh','thiet-bi-thong-minh','⌚'),
    ('Phụ kiện số','phu-kien-so','🔋'), ('Không gian làm việc','khong-gian-lam-viec','💻')
]
PRODUCT_DATA = [
    ('Aurora Wireless Pro','Âm thanh',1290000,1590000,25,'🎧','lavender',True,'Tai nghe không dây với âm thanh chi tiết, đệm tai êm ái, pin bền bỉ cho mọi hành trình.'),
    ('Nova Sound Mini','Âm thanh',790000,990000,35,'🔊','peach',True,'Loa Bluetooth nhỏ gọn với âm thanh mạnh mẽ, thích hợp những chuyến đi và không gian ấm cúng.'),
    ('AirBuds Studio','Âm thanh',1690000,1990000,18,'🎶','mint',False,'Tai nghe true wireless cùng hộp sạc nhỏ gọn, kết nối ổn định và chất âm cân bằng.'),
    ('Halo Smartwatch S2','Thiết bị thông minh',2190000,2590000,14,'⌚','sky',True,'Đồng hồ thông minh theo dõi vận động, nhắc lịch và đồng bộ thông báo trong ngày.'),
    ('Glow LED Light Bar','Không gian làm việc',890000,1090000,21,'💡','lemon',True,'Đèn bàn tối giản giúp góc làm việc sáng đều và tạo cảm giác dễ chịu.'),
    ('Keycraft Mechanical 75','Không gian làm việc',1890000,2290000,12,'⌨️','lavender',True,'Bàn phím cơ layout 75% gọn gàng, trải nghiệm gõ chắc tay và kết nối linh hoạt.'),
    ('Pebble Wireless Mouse','Không gian làm việc',590000,690000,40,'🖱️','mint',False,'Chuột không dây yên tĩnh, công thái học phù hợp bàn làm việc hiện đại.'),
    ('ChargeGo 20K','Phụ kiện số',690000,850000,27,'🔋','peach',True,'Pin dự phòng 20.000mAh hỗ trợ sạc nhanh và tích hợp bảo vệ thiết bị.'),
    ('Orbit USB-C Hub','Phụ kiện số',750000,890000,24,'🔌','sky',False,'Hub USB-C đa cổng kết nối màn hình, ổ lưu trữ và các thiết bị ngoại vi.'),
    ('Pixel Desk Mat','Không gian làm việc',390000,490000,60,'🪄','peach',False,'Tấm lót bàn mềm mại giúp sắp xếp không gian làm việc gọn gàng hơn.'),
    ('Vision Webcam 2K','Thiết bị thông minh',1390000,1590000,19,'📷','lemon',False,'Webcam 2K dành cho học tập và họp trực tuyến, hình ảnh sắc nét.'),
    ('Cloud SSD Portable 1TB','Phụ kiện số',1790000,2090000,16,'💾','lavender',False,'Ổ cứng SSD di động tốc độ cao, dễ dàng mang dữ liệu đi bất cứ đâu.')
]

def seed(session, create_demo=False):
    if session.scalar(select(Category.id).limit(1)) is None:
        for name,slug,emoji in CATEGORY_DATA:
            session.add(Category(name=name,slug=slug,emoji=emoji))
        session.flush()
    if session.scalar(select(Product.id).limit(1)) is None:
        cats = {c.name: c.id for c in session.scalars(select(Category)).all()}
        for name, cat, price, old, stock, symbol, color, featured, desc in PRODUCT_DATA:
            session.add(Product(name=name,category_id=cats[cat],price=price,old_price=old,stock=stock,
                                image_symbol=symbol,image_color=color,featured=featured,description=desc))
    if create_demo:
        for name,email,role in [('Quản trị LUMORA','admin@demo.local','admin'),('Nguyễn Minh Anh','khach@demo.local','customer')]:
            if not session.scalar(select(User).where(User.email == email)):
                session.add(User(name=name,email=email,role=role,password_hash=hash_password('Demo@123456')))
    admin_email = os.getenv('ADMIN_EMAIL', '').strip().lower()
    admin_password = os.getenv('ADMIN_PASSWORD', '')
    if admin_email and admin_password and len(admin_password) >= 10:
        if not session.scalar(select(User).where(User.email == admin_email)):
            session.add(User(name='Quản trị cửa hàng',email=admin_email,role='admin',password_hash=hash_password(admin_password)))
    session.commit()
