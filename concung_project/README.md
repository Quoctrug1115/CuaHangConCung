# 🐾 Con Cưng - Hệ thống quản lý cửa hàng thú cưng tích hợp GIS

## Yêu cầu hệ thống

- Python 3.10+
- PostgreSQL 14+ với PostGIS extension
- GDAL (thư viện GIS)

---

## Cài đặt môi trường

### 1. Cài đặt PostgreSQL + PostGIS

```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib postgis

# Tạo database và extension
sudo -u postgres psql
CREATE DATABASE concung_db;
\c concung_db
CREATE EXTENSION postgis;
\q
```

### 2. Cài đặt GDAL (bắt buộc cho GeoDjango)

```bash
# Ubuntu/Debian
sudo apt install gdal-bin libgdal-dev python3-gdal

# macOS
brew install gdal
```

### 3. Tạo môi trường Python và cài thư viện

```bash
python -m venv venv
py -3.12 -m venv venv
source venv/bin/activate       # Linux/Mac
venv\Scripts\activate          # Windows

pip install -r requirements.txt
```

### 4. Cấu hình settings.py

Chỉnh sửa `concung/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'concung_db',
        'USER': 'postgres',
        'PASSWORD': 'your_password',  # Đổi password
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 5. Chạy migrations

```bash
python manage.py makemigrations accounts stores products orders
python manage.py migrate
```

### 6. Tạo tài khoản admin

```bash
python manage.py createsuperuser
```

### 7. Khởi động server

```bash
python manage.py runserver
```
## lỗi thư viện : python -m pip install Pillow
##                python -m pip install psycopg

Truy cập: http://127.0.0.1:8000

---

## Cấu trúc dự án

```
concung_project/
├── concung/                    # Cấu hình dự án
│   ├── settings.py
│   └── urls.py
├── accounts/                   # Quản lý người dùng & phân quyền
│   ├── models.py               # Model NguoiDung (kế thừa AbstractUser)
│   ├── views.py                # Đăng ký, đăng nhập, hồ sơ
│   ├── forms.py
│   └── urls.py
├── stores/                     # Quản lý cửa hàng & nhân viên
│   ├── models.py               # CuaHang (có PointField GIS), NhanVien, CaLamViec
│   ├── views.py                # CRUD cửa hàng, nhân viên
│   ├── forms.py                # Form nhập tọa độ
│   └── urls.py
├── products/                   # Quản lý sản phẩm & kho
│   ├── models.py               # SanPham, DanhMuc, TonKho, LichSuKho
│   ├── views.py                # Danh sách SP, tìm kiếm, quản lý kho
│   ├── forms.py
│   └── urls.py
├── orders/                     # Đơn hàng & giỏ hàng
│   ├── models.py               # DonHang, ChiTietDonHang, GioHang, LichSuTrangThai
│   ├── views.py                # Giỏ hàng, đặt hàng, theo dõi, quản lý
│   └── urls.py
├── gis_utils/                  # Chức năng GIS & Dashboard
│   ├── views.py                # Trang chủ, bản đồ, API tìm cửa hàng gần nhất
│   └── urls.py
└── templates/                  # Templates HTML
    ├── base.html               # Layout chung (Bootstrap 5 + Leaflet)
    ├── accounts/
    ├── stores/
    ├── products/
    ├── orders/
    └── gis_utils/
        ├── trang_chu.html      # Trang chủ có bản đồ GIS
        ├── dashboard.html      # Admin dashboard + Chart.js
        └── ban_do.html         # Bản đồ toàn bộ cửa hàng
```

---

## Tính năng GIS

### Tìm cửa hàng gần nhất

**API endpoint:** `GET /api/cua-hang-gan-nhat/?vi_do=10.77&kinh_do=106.70&ban_kinh=10`

**Ví dụ phản hồi:**
```json
{
  "cua_hangs": [
    {
      "ten": "Con Cưng Quận 1",
      "dia_chi": "123 Nguyễn Huệ, Q.1",
      "khoang_cach_km": 0.85,
      "khoang_cach_hien_thi": "850 m",
      "kinh_do": 106.6979,
      "vi_do": 10.7762
    }
  ]
}
```

### Geocoding địa chỉ

**API endpoint:** `GET /api/geocode/?dia_chi=123+Nguyen+Hue+HCMC`

Sử dụng Nominatim (OpenStreetMap) - **miễn phí, không cần API key**.

---

## Các URL chính

| URL | Chức năng |
|-----|-----------|
| `/` | Trang chủ + bản đồ GIS |
| `/san-pham/` | Danh sách sản phẩm |
| `/cua-hang/` | Danh sách cửa hàng |
| `/ban-do/` | Bản đồ toàn quốc |
| `/don-hang/gio-hang/` | Giỏ hàng |
| `/don-hang/dat-hang/` | Đặt hàng |
| `/don-hang/theo-doi/<ma>/` | Theo dõi đơn hàng |
| `/dashboard/` | Admin dashboard |
| `/accounts/dang-nhap/` | Đăng nhập |
| `/accounts/dang-ky/` | Đăng ký |

---

## Vai trò & phân quyền

| Vai trò | Quyền |
|---------|-------|
| **admin** | Toàn quyền |
| **quan_ly** | Quản lý cửa hàng, sản phẩm, kho, nhân viên, đơn hàng |
| **nhan_vien** | Xem & cập nhật đơn hàng, nhập/xuất kho |
| **shipper** | Xem đơn hàng, cập nhật trạng thái vận chuyển |
| **khach_hang** | Mua hàng, xem đơn hàng của mình |

---

## Mở rộng

- **Thanh toán online:** Tích hợp VNPay, MoMo
- **Email thông báo:** Django email backend + SMTP
- **Chỉ đường thực tế:** OpenRouteService API (miễn phí)
- **Push notification:** Firebase Cloud Messaging
