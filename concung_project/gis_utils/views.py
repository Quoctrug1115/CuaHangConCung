import json
from django.shortcuts import render, get_object_or_404
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

# ═══════════════════════════════════════════════════════════════
#  GIS NÂNG CAO — THÊM MỚI
# ═══════════════════════════════════════════════════════════════

def api_cap_nhat_gps_cua_hang(request, pk):
    """
    API AJAX: Cập nhật tọa độ GPS cửa hàng trực tiếp từ bản đồ.
    POST {vi_do, kinh_do}  →  {ok: true, vi_do, kinh_do}
    """
    if not request.user.is_authenticated or not request.user.la_quan_ly:
        return JsonResponse({'loi': 'Không có quyền'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'loi': 'Chỉ chấp nhận POST'}, status=405)

    try:
        vi_do   = float(request.POST.get('vi_do', ''))
        kinh_do = float(request.POST.get('kinh_do', ''))
    except (TypeError, ValueError):
        return JsonResponse({'loi': 'Tọa độ không hợp lệ'}, status=400)

    # Kiểm tra hợp lệ - trong phạm vi Việt Nam
    if not (8.0 <= vi_do <= 24.0 and 102.0 <= kinh_do <= 110.0):
        return JsonResponse({'loi': 'Tọa độ ngoài lãnh thổ Việt Nam'}, status=400)

    cua_hang = get_object_or_404(CuaHang, pk=pk)
    cua_hang.vi_tri = Point(kinh_do, vi_do, srid=4326)
    cua_hang.save(update_fields=['vi_tri'])

    return JsonResponse({
        'ok':      True,
        'vi_do':   vi_do,
        'kinh_do': kinh_do,
        'ten':     cua_hang.ten,
    })


def api_xoa_gps_cua_hang(request, pk):
    """API AJAX: Xoá tọa độ GPS cửa hàng."""
    if not request.user.is_authenticated or not request.user.la_quan_ly:
        return JsonResponse({'loi': 'Không có quyền'}, status=403)
    if request.method != 'POST':
        return JsonResponse({'loi': 'Chỉ chấp nhận POST'}, status=405)

    cua_hang = get_object_or_404(CuaHang, pk=pk)
    cua_hang.vi_tri = None
    cua_hang.save(update_fields=['vi_tri'])
    return JsonResponse({'ok': True})


def api_thong_ke_gis(request):
    """
    API thống kê GIS: đơn hàng, doanh thu theo quận/huyện của cửa hàng.
    Trả về dữ liệu để vẽ heatmap và biểu đồ.
    """
    if not request.user.is_authenticated or not request.user.la_nhan_vien:
        return JsonResponse({'loi': 'Không có quyền'}, status=403)

    from orders.models import DonHang
    from django.db.models import Count, Sum

    # Thống kê theo cửa hàng
    thong_ke_ch = CuaHang.objects.filter(
        dang_hoat_dong=True, vi_tri__isnull=False
    ).annotate(
        so_don=Count('don_hangs'),
        tong_dt=Sum('don_hangs__tong_tien_san_pham'),
    ).values('id', 'ten', 'quan_huyen', 'tinh_thanh', 'so_don', 'tong_dt')

    heat_points = []
    store_stats = []

    all_ch = CuaHang.objects.filter(dang_hoat_dong=True, vi_tri__isnull=False)
    for ch in all_ch:
        so_don = DonHang.objects.filter(cua_hang=ch).count()
        tong_dt = DonHang.objects.filter(
            cua_hang=ch, trang_thai='da_giao'
        ).aggregate(t=Sum('tong_tien_san_pham'))['t'] or 0

        # Heatmap: mỗi đơn hàng tạo 1 điểm nhiệt (intensity theo so_don)
        intensity = min(so_don / 10.0, 1.0) if so_don > 0 else 0.1
        heat_points.append([ch.vi_tri.y, ch.vi_tri.x, intensity])

        store_stats.append({
            'id':       ch.pk,
            'ten':      ch.ten,
            'quan':     ch.quan_huyen,
            'vi_do':    ch.vi_tri.y,
            'kinh_do':  ch.vi_tri.x,
            'so_don':   so_don,
            'doanh_thu': int(tong_dt),
        })

    # Thống kê theo quận/huyện (từ địa chỉ giao hàng)
    from orders.models import DonHang as _DH
    don_theo_khu = _DH.objects.filter(
        trang_thai__in=['da_giao', 'dang_giao']
    ).values('cua_hang__quan_huyen').annotate(
        so_don=Count('id')
    ).order_by('-so_don')[:15]

    return JsonResponse({
        'heat_points':    heat_points,
        'store_stats':    store_stats,
        'don_theo_khu':   list(don_theo_khu),
    })


