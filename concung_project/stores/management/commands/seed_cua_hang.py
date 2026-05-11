"""
Seed 10 cửa hàng Con Cưng tại TP.HCM với tọa độ GPS thực.

HƯỚNG DẪN CÀI ĐẶT:
==================
1. Tạo thư mục (nếu chưa có):
   stores/management/__init__.py        ← file rỗng
   stores/management/commands/__init__.py  ← file rỗng

2. Copy file này vào:
   stores/management/commands/seed_cua_hang.py

3. Chạy lệnh:
   python manage.py seed_cua_hang
"""
import datetime
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from stores.models import CuaHang


STORES = [
    {
        'ma': 'CC-Q1-001',
        'ten': 'Con Cưng Quận 1 – Nguyễn Huệ',
        'dia_chi': '30 Nguyễn Huệ, Phường Bến Nghé, Quận 1',
        'quan_huyen': 'Quận 1',
        'tinh_thanh': 'TP. Hồ Chí Minh',
        'sdt': '028 3827 1000',
        'email': 'q1.nguyenhue@concung.com',
        'lat': 10.7731, 'lng': 106.7031,
        'dien_tich': 380.0, 'nv': 12,
    },
    {
        'ma': 'CC-Q3-001',
        'ten': 'Con Cưng Quận 3 – Võ Văn Tần',
        'dia_chi': '215 Võ Văn Tần, Phường 5, Quận 3',
        'quan_huyen': 'Quận 3',
        'tinh_thanh': 'TP. Hồ Chí Minh',
        'sdt': '028 3930 2000',
        'email': 'q3.vvt@concung.com',
        'lat': 10.7772, 'lng': 106.6854,
        'dien_tich': 280.0, 'nv': 9,
    },
    {
        'ma': 'CC-Q7-001',
        'ten': 'Con Cưng Quận 7 – Phú Mỹ Hưng',
        'dia_chi': 'TTTM SC VivoCity, 1058 Nguyễn Văn Linh, Quận 7',
        'quan_huyen': 'Quận 7',
        'tinh_thanh': 'TP. Hồ Chí Minh',
        'sdt': '028 5416 3000',
        'email': 'q7.pmh@concung.com',
        'lat': 10.7295, 'lng': 106.7196,
        'dien_tich': 520.0, 'nv': 16,
    },
    {
        'ma': 'CC-BT-001',
        'ten': 'Con Cưng Bình Thạnh – Xô Viết Nghệ Tĩnh',
        'dia_chi': '112 Xô Viết Nghệ Tĩnh, Phường 26, Bình Thạnh',
        'quan_huyen': 'Bình Thạnh',
        'tinh_thanh': 'TP. Hồ Chí Minh',
        'sdt': '028 3511 4000',
        'email': 'bt.xvnt@concung.com',
        'lat': 10.8108, 'lng': 106.7076,
        'dien_tich': 240.0, 'nv': 8,
    },
    {
        'ma': 'CC-TD-001',
        'ten': 'Con Cưng Tân Định – Hai Bà Trưng',
        'dia_chi': '334 Hai Bà Trưng, Phường 8, Quận 3',
        'quan_huyen': 'Quận 3',
        'tinh_thanh': 'TP. Hồ Chí Minh',
        'sdt': '028 3820 5000',
        'email': 'q3.hbt@concung.com',
        'lat': 10.7919, 'lng': 106.6956,
        'dien_tich': 200.0, 'nv': 7,
    },
    {
        'ma': 'CC-GV-001',
        'ten': 'Con Cưng Gò Vấp – Quang Trung',
        'dia_chi': '430 Quang Trung, Phường 10, Gò Vấp',
        'quan_huyen': 'Gò Vấp',
        'tinh_thanh': 'TP. Hồ Chí Minh',
        'sdt': '028 3895 6000',
        'email': 'govap.qt@concung.com',
        'lat': 10.8383, 'lng': 106.6648,
        'dien_tich': 260.0, 'nv': 9,
    },
    {
        'ma': 'CC-TB-001',
        'ten': 'Con Cưng Tân Bình – Trường Chinh',
        'dia_chi': '509 Trường Chinh, Phường 14, Tân Bình',
        'quan_huyen': 'Tân Bình',
        'tinh_thanh': 'TP. Hồ Chí Minh',
        'sdt': '028 3842 7000',
        'email': 'tanbinh.tc@concung.com',
        'lat': 10.7994, 'lng': 106.6526,
        'dien_tich': 230.0, 'nv': 8,
    },
    {
        'ma': 'CC-TP-001',
        'ten': 'Con Cưng Thủ Đức – Vincom Thủ Đức',
        'dia_chi': 'Vincom Plaza Thủ Đức, 216 Võ Văn Ngân, TP. Thủ Đức',
        'quan_huyen': 'TP. Thủ Đức',
        'tinh_thanh': 'TP. Hồ Chí Minh',
        'sdt': '028 6282 8000',
        'email': 'thuduc.vm@concung.com',
        'lat': 10.8487, 'lng': 106.7718,
        'dien_tich': 410.0, 'nv': 13,
    },
    {
        'ma': 'CC-Q8-001',
        'ten': 'Con Cưng Quận 8 – Phạm Thế Hiển',
        'dia_chi': '78 Phạm Thế Hiển, Phường 4, Quận 8',
        'quan_huyen': 'Quận 8',
        'tinh_thanh': 'TP. Hồ Chí Minh',
        'sdt': '028 3850 9000',
        'email': 'q8.pth@concung.com',
        'lat': 10.7472, 'lng': 106.6807,
        'dien_tich': 195.0, 'nv': 7,
    },
    {
        'ma': 'CC-PN-001',
        'ten': 'Con Cưng Phú Nhuận – Hoàng Văn Thụ',
        'dia_chi': '205 Hoàng Văn Thụ, Phường 8, Phú Nhuận',
        'quan_huyen': 'Phú Nhuận',
        'tinh_thanh': 'TP. Hồ Chí Minh',
        'sdt': '028 3845 1010',
        'email': 'pn.hvt@concung.com',
        'lat': 10.8012, 'lng': 106.6741,
        'dien_tich': 210.0, 'nv': 8,
    },
]


