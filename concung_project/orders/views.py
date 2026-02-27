"""
orders/views.py  —  Con Cưng
Đặt hàng, giỏ hàng, theo dõi đơn, hủy đơn, quản lý admin
"""
import traceback
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Q

from .models import DonHang, ChiTietDonHang, GioHang, LichSuTrangThai
from products.models import SanPham, TonKho


# ════════════════════════════════════════════════════════════════
#  GIỎ HÀNG
# ════════════════════════════════════════════════════════════════

@login_required
def xem_gio_hang(request):
    items = GioHang.objects.filter(nguoi_dung=request.user).select_related('san_pham')
    tong_tien = sum(item.thanh_tien for item in items)
    return render(request, 'orders/gio_hang.html', {
        'items': items,
        'tong_tien': tong_tien,
    })


@login_required
def them_vao_gio(request, san_pham_id):
    san_pham = get_object_or_404(SanPham, pk=san_pham_id, dang_ban=True)
    try:
        so_luong = max(1, int(request.POST.get('so_luong', 1)))
    except (ValueError, TypeError):
        so_luong = 1

    item, created = GioHang.objects.get_or_create(
        nguoi_dung=request.user,
        san_pham=san_pham,
        defaults={'so_luong': so_luong},
    )
    if not created:
        item.so_luong += so_luong
        item.save()

    messages.success(request, f'✅ Đã thêm "{san_pham.ten}" vào giỏ hàng!')
    return redirect(request.META.get('HTTP_REFERER', 'danh_sach_san_pham'))


@login_required
def cap_nhat_gio(request, item_id):
    item = get_object_or_404(GioHang, pk=item_id, nguoi_dung=request.user)
    try:
        so_luong = int(request.POST.get('so_luong', 1))
    except (ValueError, TypeError):
        so_luong = 1

    if so_luong <= 0:
        item.delete()
        messages.info(request, 'Đã xóa sản phẩm khỏi giỏ hàng.')
    else:
        item.so_luong = so_luong
        item.save()
    return redirect('xem_gio_hang')


@login_required
def xoa_khoi_gio(request, item_id):
    item = get_object_or_404(GioHang, pk=item_id, nguoi_dung=request.user)
    ten_sp = item.san_pham.ten
    item.delete()
    messages.info(request, f'Đã xóa "{ten_sp}" khỏi giỏ hàng.')
    return redirect('xem_gio_hang')


# ════════════════════════════════════════════════════════════════
#  ĐẶT HÀNG  (FIX CHÍNH: evaluate items trước, Decimal safe)
# ════════════════════════════════════════════════════════════════

