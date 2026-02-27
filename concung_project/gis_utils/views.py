import json
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from stores.models import CuaHang
from products.models import SanPham


def trang_chu(request):
    """Trang chủ - hiển thị bản đồ và sản phẩm nổi bật"""
    from django.db.models import Case, When, IntegerField

    # Danh sách mã sản phẩm nổi bật (ưu tiên hiển thị trên trang chủ)
    MA_NOI_BAT = [
        'CC-SUA-001',  # Sữa Aptamil - sua_1
        'CC-SUA-002',  # Sữa Enfamil - bot_sua_1
        'CC-SUA-004',  # Nước yến   - nuoc_yen_1
        'CC-DCH-001',  # LEGO Duplo  - do_choi_1
        'CC-BS-001',   # Pigeon      - binh_sua_1
        'CC-BS-004',   # Comotomo    - binh_sua_4
        'CC-BS-005',   # Ghế ăn dặm  - ghe_ngoi_1
    ]

    # Lấy SP nổi bật theo thứ tự ưu tiên
    sp_uu_tien = SanPham.objects.filter(
        ma_san_pham__in=MA_NOI_BAT, dang_ban=True
    ).annotate(
        thu_tu=Case(
            *[When(ma_san_pham=ma, then=i) for i, ma in enumerate(MA_NOI_BAT)],
            default=99,
            output_field=IntegerField()
        )
    ).order_by('thu_tu')

    san_phams_noi_bat = list(sp_uu_tien)

    # Nếu chưa đủ 8 SP thì bổ sung SP mới nhất
    if len(san_phams_noi_bat) < 8:
        ma_da_co = [sp.ma_san_pham for sp in san_phams_noi_bat]
        them = SanPham.objects.filter(dang_ban=True).exclude(
            ma_san_pham__in=ma_da_co
        ).order_by('-ngay_tao')[:8 - len(san_phams_noi_bat)]
        san_phams_noi_bat += list(them)

    cua_hangs = CuaHang.objects.filter(dang_hoat_dong=True)

    cua_hang_data = []
    for ch in cua_hangs:
        if ch.vi_tri:
            cua_hang_data.append({
                'id': ch.pk,
                'ten': ch.ten,
                'dia_chi': ch.dia_chi,
                'so_dien_thoai': ch.so_dien_thoai,
                'gio_mo': str(ch.gio_mo_cua),
                'gio_dong': str(ch.gio_dong_cua),
                'kinh_do': ch.vi_tri.x,
                'vi_do': ch.vi_tri.y,
            })

    return render(request, 'gis_utils/trang_chu.html', {
        'san_phams_noi_bat': san_phams_noi_bat,
        'cua_hang_data_json': json.dumps(cua_hang_data, ensure_ascii=False),
    })



def tim_cua_hang_gan_nhat(request):
    """API: Tìm cửa hàng gần nhất theo tọa độ người dùng"""
    try:
        vi_do = float(request.GET.get('vi_do'))
        kinh_do = float(request.GET.get('kinh_do'))
        ban_kinh_km = float(request.GET.get('ban_kinh', 10))  # Mặc định 10km
    except (TypeError, ValueError):
        return JsonResponse({'loi': 'Tọa độ không hợp lệ'}, status=400)

    vi_tri_nguoi_dung = Point(kinh_do, vi_do, srid=4326)

    # Truy vấn PostGIS: tìm cửa hàng trong bán kính và sắp xếp theo khoảng cách
    cua_hangs = CuaHang.objects.filter(
        dang_hoat_dong=True,
        vi_tri__isnull=False,
        vi_tri__dwithin=(vi_tri_nguoi_dung, D(km=ban_kinh_km))
    ).annotate(
        khoang_cach=Distance('vi_tri', vi_tri_nguoi_dung)
    ).order_by('khoang_cach')[:5]

    ket_qua = []
    for ch in cua_hangs:
        # Khoảng cách theo đường chim bay (km)
        khoang_cach_km = round(ch.khoang_cach.km, 2)

        ket_qua.append({
            'id': ch.pk,
            'ten': ch.ten,
            'dia_chi': ch.dia_chi,
            'so_dien_thoai': ch.so_dien_thoai,
            'gio_mo': str(ch.gio_mo_cua),
            'gio_dong': str(ch.gio_dong_cua),
            'kinh_do': ch.vi_tri.x,
            'vi_do': ch.vi_tri.y,
            'khoang_cach_km': khoang_cach_km,
            'khoang_cach_hien_thi': f"{khoang_cach_km} km" if khoang_cach_km >= 1 else f"{int(khoang_cach_km * 1000)} m",
        })

    return JsonResponse({
        'cua_hangs': ket_qua,
        'tong_so': len(ket_qua),
        'vi_tri_nguoi_dung': {'vi_do': vi_do, 'kinh_do': kinh_do}
    })


