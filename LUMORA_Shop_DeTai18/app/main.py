import hmac
import os
import re
import secrets
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import quote

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import desc, func, or_, select
from sqlalchemy.orm import Session, selectinload
from starlette.middleware.sessions import SessionMiddleware
from starlette.templating import Jinja2Templates

from .db import SessionLocal, engine, get_db
from .models import Base, Category, Order, OrderEvent, OrderItem, Product, User
from .security import hash_password, verify_password
from .seed import seed

ROOT = Path(__file__).resolve().parent
ENV = os.getenv('APP_ENV', 'development').lower()
SECRET_KEY = os.getenv('SECRET_KEY', 'local-dev-only-change-in-production')
if ENV == 'production' and (SECRET_KEY == 'local-dev-only-change-in-production' or len(SECRET_KEY) < 32):
    raise RuntimeError('Production yêu cầu SECRET_KEY mạnh, dài ít nhất 32 ký tự.')

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        seed(db, create_demo=ENV != 'production' and os.getenv('ENABLE_DEMO_ACCOUNTS', '1') == '1')
    yield

app = FastAPI(title='LUMORA Shop - Đề tài 18', lifespan=lifespan, docs_url=None, redoc_url=None)
app.mount('/static', StaticFiles(directory=str(ROOT / 'static')), name='static')
templates = Jinja2Templates(directory=str(ROOT / 'templates'))
templates.env.filters['money'] = lambda value: f'{int(value):,}'.replace(',', '.') + ' ₫'
templates.env.globals['status_labels'] = {
    'pending': 'Chờ xác nhận', 'confirmed': 'Đã xác nhận',
    'shipping': 'Đang giao', 'delivered': 'Hoàn thành', 'cancelled': 'Đã hủy'
}

@app.middleware('http')
async def load_user(request: Request, call_next):
    request.state.user = None
    uid = request.session.get('uid')
    if uid:
        with SessionLocal() as db:
            request.state.user = db.get(User, uid)
    response = await call_next(request)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['X-Frame-Options'] = 'DENY'
    return response

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY, same_site='lax', https_only=ENV == 'production', max_age=7 * 24 * 3600)


def csrf_token(request):
    if not request.session.get('csrf'):
        request.session['csrf'] = secrets.token_urlsafe(32)
    return request.session['csrf']


def require_csrf(request, token):
    actual = request.session.get('csrf', '')
    if not actual or not hmac.compare_digest(actual, token or ''):
        raise HTTPException(status_code=403, detail='Phiên làm việc không hợp lệ. Hãy tải lại trang và thử lại.')


def redirect(path):
    return RedirectResponse(path, status_code=303)


def flash(request, message, kind='success'):
    request.session['flash'] = {'message': message, 'kind': kind}


def cart_items(request, db):
    cart = request.session.get('cart') or {}
    ids = []
    for k in cart:
        try: ids.append(int(k))
        except ValueError: pass
    products = db.scalars(select(Product).where(Product.id.in_(ids), Product.is_active == True)).all() if ids else []
    items = []
    for p in products:
        qty = max(0, min(int(cart.get(str(p.id), 0)), 99))
        if qty:
            items.append({'product': p, 'quantity': qty, 'total': p.price * qty})
    items.sort(key=lambda i: i['product'].id)
    return items


def render(request, template, db=None, status_code=200, **context):
    if db is None:
        with SessionLocal() as d:
            count = sum(i['quantity'] for i in cart_items(request,d))
    else:
        count = sum(i['quantity'] for i in cart_items(request,db))
    ctx = {'request': request, 'user': request.state.user, 'csrf': csrf_token(request),
           'cart_count': count, 'flash': request.session.pop('flash', None), **context}
    return templates.TemplateResponse(request, template, ctx, status_code=status_code)


def require_login(request):
    if request.state.user is None:
        return redirect('/login?next=' + quote(request.url.path, safe='/'))
    return None


def require_admin(request):
    if request.state.user is None or request.state.user.role != 'admin':
        raise HTTPException(status_code=403, detail='Chỉ quản trị viên được sử dụng chức năng này.')


@app.exception_handler(HTTPException)
async def http_error(request, exc):
    return render(request, 'error.html', status_code=exc.status_code, title=f'Lỗi {exc.status_code}', message=str(exc.detail))