@login_required
def dat_hang(request):
    from stores.models import CuaHang

    # ── Evaluate queryset thành list ngay lập tức ──────────────
    items_qs = GioHang.objects.filter(nguoi_dung=request.user).select_related('san_pham')
    if not items_qs.exists():
        messages.warning(request, 'Giỏ hàng của bạn đang trống.')
        return redirect('danh_sach_san_pham')

    # Evaluate to list để không bị ảnh hưởng khi delete giỏ hàng
    items = list(items_qs)
    cua_hangs = CuaHang.objects.filter(dang_hoat_dong=True).order_by('tinh_thanh', 'ten')

    # Tính tổng tiền với Decimal an toàn
    tong_tien = sum(
        Decimal(str(item.san_pham.gia_hien_thi)) * item.so_luong
        for item in items
    )
    form_errors = {}

    if request.method == 'POST':
        phuong_thuc_giao  = request.POST.get('phuong_thuc_giao', 'giao_tan_noi')
        ho_ten            = request.POST.get('ho_ten', '').strip()
        so_dien_thoai     = request.POST.get('so_dien_thoai', '').strip()
        dia_chi_post      = request.POST.get('dia_chi', '').strip()
        cua_hang_id_raw   = request.POST.get('cua_hang', '').strip()
        thanh_toan        = request.POST.get('thanh_toan', 'tien_mat')
        ghi_chu           = request.POST.get('ghi_chu', '').strip()

        # ── Validate ──────────────────────────────────────────
        if not ho_ten:
            form_errors['ho_ten'] = 'Vui lòng nhập họ tên người nhận.'
        if not so_dien_thoai:
            form_errors['so_dien_thoai'] = 'Vui lòng nhập số điện thoại.'

        cua_hang_id  = None
        dia_chi_giao = ''

        if phuong_thuc_giao == 'nhan_tai_cua_hang':
            if not cua_hang_id_raw or not cua_hang_id_raw.isdigit():
                form_errors['cua_hang'] = 'Vui lòng chọn cửa hàng nhận hàng.'
            else:
                cua_hang_id = int(cua_hang_id_raw)
                try:
                    ch_obj = CuaHang.objects.get(pk=cua_hang_id, dang_hoat_dong=True)
                    dia_chi_giao = f'Nhận tại cửa hàng: {ch_obj.ten} — {ch_obj.dia_chi}'
                except CuaHang.DoesNotExist:
                    form_errors['cua_hang'] = 'Cửa hàng không hợp lệ.'
        else:
            if not dia_chi_post:
                form_errors['dia_chi'] = 'Vui lòng nhập địa chỉ giao hàng.'
            else:
                dia_chi_giao = dia_chi_post

        if form_errors:
            return render(request, 'orders/dat_hang.html', {
                'items':       items,
                'tong_tien':   tong_tien,
                'cua_hangs':   cua_hangs,
                'nguoi_dung':  request.user,
                'form_errors': form_errors,
                'post_data':   request.POST,
            })

        # ── Lưu đơn hàng trong transaction ────────────────────
        try:
            with transaction.atomic():
                phi_ship = Decimal('30000') if phuong_thuc_giao == 'giao_tan_noi' else Decimal('0')

                don_hang = DonHang.objects.create(
                    khach_hang              = request.user,
                    cua_hang_id             = cua_hang_id,
                    ho_ten_nguoi_nhan       = ho_ten,
                    so_dien_thoai_nhan      = so_dien_thoai,
                    dia_chi_giao_hang       = dia_chi_giao if dia_chi_giao else 'Nhận tại cửa hàng',
                    phuong_thuc_giao        = phuong_thuc_giao,
                    phuong_thuc_thanh_toan  = thanh_toan,
                    tong_tien_san_pham      = tong_tien,
                    phi_giao_hang           = phi_ship,
                    ghi_chu                 = ghi_chu,
                )

                # Lịch sử khởi tạo
                LichSuTrangThai.objects.create(
                    don_hang        = don_hang,
                    trang_thai_cu   = 'cho_xac_nhan',
                    trang_thai_moi  = 'cho_xac_nhan',
                    ghi_chu         = 'Đơn hàng được tạo bởi khách hàng',
                    nguoi_thuc_hien = request.user,
                )

                # Chi tiết sản phẩm + trừ tồn kho (items đã là list)
                for item in items:
                    gia = Decimal(str(item.san_pham.gia_hien_thi))
                    ChiTietDonHang.objects.create(
                        don_hang          = don_hang,
                        san_pham          = item.san_pham,
                        so_luong          = item.so_luong,
                        gia_tai_thoi_diem = gia,
                    )
                    if cua_hang_id:
                        tk = TonKho.objects.filter(
                            san_pham=item.san_pham,
                            cua_hang_id=cua_hang_id,
                        ).first()
                        if tk and tk.so_luong >= item.so_luong:
                            tk.so_luong -= item.so_luong
                            tk.save()

                # Xóa giỏ hàng sau khi tất cả đã lưu
                GioHang.objects.filter(nguoi_dung=request.user).delete()

            # Redirect ngoài transaction để tránh commit bị hoãn
            messages.success(
                request,
                f'🎉 Đặt hàng thành công! Mã đơn: <strong>{don_hang.ma_don_hang}</strong>'
            )
            return redirect('theo_doi_don_hang', ma=don_hang.ma_don_hang)

        except Exception as exc:
            traceback.print_exc()  # ghi log console server
            messages.error(
                request,
                f'❌ Lỗi tạo đơn hàng: {str(exc)[:300]} — Vui lòng thử lại hoặc gọi 1800 6996.'
            )

    return render(request, 'orders/dat_hang.html', {
        'items':      items,
        'tong_tien':  tong_tien,
        'cua_hangs':  cua_hangs,
        'nguoi_dung': request.user,
    })