def geocode_dia_chi(request):
    """API: Geocoding địa chỉ -> tọa độ dùng Nominatim (miễn phí)"""
    dia_chi = request.GET.get('dia_chi', '').strip()
    if not dia_chi:
        return JsonResponse({'loi': 'Thiếu địa chỉ'}, status=400)

    try:
        import urllib.request
        import urllib.parse
        from django.conf import settings

        params = urllib.parse.urlencode({
            'q': dia_chi,
            'format': 'json',
            'limit': 1,
            'countrycodes': 'vn',
        })
        url = f'https://nominatim.openstreetmap.org/search?{params}'
        req = urllib.request.Request(
            url,
            headers={'User-Agent': settings.NOMINATIM_USER_AGENT}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read())

        if data:
            return JsonResponse({
                'vi_do': float(data[0]['lat']),
                'kinh_do': float(data[0]['lon']),
                'ten_hien_thi': data[0].get('display_name', dia_chi),
            })
        else:
            return JsonResponse({'loi': 'Không tìm thấy địa chỉ'}, status=404)

    except Exception as e:
        return JsonResponse({'loi': str(e)}, status=500)


def ban_do_tat_ca_cua_hang(request):
    """Trang bản đồ tất cả cửa hàng"""
    cua_hangs = CuaHang.objects.filter(dang_hoat_dong=True, vi_tri__isnull=False)

    cua_hang_data = [{
        'id': ch.pk,
        'ten': ch.ten,
        'dia_chi': ch.dia_chi,
        'so_dien_thoai': ch.so_dien_thoai,
        'gio_mo': str(ch.gio_mo_cua),
        'gio_dong': str(ch.gio_dong_cua),
        'kinh_do': ch.vi_tri.x,
        'vi_do': ch.vi_tri.y,
    } for ch in cua_hangs]

    return render(request, 'gis_utils/ban_do.html', {
        'cua_hang_data_json': json.dumps(cua_hang_data, ensure_ascii=False),
        'tong_cua_hang': len(cua_hang_data),
    })


def thong_ke_dashboard(request):
    """Admin: Dashboard thống kê"""
    if not request.user.is_authenticated or not request.user.la_nhan_vien:
        from django.shortcuts import redirect
        return redirect('trang_chu')

    from orders.models import DonHang
    from products.models import TonKho
    from django.db.models import Sum, Count, F
    from django.utils import timezone
    import datetime

    # Thống kê đơn hàng
    hom_nay = timezone.now().date()
    thang_nay = timezone.now().replace(day=1)

    tong_don_hom_nay = DonHang.objects.filter(ngay_tao__date=hom_nay).count()
    don_cho_xu_ly = DonHang.objects.filter(
        trang_thai__in=['cho_xac_nhan', 'da_xac_nhan', 'dang_dong_goi']
    ).count()

    doanh_thu_thang = DonHang.objects.filter(
        ngay_tao__gte=thang_nay,
        trang_thai='da_giao'
    ).aggregate(
        tong=Sum('tong_tien_san_pham')
    )['tong'] or 0

    # Cảnh báo tồn kho
    so_canh_bao_kho = TonKho.objects.filter(
        so_luong__lte=F('so_luong_toi_thieu')
    ).count()

    # Thống kê theo ngày trong tuần (7 ngày gần nhất)
    bieu_do_data = []
    for i in range(6, -1, -1):
        ngay = hom_nay - datetime.timedelta(days=i)
        so_don = DonHang.objects.filter(ngay_tao__date=ngay).count()
        bieu_do_data.append({
            'ngay': ngay.strftime('%d/%m'),
            'so_don': so_don,
        })

    return render(request, 'gis_utils/dashboard.html', {
        'tong_don_hom_nay': tong_don_hom_nay,
        'don_cho_xu_ly': don_cho_xu_ly,
        'doanh_thu_thang': doanh_thu_thang,
        'so_canh_bao_kho': so_canh_bao_kho,
        'bieu_do_data_json': json.dumps(bieu_do_data, ensure_ascii=False),
        'tong_cua_hang': CuaHang.objects.filter(dang_hoat_dong=True).count(),
    })