@app.get('/health')
def health():
    return {'status': 'ok', 'app': 'lumora-shop'}

@app.get('/', response_class=HTMLResponse)
def homepage(request: Request, db: Session = Depends(get_db)):
    categories = db.scalars(select(Category)).all()
    featured = db.scalars(select(Product).where(Product.is_active == True, Product.featured == True).order_by(Product.id).limit(8)).all()
    latest = db.scalars(select(Product).where(Product.is_active == True).order_by(desc(Product.id)).limit(4)).all()
    return render(request, 'home.html', db, categories=categories, featured=featured, latest=latest)

@app.get('/san-pham', response_class=HTMLResponse)
def products(request: Request, q: str = '', category: str = '', sort: str = 'popular', db: Session = Depends(get_db)):
    q = q.strip()[:100]
    conditions = [Product.is_active == True]
    if q: conditions.append(or_(Product.name.ilike(f'%{q}%'), Product.description.ilike(f'%{q}%')))
    if category: conditions.append(Product.category.has(Category.slug == category))
    query = select(Product).where(*conditions)
    sort_options = {'popular': (desc(Product.featured), Product.id), 'newest': (desc(Product.id),),
                    'price_asc': (Product.price,), 'price_desc': (desc(Product.price),)}
    query = query.order_by(*sort_options.get(sort, sort_options['popular']))
    found = db.scalars(query).all()
    return render(request, 'products.html', db, products=found, categories=db.scalars(select(Category)).all(),
                  q=q, category=category, sort=sort)