# ════════════════════════════════════════════════════════════════
#  ĐƠN HÀNG CỦA TÔI
# ════════════════════════════════════════════════════════════════

@login_required
def don_hang_cua_toi(request):
    qs = DonHang.objects.filter(khach_hang=request.user).order_by('-ngay_tao')

    tt = request.GET.get('tt', '').strip()
    if tt:
        qs = qs.filter(trang_thai=tt)

    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(ma_don_hang__icontains=q)

    all_qs = DonHang.objects.filter(khach_hang=request.user)
    tong_don       = all_qs.count()
    don_da_giao    = all_qs.filter(trang_thai='da_giao').count()
    don_dang_xu_ly = all_qs.filter(
        trang_thai__in=['cho_xac_nhan', 'da_xac_nhan', 'dang_dong_goi',
                        'ban_giao_van_chuyen', 'dang_giao']
    ).count()
    don_huy = all_qs.filter(trang_thai='huy').count()

    paginator = Paginator(qs, 8)
    don_hangs = paginator.get_page(request.GET.get('page', 1))

    for dh in don_hangs:
        dh.timeline_steps = _build_timeline(dh)

    return render(request, 'orders/don_hang_cua_toi.html', {
        'don_hangs':       don_hangs,
        'trang_thai_loc':  tt,
        'tu_khoa':         q,
        'tong_don':        tong_don,
        'don_da_giao':     don_da_giao,
        'don_dang_xu_ly':  don_dang_xu_ly,
        'don_huy':         don_huy,
        'TRANG_THAI':      DonHang.TRANG_THAI,
    })


# ════════════════════════════════════════════════════════════════
#  THEO DÕI CHI TIẾT
# ════════════════════════════════════════════════════════════════

def theo_doi_don_hang(request, ma):
    don_hang = get_object_or_404(DonHang, ma_don_hang=ma)

    if request.user.is_authenticated:
        if don_hang.khach_hang != request.user and not request.user.la_nhan_vien:
            messages.error(request, 'Bạn không có quyền xem đơn hàng này.')
            return redirect('trang_chu')

    lich_su   = don_hang.lich_su_trang_thais.all().order_by('thoi_gian')
    chi_tiets = don_hang.chi_tiets.select_related('san_pham').all()
    timeline  = _build_timeline_full(don_hang, lich_su)

    return render(request, 'orders/theo_doi.html', {
        'don_hang':       don_hang,
        'lich_su':        lich_su,
        'chi_tiets':      chi_tiets,
        'timeline_steps': timeline,
    })


# ════════════════════════════════════════════════════════════════
#  HỦY ĐƠN (khách hàng)
# ════════════════════════════════════════════════════════════════

@login_required
def huy_don_hang(request, pk):
    don_hang = get_object_or_404(DonHang, pk=pk, khach_hang=request.user)
    if don_hang.trang_thai != 'cho_xac_nhan':
        messages.error(request, 'Chỉ có thể hủy đơn đang ở trạng thái "Chờ xác nhận".')
        return redirect('theo_doi_don_hang', ma=don_hang.ma_don_hang)

    if request.method == 'POST':
        cu = don_hang.trang_thai
        don_hang.trang_thai = 'huy'
        don_hang.save()
        LichSuTrangThai.objects.create(
            don_hang=don_hang,
            trang_thai_cu=cu,
            trang_thai_moi='huy',
            ghi_chu='Khách hàng chủ động hủy đơn',
            nguoi_thuc_hien=request.user,
        )
        messages.success(request, f'Đã hủy đơn hàng #{don_hang.ma_don_hang}.')
        return redirect('don_hang_cua_toi')

    return redirect('theo_doi_don_hang', ma=don_hang.ma_don_hang)


# ════════════════════════════════════════════════════════════════
#  QUẢN LÝ ĐƠN HÀNG (nhân viên / admin)
# ════════════════════════════════════════════════════════════════