class Command(BaseCommand):
    help = 'Seed 10 cửa hàng Con Cưng tại TP.HCM với tọa độ GPS'

    def handle(self, *args, **options):
        self.stdout.write('\n🏪  Seed cửa hàng Con Cưng\n' + '═' * 55)
        them = cap_nhat = 0

        for s in STORES:
            defaults = {
                'ten':                s['ten'],
                'dia_chi':            s['dia_chi'],
                'quan_huyen':         s['quan_huyen'],
                'tinh_thanh':         s['tinh_thanh'],
                'so_dien_thoai':      s['sdt'],
                'email':              s['email'],
                'vi_tri':             Point(s['lng'], s['lat'], srid=4326),
                'gio_mo_cua':         datetime.time(8, 0),
                'gio_dong_cua':       datetime.time(22, 0),
                'ngay_lam_viec':      'Thứ 2 – Chủ nhật',
                'dien_tich':          s['dien_tich'],
                'so_luong_nhan_vien': s['nv'],
                'dang_hoat_dong':     True,
            }
            obj, created = CuaHang.objects.update_or_create(
                ma_cua_hang=s['ma'], defaults=defaults
            )
            if created:
                them += 1
                self.stdout.write(f"  ✅ Thêm mới : {s['ten']}")
            else:
                cap_nhat += 1
                self.stdout.write(f"  🔄 Cập nhật: {s['ten']}")

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Hoàn tất! Thêm mới: {them} · Cập nhật: {cap_nhat}'
            f'\n👉 http://127.0.0.1:8000/cua-hang/'
            f'\n👉 http://127.0.0.1:8000/ban-do/\n'
        ))