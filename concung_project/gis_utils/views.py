import json
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from stores.models import CuaHang
from products.models import SanPham


def _serialize_store(ch, dist_km=None):
    """Serialize một cửa hàng thành dict JSON-safe."""
    d = {
        'id':            ch.pk,
        'ten':           ch.ten,
        'dia_chi':       ch.dia_chi,
        'quan_huyen':    ch.quan_huyen,
        'tinh_thanh':    ch.tinh_thanh,
        'so_dien_thoai': ch.so_dien_thoai,
        'email':         ch.email or '',
        'gio_mo':        str(ch.gio_mo_cua),
        'gio_dong':      str(ch.gio_dong_cua),
        'ngay_lam_viec': ch.ngay_lam_viec,
        'co_ban_do':     bool(ch.vi_tri),
        'kinh_do':       ch.vi_tri.x if ch.vi_tri else None,
        'vi_do':         ch.vi_tri.y if ch.vi_tri else None,
    }
    if dist_km is not None:
        d['khoang_cach_km'] = dist_km
        if dist_km >= 1:
            d['khoang_cach_hien_thi'] = f"{dist_km:.1f} km"
        else:
            d['khoang_cach_hien_thi'] = f"{int(dist_km * 1000)} m"
    return d


def trang_chu(request):
    """Trang chủ"""
    san_phams_noi_bat = SanPham.objects.filter(dang_ban=True).order_by('-ngay_tao')[:8]
    cua_hangs = CuaHang.objects.filter(dang_hoat_dong=True)

    cua_hang_data = [_serialize_store(ch) for ch in cua_hangs if ch.vi_tri]

    return render(request, 'gis_utils/trang_chu.html', {
        'san_phams_noi_bat': san_phams_noi_bat,
        'cua_hang_data_json': json.dumps(cua_hang_data, ensure_ascii=False),
    })


def tim_cua_hang_gan_nhat(request):
    """API GIS: Tìm cửa hàng gần nhất - hỗ trợ fallback khi PostGIS không khả dụng."""
    try:
        vi_do    = float(request.GET.get('vi_do', ''))
        kinh_do  = float(request.GET.get('kinh_do', ''))
    except (TypeError, ValueError):
        return JsonResponse({'loi': 'Tọa độ không hợp lệ', 'cua_hangs': []}, status=400)

    ban_kinh_km = float(request.GET.get('ban_kinh', 10))
    ket_qua = []

    try:
        # --- Thử PostGIS trước ---
        vi_tri_nd = Point(kinh_do, vi_do, srid=4326)
        cua_hangs = CuaHang.objects.filter(
            dang_hoat_dong=True,
            vi_tri__isnull=False,
            vi_tri__dwithin=(vi_tri_nd, D(km=ban_kinh_km))
        ).annotate(
            khoang_cach=Distance('vi_tri', vi_tri_nd)
        ).order_by('khoang_cach')[:10]

        for ch in cua_hangs:
            ket_qua.append(_serialize_store(ch, round(ch.khoang_cach.km, 2)))

    except Exception:
        # --- Fallback: tính khoảng cách Haversine thuần Python ---
        import math

        def haversine(lat1, lon1, lat2, lon2):
            R = 6371
            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)
            a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
            return R * 2 * math.asin(math.sqrt(a))

        all_ch = CuaHang.objects.filter(dang_hoat_dong=True, vi_tri__isnull=False)
        pairs = []
        for ch in all_ch:
            d = haversine(vi_do, kinh_do, ch.vi_tri.y, ch.vi_tri.x)
            if d <= ban_kinh_km:
                pairs.append((d, ch))

        pairs.sort(key=lambda x: x[0])
        for dist, ch in pairs[:10]:
            ket_qua.append(_serialize_store(ch, round(dist, 2)))

    return JsonResponse({
        'cua_hangs': ket_qua,
        'tong_so':   len(ket_qua),
        'vi_tri_nguoi_dung': {'vi_do': vi_do, 'kinh_do': kinh_do},
    })