def api_vung_phu_song(request):
    """
    API: Tính vùng phủ sóng (coverage circle) cho tất cả cửa hàng.
    Trả về danh sách circle GeoJSON để hiển thị trên bản đồ.
    """
    ban_kinh_km = float(request.GET.get('ban_kinh', 5))
    ban_kinh_km = max(0.5, min(ban_kinh_km, 30))  # clamp 0.5–30 km

    cua_hangs = CuaHang.objects.filter(dang_hoat_dong=True, vi_tri__isnull=False)

    vung_phu = []
    for ch in cua_hangs:
        from orders.models import DonHang
        so_don = DonHang.objects.filter(cua_hang=ch).count()
        # Màu theo mức độ hoạt động
        if so_don == 0:
            mau = '#94A3B8'
        elif so_don < 5:
            mau = '#3B82F6'
        elif so_don < 20:
            mau = '#10B981'
        else:
            mau = '#F59E0B'

        vung_phu.append({
            'id':          ch.pk,
            'ten':         ch.ten,
            'vi_do':       ch.vi_tri.y,
            'kinh_do':     ch.vi_tri.x,
            'ban_kinh_m':  int(ban_kinh_km * 1000),
            'so_don':      so_don,
            'mau':         mau,
        })

    return JsonResponse({'vung_phu_song': vung_phu, 'ban_kinh_km': ban_kinh_km})


def ban_do_gis_nang_cao(request):
    """Trang bản đồ GIS nâng cao cho admin - heatmap, coverage, GPS editor."""
    if not request.user.is_authenticated or not request.user.la_nhan_vien:
        from django.shortcuts import redirect
        return redirect('trang_chu')

    tat_ca = CuaHang.objects.filter(dang_hoat_dong=True).order_by('tinh_thanh', 'ten')
    cua_hang_data = [_serialize_store(ch) for ch in tat_ca]  # kể cả chưa có GPS

    return render(request, 'gis_utils/ban_do_gis.html', {
        'cua_hang_data_json': json.dumps(cua_hang_data, ensure_ascii=False),
        'tat_ca_cua_hang':    tat_ca,
        'tong_cua_hang':      tat_ca.count(),
        'so_co_ban_do':       tat_ca.filter(vi_tri__isnull=False).count(),
    })


def api_san_pham_ton_kho_cua_hang(request):
    """
    API: Lấy tồn kho sản phẩm của một cửa hàng cụ thể (dùng trong trang đặt hàng để 
    hiển thị kho cửa hàng gần nhất).
    GET ?cua_hang_id=<id>&san_pham_ids=1,2,3
    """
    try:
        cua_hang_id = int(request.GET.get('cua_hang_id', ''))
    except (ValueError, TypeError):
        return JsonResponse({'loi': 'Thiếu cua_hang_id'}, status=400)

    from products.models import TonKho
    sp_ids_raw = request.GET.get('san_pham_ids', '')
    sp_ids = [int(x) for x in sp_ids_raw.split(',') if x.strip().isdigit()]

    qs = TonKho.objects.filter(cua_hang_id=cua_hang_id).select_related('san_pham')
    if sp_ids:
        qs = qs.filter(san_pham_id__in=sp_ids)

    result = []
    for tk in qs:
        result.append({
            'san_pham_id':  tk.san_pham_id,
            'ten':          tk.san_pham.ten,
            'so_luong':     tk.so_luong,
            'canh_bao':     tk.can_canh_bao,
            'vi_tri_ke':    tk.vi_tri_ke,
        })

    return JsonResponse({'ton_kho': result, 'cua_hang_id': cua_hang_id})