@login_required
def quan_ly_don_hang(request):
    if not request.user.la_nhan_vien:
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('trang_chu')

    qs = DonHang.objects.select_related('khach_hang', 'cua_hang').all()

    trang_thai = request.GET.get('trang_thai', '').strip()
    if trang_thai:
        qs = qs.filter(trang_thai=trang_thai)

    if not request.user.la_admin and hasattr(request.user, 'nhan_vien'):
        qs = qs.filter(cua_hang=request.user.nhan_vien.cua_hang)

    paginator = Paginator(qs.order_by('-ngay_tao'), 20)
    return render(request, 'orders/quan_ly.html', {
        'don_hangs':           paginator.get_page(request.GET.get('page', 1)),
        'trang_thai_hien_tai': trang_thai,
        'TRANG_THAI':          DonHang.TRANG_THAI,
    })


@login_required
def cap_nhat_trang_thai(request, pk):
    if not request.user.la_nhan_vien:
        return JsonResponse({'success': False, 'loi': 'Không có quyền'}, status=403)

    don_hang       = get_object_or_404(DonHang, pk=pk)
    trang_thai_moi = request.POST.get('trang_thai', '').strip()
    ghi_chu        = request.POST.get('ghi_chu', '').strip()
    ma_van_don     = request.POST.get('ma_van_don', '').strip()

    if trang_thai_moi:
        cu = don_hang.trang_thai
        don_hang.trang_thai = trang_thai_moi
        if ma_van_don:
            don_hang.ma_van_don = ma_van_don
        don_hang.save()
        LichSuTrangThai.objects.create(
            don_hang=don_hang,
            trang_thai_cu=cu,
            trang_thai_moi=trang_thai_moi,
            ghi_chu=ghi_chu,
            nguoi_thuc_hien=request.user,
        )
        messages.success(request, f'Đã cập nhật trạng thái đơn #{don_hang.ma_don_hang}!')

    return redirect('quan_ly_don_hang')


# ════════════════════════════════════════════════════════════════
#  HELPER: Xây dựng timeline
# ════════════════════════════════════════════════════════════════

_STEPS = [
    ('cho_xac_nhan',        '⏳', 'Chờ xác nhận'),
    ('da_xac_nhan',         '✔️',  'Đã xác nhận'),
    ('dang_dong_goi',       '📦',  'Đóng gói'),
    ('ban_giao_van_chuyen', '🏷️',  'Bàn giao VC'),
    ('dang_giao',           '🚚',  'Đang giao'),
    ('da_giao',             '🎉',  'Đã giao'),
]
_IDX = {s[0]: i for i, s in enumerate(_STEPS)}


def _build_timeline(don_hang):
    ts  = don_hang.trang_thai
    cur = _IDX.get(ts, -1)
    result = []
    for i, (key, icon, label) in enumerate(_STEPS):
        if ts == 'huy':
            cls = 'canceled' if i == 0 else 'pending'
        elif i < cur:
            cls = 'done'
        elif i == cur:
            cls = 'active'
        else:
            cls = 'pending'
        result.append({'key': key, 'icon': icon, 'label': label, 'class': cls})
    return result


def _build_timeline_full(don_hang, lich_su):
    ts  = don_hang.trang_thai
    cur = _IDX.get(ts, -1)

    time_map = {}
    for ls in lich_su:
        if ls.trang_thai_moi not in time_map:
            time_map[ls.trang_thai_moi] = ls.thoi_gian

    result = []
    for i, (key, icon, label) in enumerate(_STEPS):
        if ts == 'huy':
            cls = 'done' if i == 0 else 'pending'
        elif i < cur:
            cls = 'done'
        elif i == cur:
            cls = 'active'
        else:
            cls = 'pending'

        t = time_map.get(key)
        if key == 'cho_xac_nhan' and not t:
            t = don_hang.ngay_tao

        result.append({
            'key':   key,
            'icon':  icon,
            'label': label,
            'class': cls,
            'time':  t.strftime('%d/%m/%Y %H:%M') if t else None,
            'note':  None,
        })
    return result