def geocode_dia_chi(request):
    """API: Geocoding địa chỉ → tọa độ dùng Nominatim."""
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
            headers={'User-Agent': getattr(settings, 'NOMINATIM_USER_AGENT', 'ConCungApp/1.0')}
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read())

        if data:
            return JsonResponse({
                'vi_do':       float(data[0]['lat']),
                'kinh_do':     float(data[0]['lon']),
                'ten_hien_thi': data[0].get('display_name', dia_chi),
            })
        return JsonResponse({'loi': 'Không tìm thấy địa chỉ'}, status=404)

    except Exception as e:
        return JsonResponse({'loi': str(e)}, status=500)


def ban_do_tat_ca_cua_hang(request):
    """Trang bản đồ - bao gồm cả cửa hàng chưa có GPS (hiển thị danh sách)."""
    tat_ca = CuaHang.objects.filter(dang_hoat_dong=True).order_by('tinh_thanh', 'ten')

    # Chỉ đưa vào JSON cửa hàng có tọa độ
    cua_hang_data = [_serialize_store(ch) for ch in tat_ca if ch.vi_tri]

    return render(request, 'gis_utils/ban_do.html', {
        'cua_hang_data_json': json.dumps(cua_hang_data, ensure_ascii=False),
        'tat_ca_cua_hang':    tat_ca,
        'tong_cua_hang':      tat_ca.count(),
        'so_co_ban_do':       len(cua_hang_data),
    })


def thong_ke_dashboard(request):
    """Admin: Dashboard thống kê"""
    if not request.user.is_authenticated or not request.user.la_nhan_vien:
        from django.shortcuts import redirect
        return redirect('trang_chu')

    from orders.models import DonHang
    from products.models import TonKho
    from django.db.models import Sum, F
    from django.utils import timezone
    import datetime

    hom_nay  = timezone.now().date()
    thang_nay = timezone.now().replace(day=1)

    tong_don_hom_nay = DonHang.objects.filter(ngay_tao__date=hom_nay).count()
    don_cho_xu_ly    = DonHang.objects.filter(
        trang_thai__in=['cho_xac_nhan', 'da_xac_nhan', 'dang_dong_goi']
    ).count()
    doanh_thu_thang  = DonHang.objects.filter(
        ngay_tao__gte=thang_nay, trang_thai='da_giao'
    ).aggregate(tong=Sum('tong_tien_san_pham'))['tong'] or 0

    so_canh_bao_kho = TonKho.objects.filter(
        so_luong__lte=F('so_luong_toi_thieu')
    ).count()

    bieu_do_data = []
    for i in range(6, -1, -1):
        ngay = hom_nay - datetime.timedelta(days=i)
        bieu_do_data.append({
            'ngay':   ngay.strftime('%d/%m'),
            'so_don': DonHang.objects.filter(ngay_tao__date=ngay).count(),
        })

    from orders.models import DonHang as _DH
    don_hangs_moi = _DH.objects.select_related('khach_hang').order_by('-ngay_tao')[:10]

    return render(request, 'gis_utils/dashboard.html', {
        'tong_don_hom_nay': tong_don_hom_nay,
        'don_cho_xu_ly':    don_cho_xu_ly,
        'doanh_thu_thang':  doanh_thu_thang,
        'so_canh_bao_kho':  so_canh_bao_kho,
        'bieu_do_data_json': json.dumps(bieu_do_data, ensure_ascii=False),
        'tong_cua_hang':    CuaHang.objects.filter(dang_hoat_dong=True).count(),
        'don_hangs_moi':    don_hangs_moi,
    })


def api_goi_y_dia_chi(request):
    """
    API autocomplete địa chỉ dùng Nominatim.
    GET ?q=<chuỗi> → [{display_name, lat, lon, place_id}, ...]
    """
    q = request.GET.get('q', '').strip()
    if len(q) < 3:
        return JsonResponse({'goi_y': []})

    try:
        import urllib.request, urllib.parse
        from django.conf import settings

        params = urllib.parse.urlencode({
            'q':            q + ', Việt Nam',
            'format':       'json',
            'limit':        6,
            'countrycodes': 'vn',
            'addressdetails': 1,
        })
        url = f'https://nominatim.openstreetmap.org/search?{params}'
        req = urllib.request.Request(
            url,
            headers={'User-Agent': getattr(settings, 'NOMINATIM_USER_AGENT', 'ConCungApp/1.0')}
        )
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read())

        goi_y = []
        for item in data:
            addr = item.get('address', {})
            # Rút gọn tên hiển thị
            parts = []
            for key in ['road', 'suburb', 'city_district', 'city', 'state']:
                v = addr.get(key)
                if v and v not in parts:
                    parts.append(v)
            short_name = ', '.join(parts[:4]) if parts else item['display_name'][:60]
            goi_y.append({
                'ten':      short_name,
                'day_du':   item['display_name'],
                'vi_do':    float(item['lat']),
                'kinh_do':  float(item['lon']),
            })

        return JsonResponse({'goi_y': goi_y})

    except Exception as e:
        return JsonResponse({'goi_y': [], 'loi': str(e)})