def api_isochrone_simple(request):
    """
    API: Tính vùng đẳng thời đơn giản (isochrone) dựa trên thời gian đi xe máy.
    Dùng công thức gần đúng: tốc độ TB xe máy TP.HCM ≈ 20 km/h.
    GET ?cua_hang_id=<id>&phut=15
    Trả về polygon GeoJSON gần đúng (circle với bán kính điều chỉnh theo giờ cao điểm).
    """
    try:
        cua_hang_id = int(request.GET.get('cua_hang_id', ''))
        phut = float(request.GET.get('phut', 15))
    except (ValueError, TypeError):
        return JsonResponse({'loi': 'Tham số không hợp lệ'}, status=400)

    phut = max(5, min(phut, 60))
    cua_hang = get_object_or_404(CuaHang, pk=cua_hang_id)

    if not cua_hang.vi_tri:
        return JsonResponse({'loi': 'Cửa hàng chưa có GPS'}, status=404)

    import math
    from django.utils import timezone

    # Tốc độ trung bình tùy giờ (km/h)
    gio_hien_tai = timezone.now().astimezone().hour
    # Giờ cao điểm sáng 7-9, chiều 17-19 → tốc độ thấp hơn
    if 7 <= gio_hien_tai <= 9 or 17 <= gio_hien_tai <= 19:
        van_toc_kmh = 15  # giờ cao điểm
        mo_ta_gio = 'giờ cao điểm'
    elif 22 <= gio_hien_tai or gio_hien_tai <= 5:
        van_toc_kmh = 30  # ban đêm
        mo_ta_gio = 'ban đêm'
    else:
        van_toc_kmh = 20  # bình thường
        mo_ta_gio = 'bình thường'

    ban_kinh_km = (van_toc_kmh * phut) / 60.0
    ban_kinh_m  = int(ban_kinh_km * 1000)

    # Tạo polygon gần đúng (32-điểm circle)
    vi_do_c  = cua_hang.vi_tri.y
    kinh_do_c = cua_hang.vi_tri.x
    # 1 độ kinh ≈ 111.32 km; 1 độ vĩ ≈ 110.57 km
    r_lat = ban_kinh_km / 110.57
    r_lng = ban_kinh_km / (111.32 * math.cos(math.radians(vi_do_c)))

    coords = []
    for i in range(33):
        angle = math.radians(i * (360 / 32))
        coords.append([
            round(kinh_do_c + r_lng * math.cos(angle), 6),
            round(vi_do_c   + r_lat * math.sin(angle), 6),
        ])

    polygon_geojson = {
        'type': 'Feature',
        'geometry': {'type': 'Polygon', 'coordinates': [coords]},
        'properties': {
            'cua_hang_id':   cua_hang_id,
            'ten':           cua_hang.ten,
            'phut':          int(phut),
            'ban_kinh_km':   round(ban_kinh_km, 2),
            'ban_kinh_m':    ban_kinh_m,
            'van_toc_kmh':   van_toc_kmh,
            'mo_ta_gio':     mo_ta_gio,
            'trung_tam':     [kinh_do_c, vi_do_c],
        }
    }

    return JsonResponse({'isochrone': polygon_geojson})


def api_tat_ca_cua_hang_json(request):
    """
    API JSON: Trả về tất cả cửa hàng đang hoạt động với tọa độ.
    Dùng bởi widget GIS trên trang đặt hàng.
    """
    cua_hangs = CuaHang.objects.filter(dang_hoat_dong=True).order_by('tinh_thanh', 'ten')
    data = []
    for ch in cua_hangs:
        data.append({
            'id':          ch.pk,
            'ten':         ch.ten,
            'dia_chi':     ch.dia_chi,
            'quan_huyen':  ch.quan_huyen,
            'tinh_thanh':  ch.tinh_thanh,
            'so_dien_thoai': ch.so_dien_thoai,
            'gio_mo':      str(ch.gio_mo_cua),
            'gio_dong':    str(ch.gio_dong_cua),
            'vi_do':       ch.vi_tri.y if ch.vi_tri else None,
            'kinh_do':     ch.vi_tri.x if ch.vi_tri else None,
            'co_gps':      bool(ch.vi_tri),
        })
    return JsonResponse({'cua_hangs': data, 'tong': len(data)})
