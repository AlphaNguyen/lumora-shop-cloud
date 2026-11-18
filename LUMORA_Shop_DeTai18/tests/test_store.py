"""Run: python -m pytest -q ; test DB local được tạo riêng trong tmp_path."""
import importlib
import re
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

@pytest.fixture
def store(tmp_path, monkeypatch):
    monkeypatch.setenv('DATABASE_URL', 'sqlite:///' + str(tmp_path / 'test.db'))
    monkeypatch.setenv('ENABLE_DEMO_ACCOUNTS','1')
    monkeypatch.setenv('APP_ENV','development')
    monkeypatch.setenv('SECRET_KEY','only-for-testing-secret-not-production')
    for module in ['app.main','app.db']:
        sys.modules.pop(module, None)
    from app.main import app
    with TestClient(app) as client:
        yield client


def token(html):
    match = re.search(r'name="csrf" value="([^"]+)"', html)
    assert match, 'CSRF field missing'
    return match.group(1)


def login(client,email='khach@demo.local',password='Demo@123456'):
    page = client.get('/dang-nhap')
    return client.post('/dang-nhap',data={'csrf':token(page.text),'email':email,'password':password},follow_redirects=True)


def test_public_and_search(store):
    assert store.get('/health').json()['status'] == 'ok'
    assert 'LUMORA' in store.get('/').text
    assert 'Aurora Wireless Pro' in store.get('/san-pham?q=aurora').text
    assert 'Aurora Wireless Pro' not in store.get('/san-pham?q=webcam').text
    assert 'Halo Smartwatch S2' in store.get('/san-pham?category=thiet-bi-thong-minh').text


def test_cart_order_cancel_and_stock(store):
    assert 'Chào mừng' in login(store).text or 'LUMORA' in store.get('/').text
    before = store.get('/san-pham/1').text
    assert 'Còn 25 sản phẩm' in before
    t = token(store.get('/san-pham/1').text)
    added = store.post('/gio-hang/them/1', data={'csrf':t,'quantity':'2'},follow_redirects=True)
    assert '2.580.000' in added.text
    checkout = store.get('/thanh-toan')
    paid = store.post('/thanh-toan', data={'csrf':token(checkout.text),'customer_name':'Nguyễn Văn Test',
                 'phone':'0901234567','address':'12 Đường Nguyễn Huệ, Phường Bến Nghé, Thành phố Hồ Chí Minh'},follow_redirects=True)
    assert paid.status_code == 200
    assert '2.580.000' in paid.text and '#00001' in paid.text
    assert 'Còn 23 sản phẩm' in store.get('/san-pham/1').text
    cancelled = store.post('/don-hang/1/huy',data={'csrf':token(paid.text)},follow_redirects=True)
    assert cancelled.status_code == 200 and 'Đã hủy' in cancelled.text
    assert 'Còn 25 sản phẩm' in store.get('/san-pham/1').text


def test_admin_workflow(store):
    assert login(store,'admin@demo.local').status_code == 200
    dash = store.get('/quan-tri')
    assert dash.status_code == 200
    form = store.get('/quan-tri/san-pham/moi')
    created = store.post('/quan-tri/san-pham/luu',data={'csrf':token(form.text),'name':'Sản phẩm Demo mới',
       'description':'Test','category_id':'1','price':'150000','old_price':'190000','stock':'10',
       'image_symbol':'🎁','image_color':'mint','is_active':'on','featured':'on'},follow_redirects=True)
    assert created.status_code == 200 and 'Sản phẩm Demo mới' in created.text
    assert 'Sản phẩm Demo mới' in store.get('/san-pham').text


def test_security_csrf_admin_and_broken_auth(store):
    assert store.post('/gio-hang/them/1',data={'quantity':'99'}).status_code == 403
    assert store.get('/quan-tri').status_code == 403
    assert login(store).status_code == 200
    assert store.get('/quan-tri').status_code == 403
    assert store.post('/quan-tri/don-hang/1/trang-thai', data={'csrf':token(store.get('/gio-hang').text),'status':'delivered'}).status_code == 403
    assert '&lt;script&gt;' in store.get('/san-pham?q=%3Cscript%3E').text


def test_order_status_pipeline(store):
    login(store)
    t=token(store.get('/san-pham/2').text)
    store.post('/gio-hang/them/2',data={'csrf':t,'quantity':'1'})
    t=token(store.get('/thanh-toan').text)
    r=store.post('/thanh-toan',data={'csrf':t,'customer_name':'Khách hàng thử nghiệm','phone':'0934455667','address':'20 Lê Lợi, Phường Sài Gòn, Hồ Chí Minh'},follow_redirects=True)
    assert r.status_code == 200
    t=token(store.get('/').text)
    store.post('/dang-xuat',data={'csrf':t})
    login(store,'admin@demo.local')
    for state in ['confirmed','shipping','delivered']:
        t=token(store.get('/quan-tri/don-hang').text)
        r=store.post('/quan-tri/don-hang/1/trang-thai',data={'csrf':t,'status':state},follow_redirects=True)
        assert r.status_code == 200, (state,r.text[:200])
    assert '790.000' in store.get('/quan-tri').text
    invalid=store.post('/quan-tri/don-hang/1/trang-thai',data={'csrf':token(store.get('/quan-tri/don-hang').text),'status':'cancelled'},follow_redirects=True)
    assert 'Chuyển trạng thái không hợp lệ' in invalid.text
    assert store.get('/don-hang/1').status_code == 200