@app.get('/san-pham/{product_id}', response_class=HTMLResponse)
def product_detail(request: Request, product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product or not product.is_active: raise HTTPException(status_code=404, detail='Không tìm thấy sản phẩm.')
    related = db.scalars(select(Product).where(Product.category_id == product.category_id, Product.id != product_id, Product.is_active == True).limit(4)).all()
    return render(request, 'product_detail.html', db, product=product, related=related)

@app.get('/dang-ky', response_class=HTMLResponse)
def register_page(request: Request):
    return render(request, 'register.html')

@app.post('/dang-ky')
def register(request: Request, name: str = Form(''), email: str = Form(''), password: str = Form(''), csrf: str = Form(''), db: Session = Depends(get_db)):
    require_csrf(request, csrf)
    name, email = name.strip()[:120], email.strip().lower()[:255]
    if len(name) < 2 or not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', email) or len(password) < 8:
        return render(request, 'register.html', db, error='Vui lòng nhập tên, email hợp lệ và mật khẩu từ 8 ký tự.', status_code=400)
    if db.scalar(select(User.id).where(User.email == email)):
        return render(request, 'register.html', db, error='Email đã được sử dụng.', status_code=400)
    user = User(name=name, email=email, password_hash=hash_password(password), role='customer')
    db.add(user)
    try: db.commit()
    except Exception:
        db.rollback()
        return render(request, 'register.html', db, error='Không thể đăng ký bằng email này.', status_code=400)
    db.refresh(user)
    request.session['uid'] = user.id
    flash(request, 'Tạo tài khoản thành công. Chào mừng bạn đến với LUMORA!')
    return redirect('/')

@app.get('/dang-nhap', response_class=HTMLResponse)
@app.get('/login', response_class=HTMLResponse)
def login_page(request: Request, next: str = '/'):
    safe_next = next if next.startswith('/') and not next.startswith('//') else '/'
    return render(request, 'login.html', next=safe_next)

@app.post('/dang-nhap')
@app.post('/login')
def login(request: Request, email: str = Form(''), password: str = Form(''), next: str = Form('/'), csrf: str = Form(''), db: Session = Depends(get_db)):
    require_csrf(request, csrf)
    account = db.scalar(select(User).where(User.email == email.strip().lower()))
    if not account or not verify_password(password, account.password_hash):
        return render(request, 'login.html', db, error='Email hoặc mật khẩu không đúng.', next='/', status_code=401)
    request.session['uid'] = account.id
    flash(request, f'Xin chào, {account.name}!')
    return redirect(next if next.startswith('/') and not next.startswith('//') else '/')

@app.post('/dang-xuat')
def logout(request: Request, csrf: str = Form('')):
    require_csrf(request, csrf)
    request.session.pop('uid', None)
    flash(request, 'Bạn đã đăng xuất thành công.')
    return redirect('/')

@app.post('/gio-hang/them/{product_id}')
def cart_add(request: Request, product_id: int, quantity: int = Form(1), csrf: str = Form(''), db: Session = Depends(get_db)):
    require_csrf(request, csrf)
    product = db.get(Product, product_id)
    if not product or not product.is_active: raise HTTPException(status_code=404, detail='Sản phẩm không tồn tại.')
    if product.stock < 1:
        flash(request, 'Sản phẩm đã hết hàng.', 'error')
        return redirect('/san-pham/' + str(product_id))
    cart = dict(request.session.get('cart') or {})
    qty = min(99, max(1, quantity))
    cart[str(product_id)] = min(product.stock, int(cart.get(str(product_id), 0)) + qty)
    request.session['cart'] = cart
    flash(request, f'Đã thêm {product.name} vào giỏ hàng.')
    return redirect('/gio-hang')

@app.get('/gio-hang', response_class=HTMLResponse)
def cart_page(request: Request, db: Session = Depends(get_db)):
    items = cart_items(request, db)
    subtotal = sum(i['total'] for i in items)
    shipping = 0 if subtotal >= 500000 or subtotal == 0 else 30000
    return render(request, 'cart.html', db, items=items, subtotal=subtotal, shipping=shipping)

@app.post('/gio-hang/cap-nhat/{product_id}')
def cart_update(request: Request, product_id: int, quantity: int = Form(0), csrf: str = Form(''), db: Session = Depends(get_db)):
    require_csrf(request, csrf)
    cart = dict(request.session.get('cart') or {})
    product = db.get(Product, product_id)
    if quantity <= 0 or not product or not product.is_active:
        cart.pop(str(product_id), None)
    else:
        cart[str(product_id)] = min(max(1, quantity), product.stock, 99)
        if cart[str(product_id)] <= 0: cart.pop(str(product_id), None)
    request.session['cart'] = cart
    return redirect('/gio-hang')

@app.get('/thanh-toan', response_class=HTMLResponse)
def checkout_page(request: Request, db: Session = Depends(get_db)):
    guard = require_login(request)
    if guard: return guard
    items = cart_items(request, db)
    if not items: return redirect('/gio-hang')
    subtotal = sum(i['total'] for i in items)
    return render(request, 'checkout.html', db, items=items, subtotal=subtotal,
                  shipping=0 if subtotal >= 500000 else 30000)

@app.post('/thanh-toan')
def checkout(request: Request, customer_name: str = Form(''), phone: str = Form(''),
             address: str = Form(''), note: str = Form(''), csrf: str = Form(''), db: Session = Depends(get_db)):
    guard = require_login(request)
    if guard: return guard
    require_csrf(request, csrf)
    customer_name, phone, address, note = customer_name.strip(), phone.strip(), address.strip(), note.strip()
    if not 2 <= len(customer_name) <= 120 or not re.fullmatch(r'[0-9+ .()\-]{9,20}', phone) or not 10 <= len(address) <= 500 or len(note) > 1000:
        flash(request, 'Kiểm tra họ tên, số điện thoại và địa chỉ giao hàng.', 'error')
        return redirect('/thanh-toan')
    items = cart_items(request, db)
    if not items:
        flash(request, 'Giỏ hàng của bạn đang trống.', 'error')
        return redirect('/gio-hang')
    try:
        products = {}
        for row in items:
            pid = row['product'].id
            product = db.scalar(select(Product).where(Product.id == pid).with_for_update())
            if product is None or not product.is_active or product.stock < row['quantity']:
                raise ValueError(f'Sản phẩm {row["product"].name} không còn đủ tồn kho.')
            products[pid] = product
        subtotal = sum(products[r['product'].id].price * r['quantity'] for r in items)
        shipping = 0 if subtotal >= 500000 else 30000
        order = Order(user_id=request.state.user.id, customer_name=customer_name, phone=phone,
                      address=address, note=note, subtotal=subtotal, shipping_fee=shipping,
                      total=subtotal + shipping, payment_method='cod', status='pending')
        db.add(order)
        db.flush()
        for row in items:
            p, qty = products[row['product'].id], row['quantity']
            p.stock -= qty
            db.add(OrderItem(order_id=order.id, product_id=p.id, product_name=p.name,
                             quantity=qty, unit_price=p.price, line_total=p.price * qty))
        db.add(OrderEvent(order_id=order.id, status='pending', description='Khách hàng đặt hàng thành công.'))
        db.commit()
    except ValueError as exc:
        db.rollback()
        flash(request, str(exc), 'error')
        return redirect('/gio-hang')
    request.session['cart'] = {}
    flash(request, f'Đặt hàng thành công! Mã đơn hàng #{order.id:05d}.')
    return redirect(f'/don-hang/{order.id}')

@app.get('/don-hang', response_class=HTMLResponse)
def my_orders(request: Request, db: Session = Depends(get_db)):
    guard = require_login(request)
    if guard: return guard
    orders = db.scalars(select(Order).where(Order.user_id == request.state.user.id).order_by(desc(Order.id))).all()
    return render(request, 'orders.html', db, orders=orders)

@app.get('/don-hang/{order_id}', response_class=HTMLResponse)
def order_detail(request: Request, order_id: int, db: Session = Depends(get_db)):
    guard = require_login(request)
    if guard: return guard
    order = db.scalar(select(Order).where(Order.id == order_id).options(selectinload(Order.items), selectinload(Order.events)))
    if not order or (order.user_id != request.state.user.id and request.state.user.role != 'admin'):
        raise HTTPException(status_code=404, detail='Không tìm thấy đơn hàng.')
    return render(request, 'order_detail.html', db, order=order)

@app.post('/don-hang/{order_id}/huy')
def cancel_order(request: Request, order_id: int, csrf: str = Form(''), db: Session = Depends(get_db)):
    guard = require_login(request)
    if guard: return guard
    require_csrf(request, csrf)
    order = db.scalar(select(Order).where(Order.id == order_id).with_for_update())
    if not order or order.user_id != request.state.user.id: raise HTTPException(status_code=404, detail='Không tìm thấy đơn hàng.')
    if order.status != 'pending':
        flash(request, 'Chỉ được hủy đơn đang chờ xác nhận.', 'error')
        return redirect(f'/don-hang/{order_id}')
    order.status = 'cancelled'
    for row in db.scalars(select(OrderItem).where(OrderItem.order_id == order_id)).all():
        p = db.get(Product, row.product_id)
        if p: p.stock += row.quantity
    db.add(OrderEvent(order_id=order.id, status='cancelled', description='Khách hàng hủy đơn, hoàn trả tồn kho.'))
    db.commit()
    flash(request, 'Đã hủy đơn hàng và hoàn lại số lượng sản phẩm trong kho.')
    return redirect(f'/don-hang/{order_id}')

@app.get('/quan-tri', response_class=HTMLResponse)
def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    require_admin(request)
    total_orders = db.scalar(select(func.count(Order.id))) or 0
    sales = db.scalar(select(func.coalesce(func.sum(Order.total),0)).where(Order.status == 'delivered')) or 0
    pending = db.scalar(select(func.count(Order.id)).where(Order.status == 'pending')) or 0
    total_products = db.scalar(select(func.count(Product.id)).where(Product.is_active == True)) or 0
    low_stock = db.scalars(select(Product).where(Product.stock <= 5, Product.is_active == True).order_by(Product.stock).limit(6)).all()
    orders = db.scalars(select(Order).order_by(desc(Order.id)).limit(8)).all()
    return render(request, 'admin_dashboard.html', db, total_orders=total_orders, sales=sales,
                  pending=pending, total_products=total_products, low_stock=low_stock, orders=orders)

@app.get('/quan-tri/san-pham', response_class=HTMLResponse)
def admin_products(request: Request, db: Session = Depends(get_db)):
    require_admin(request)
    return render(request, 'admin_products.html', db, products=db.scalars(select(Product).order_by(desc(Product.id))).all(),
                  categories=db.scalars(select(Category)).all())

@app.get('/quan-tri/san-pham/moi', response_class=HTMLResponse)
def new_product(request: Request, db: Session = Depends(get_db)):
    require_admin(request)
    return render(request, 'admin_product_form.html', db, product=None, categories=db.scalars(select(Category)).all())

@app.get('/quan-tri/san-pham/{product_id}/sua', response_class=HTMLResponse)
def edit_product(request: Request, product_id: int, db: Session = Depends(get_db)):
    require_admin(request)
    product = db.get(Product, product_id)
    if not product: raise HTTPException(status_code=404, detail='Không tìm thấy sản phẩm.')
    return render(request, 'admin_product_form.html', db, product=product, categories=db.scalars(select(Category)).all())

@app.post('/quan-tri/san-pham/luu')
def save_product(request: Request, csrf: str = Form(''), id: int = Form(0), name: str = Form(''),
                 description: str = Form(''), category_id: int = Form(0), price: int = Form(0),
                 old_price: int = Form(0), stock: int = Form(0), image_symbol: str = Form('📦'),
                 image_color: str = Form('lavender'), featured: str = Form(''),
                 is_active: str = Form(''), db: Session = Depends(get_db)):
    require_admin(request)
    require_csrf(request, csrf)
    if not 2 <= len(name.strip()) <= 180 or len(description) > 3000 or not 1000 <= price <= 1000000000 or not 0 <= stock <= 100000 or not db.get(Category, category_id):
        flash(request, 'Thông tin sản phẩm chưa hợp lệ.', 'error')
        return redirect(f'/quan-tri/san-pham/{id}/sua' if id else '/quan-tri/san-pham/moi')
    if len(image_symbol) > 12 or image_color not in ('lavender','peach','sky','mint','lemon'):
        flash(request, 'Hình minh họa chưa hợp lệ.', 'error')
        return redirect('/quan-tri/san-pham')
    p = db.get(Product,id) if id else Product()
    if p is None: raise HTTPException(status_code=404, detail='Sản phẩm không tồn tại.')
    p.name=name.strip(); p.description=description.strip(); p.category_id=category_id
    p.price=price; p.old_price=old_price if old_price > price else None
    p.stock=stock; p.image_symbol=image_symbol or '📦'; p.image_color=image_color
    p.featured=featured == 'on'; p.is_active=is_active == 'on'
    db.add(p); db.commit()
    flash(request, 'Đã lưu sản phẩm thành công.')
    return redirect('/quan-tri/san-pham')

@app.get('/quan-tri/don-hang', response_class=HTMLResponse)
def admin_orders(request: Request, status: str = '', db: Session = Depends(get_db)):
    require_admin(request)
    query = select(Order).order_by(desc(Order.id))
    if status in ('pending','confirmed','shipping','delivered','cancelled'):
        query = query.where(Order.status == status)
    return render(request, 'admin_orders.html', db, orders=db.scalars(query).all(), status=status)

TRANSITIONS = {'pending': ('confirmed','cancelled'), 'confirmed': ('shipping','cancelled'),
               'shipping': ('delivered',), 'delivered': (), 'cancelled': ()}

@app.post('/quan-tri/don-hang/{order_id}/trang-thai')
def order_status(request: Request, order_id: int, status: str = Form(''), csrf: str = Form(''), db: Session = Depends(get_db)):
    require_admin(request)
    require_csrf(request, csrf)
    order = db.scalar(select(Order).where(Order.id == order_id).with_for_update())
    if not order: raise HTTPException(status_code=404, detail='Không tìm thấy đơn hàng.')
    if status not in TRANSITIONS[order.status]:
        flash(request, 'Chuyển trạng thái không hợp lệ.', 'error')
        return redirect('/quan-tri/don-hang')
    if status == 'cancelled':
        for row in db.scalars(select(OrderItem).where(OrderItem.order_id == order_id)).all():
            p = db.get(Product,row.product_id)
            if p: p.stock += row.quantity
    order.status = status
    db.add(OrderEvent(order_id=order.id, status=status, description=f'Quản trị cập nhật: {templates.env.globals["status_labels"][status]}'))
    db.commit()
    flash(request, 'Đã cập nhật trạng thái đơn hàng.')
    return redirect('/quan-tri/don-hang')