def api_duong_di(request):
    """
    API tìm đường đi ngắn nhất dùng OSRM public API (không cần key).
    GET ?tu_lat=&tu_lng=&den_lat=&den_lng=
    → {khoang_cach_km, thoi_gian_phut, geometry (GeoJSON LineString)}
    """
    try:
        tu_lat  = float(request.GET.get('tu_lat', ''))
        tu_lng  = float(request.GET.get('tu_lng', ''))
        den_lat = float(request.GET.get('den_lat', ''))
        den_lng = float(request.GET.get('den_lng', ''))
    except (TypeError, ValueError):
        return JsonResponse({'loi': 'Thiếu hoặc sai tọa độ'}, status=400)

    try:
        import urllib.request
        # OSRM public demo server - driving profile, return full geometry
        url = (
            f'https://router.project-osrm.org/route/v1/driving/'
            f'{tu_lng},{tu_lat};{den_lng},{den_lat}'
            f'?overview=full&geometries=geojson&steps=true'
        )
        req = urllib.request.Request(url, headers={'User-Agent': 'ConCungApp/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())

        if data.get('code') != 'Ok' or not data.get('routes'):
            return JsonResponse({'loi': 'Không tìm được đường đi'}, status=404)

        route = data['routes'][0]
        dist_km   = round(route['distance'] / 1000, 2)
        time_min  = round(route['duration'] / 60, 0)

        # Trích xuất turn-by-turn steps
        steps = []
        for leg in route.get('legs', []):
            for step in leg.get('steps', []):
                maneuver = step.get('maneuver', {})
                name = step.get('name', '')
                mtype = maneuver.get('type', '')
                modifier = maneuver.get('modifier', '')
                dist = round(step.get('distance', 0))
                if dist == 0:
                    continue
                # Map maneuver → icon + text tiếng Việt
                icon_map = {
                    'depart':       ('🚀', 'Xuất phát'),
                    'arrive':       ('🏁', 'Đến nơi'),
                    'turn':         ('↩️',  f'Rẽ {modifier}'),
                    'continue':     ('⬆️',  'Đi thẳng'),
                    'merge':        ('↗️',  'Nhập làn'),
                    'roundabout':   ('🔄', 'Vào vòng xuyến'),
                    'exit roundabout': ('↗️', 'Ra vòng xuyến'),
                    'fork':         ('⤴️',  f'Rẽ {modifier}'),
                    'end of road':  ('↩️',  f'Rẽ {modifier} cuối đường'),
                }
                icon, action = icon_map.get(mtype, ('→', mtype))
                mod_vn = {'left': 'trái', 'right': 'phải', 'straight': 'thẳng',
                          'slight left': 'nhẹ trái', 'slight right': 'nhẹ phải',
                          'sharp left': 'gấp trái', 'sharp right': 'gấp phải',
                          'uturn': 'quay đầu'}.get(modifier, modifier)
                action = action.replace(modifier, mod_vn)
                label = f"{action}{': ' + name if name else ''}"
                dist_text = f"{dist} m" if dist < 1000 else f"{dist/1000:.1f} km"
                steps.append({'icon': icon, 'label': label, 'khoang_cach': dist_text})

        return JsonResponse({
            'khoang_cach_km':  dist_km,
            'thoi_gian_phut':  int(time_min),
            'geometry':        route['geometry'],
            'steps':           steps,
        })

    except Exception as e:
        return JsonResponse({'loi': str(e)}, status=500)