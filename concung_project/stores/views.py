from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import CuaHang, NhanVien, CaLamViec
from .forms import CuaHangForm, NhanVienForm
from products.models import TonKho


def danh_sach_cua_hang(request):
    """Trang danh sách cửa hàng - public"""
    qs = CuaHang.objects.filter(dang_hoat_dong=True).order_by('tinh_thanh', 'ten')

    # Lọc theo tỉnh/thành
    tinh = request.GET.get('tinh', '').strip()
    if tinh:
        qs = qs.filter(tinh_thanh=tinh)

    # Tìm kiếm
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(ten__icontains=q) | Q(dia_chi__icontains=q) | Q(ma_cua_hang__icontains=q))

    # Danh sách tỉnh/thành duy nhất
    tinh_thanhs = CuaHang.objects.filter(dang_hoat_dong=True)\
        .values_list('tinh_thanh', flat=True).distinct().order_by('tinh_thanh')

    tong_cua_hang = CuaHang.objects.filter(dang_hoat_dong=True).count()
    so_tinh_thanh = len(tinh_thanhs)
    tong_nhan_vien = NhanVien.objects.filter(dang_lam_viec=True).count()

    return render(request, 'stores/danh_sach.html', {
        'cua_hangs':     qs,
        'tinh_thanhs':   tinh_thanhs,
        'tinh_hien_tai': tinh,
        'tu_khoa':       q,
        'tong_cua_hang': tong_cua_hang,
        'so_tinh_thanh': so_tinh_thanh,
        'tong_nhan_vien': tong_nhan_vien,
    })


def chi_tiet_cua_hang(request, pk):
    """Chi tiết một cửa hàng"""
    cua_hang  = get_object_or_404(CuaHang, pk=pk)
    nhan_viens = NhanVien.objects.filter(cua_hang=cua_hang, dang_lam_viec=True)\
        .select_related('nguoi_dung')
    ton_khos  = TonKho.objects.filter(cua_hang=cua_hang)\
        .select_related('san_pham').order_by('san_pham__ten')[:30]

    return render(request, 'stores/chi_tiet.html', {
        'cua_hang':  cua_hang,
        'nhan_viens': nhan_viens,
        'ton_khos':  ton_khos,
    })


@login_required
def quan_ly_cua_hang(request):
    """Admin: Quản lý danh sách cửa hàng"""
    if not request.user.la_quan_ly:
        messages.error(request, 'Bạn không có quyền truy cập.')
        return redirect('trang_chu')

    qs = CuaHang.objects.all().order_by('tinh_thanh', 'ten')

    # Tìm kiếm
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(ten__icontains=q) | Q(ma_cua_hang__icontains=q) | Q(dia_chi__icontains=q))

    # Lọc tỉnh
    tinh = request.GET.get('tinh', '').strip()
    if tinh:
        qs = qs.filter(tinh_thanh=tinh)

    tinh_thanhs = CuaHang.objects.values_list('tinh_thanh', flat=True).distinct().order_by('tinh_thanh')

    paginator = Paginator(qs, 15)
    cua_hangs = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'stores/quan_ly.html', {
        'cua_hangs':    cua_hangs,
        'tu_khoa':      q,
        'tinh_loc':     tinh,
        'tinh_thanhs':  tinh_thanhs,
        'tong_ch':      CuaHang.objects.count(),
        'so_hoat_dong': CuaHang.objects.filter(dang_hoat_dong=True).count(),
        'so_co_gps':    CuaHang.objects.filter(vi_tri__isnull=False).count(),
    })


@login_required
def them_cua_hang(request):
    """Admin: Thêm cửa hàng"""
    if not request.user.la_quan_ly:
        messages.error(request, 'Bạn không có quyền truy cập.')
        return redirect('trang_chu')

    if request.method == 'POST':
        form = CuaHangForm(request.POST)
        if form.is_valid():
            cua_hang = form.save()
            messages.success(request, f'✅ Đã thêm cửa hàng "{cua_hang.ten}" thành công!')
            return redirect('chi_tiet_cua_hang', pk=cua_hang.pk)
        else:
            messages.error(request, 'Có lỗi trong form. Vui lòng kiểm tra lại.')
    else:
        form = CuaHangForm()

    return render(request, 'stores/form_cua_hang.html', {
        'form': form, 'tieu_de': 'Thêm cửa hàng mới'
    })


@login_required
def sua_cua_hang(request, pk):
    """Admin: Sửa thông tin cửa hàng"""
    if not request.user.la_quan_ly:
        messages.error(request, 'Bạn không có quyền truy cập.')
        return redirect('trang_chu')

    cua_hang = get_object_or_404(CuaHang, pk=pk)

    if request.method == 'POST':
        form = CuaHangForm(request.POST, instance=cua_hang)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ Đã cập nhật cửa hàng "{cua_hang.ten}"!')
            return redirect('chi_tiet_cua_hang', pk=cua_hang.pk)
        else:
            messages.error(request, 'Có lỗi trong form. Vui lòng kiểm tra lại.')
    else:
        form = CuaHangForm(instance=cua_hang)

    return render(request, 'stores/form_cua_hang.html', {
        'form': form, 'tieu_de': f'Sửa: {cua_hang.ten}'
    })


@login_required
def xoa_cua_hang(request, pk):
    """Admin: Vô hiệu hóa cửa hàng (xóa mềm)"""
    if not request.user.la_admin:
        messages.error(request, 'Chỉ quản trị viên mới có thể thực hiện thao tác này.')
        return redirect('quan_ly_cua_hang')

    cua_hang = get_object_or_404(CuaHang, pk=pk)
    if request.method == 'POST':
        cua_hang.dang_hoat_dong = False
        cua_hang.save()
        messages.success(request, f'Đã vô hiệu hóa cửa hàng "{cua_hang.ten}".')
        return redirect('quan_ly_cua_hang')

    return render(request, 'stores/xac_nhan_xoa.html', {'cua_hang': cua_hang})


@login_required
def quan_ly_nhan_vien(request):
    """Admin: Quản lý nhân viên"""
    if not request.user.la_quan_ly:
        messages.error(request, 'Bạn không có quyền truy cập.')
        return redirect('trang_chu')

    nhan_viens = NhanVien.objects.select_related('nguoi_dung', 'cua_hang').filter(dang_lam_viec=True)

    if not request.user.la_admin and hasattr(request.user, 'nhan_vien'):
        nhan_viens = nhan_viens.filter(cua_hang=request.user.nhan_vien.cua_hang)

    paginator = Paginator(nhan_viens, 15)
    return render(request, 'stores/quan_ly_nhan_vien.html', {
        'nhan_viens': paginator.get_page(request.GET.get('page', 1))
    })

@login_required
def chi_tiet_nhan_vien(request, pk):
    """Admin: Xem chi tiết nhân viên"""
    if not request.user.la_quan_ly:
        messages.error(request, 'Bạn không có quyền truy cập.')
        return redirect('trang_chu')

    # Dùng select_related để tối ưu truy vấn (join bảng NguoiDung và CuaHang)
    nv = get_object_or_404(NhanVien.objects.select_related('nguoi_dung', 'cua_hang'), pk=pk)

    return render(request, 'stores/chi_tiet_nhan_vien.html', {
        'nv': nv,
        'tieu_de': f'Hồ sơ: {nv.nguoi_dung.get_full_name() or nv.nguoi_dung.username}'
    })
# ════════════════════════════════════════════════════════════════════════
#  NHÂN VIÊN CRUD
# ════════════════════════════════════════════════════════════════════════

@login_required
def them_nhan_vien(request):
    """Admin: Thêm nhân viên mới — tạo NguoiDung + NhanVien cùng lúc"""
    if not request.user.la_quan_ly:
        messages.error(request, 'Bạn không có quyền truy cập.')
        return redirect('trang_chu')

    from accounts.models import NguoiDung

    cua_hangs = CuaHang.objects.filter(dang_hoat_dong=True).order_by('ten')
    errors = {}

    if request.method == 'POST':
        p = request.POST

        # ── Validate NguoiDung fields ──────────────────────────────
        username = p.get('username', '').strip()
        email    = p.get('email', '').strip()
        pw1      = p.get('password1', '')
        pw2      = p.get('password2', '')
        last_name  = p.get('last_name', '').strip()
        first_name = p.get('first_name', '').strip()
        so_dt      = p.get('so_dien_thoai', '').strip()

        if not username:
            errors['username'] = 'Vui lòng nhập tên đăng nhập.'
        elif NguoiDung.objects.filter(username=username).exists():
            errors['username'] = f'Tên đăng nhập "{username}" đã tồn tại.'
        if not pw1:
            errors['password1'] = 'Vui lòng nhập mật khẩu.'
        elif pw1 != pw2:
            errors['password'] = 'Mật khẩu xác nhận không khớp.'
        elif len(pw1) < 6:
            errors['password1'] = 'Mật khẩu phải có ít nhất 6 ký tự.'
        if not last_name:
            errors['last_name'] = 'Vui lòng nhập họ.'
        if not first_name:
            errors['first_name'] = 'Vui lòng nhập tên.'

        # ── Validate NhanVien fields ──────────────────────────────
        ma_nv       = p.get('ma_nhan_vien', '').strip()
        chuc_vu     = p.get('chuc_vu', '').strip()
        ngay_vao    = p.get('ngay_vao_lam', '').strip()
        luong       = p.get('luong_co_ban', '').strip()
        cua_hang_id = p.get('cua_hang', '').strip()
        dang_lam    = p.get('dang_lam_viec') == 'on'

        if not ma_nv:
            errors['ma_nhan_vien'] = 'Vui lòng nhập mã nhân viên.'
        elif NhanVien.objects.filter(ma_nhan_vien=ma_nv).exists():
            errors['ma_nhan_vien'] = f'Mã nhân viên "{ma_nv}" đã tồn tại.'
        if not chuc_vu:
            errors['chuc_vu'] = 'Vui lòng chọn chức vụ.'
        if not ngay_vao:
            errors['ngay_vao_lam'] = 'Vui lòng nhập ngày vào làm.'
        if not luong:
            errors['luong_co_ban'] = 'Vui lòng nhập lương cơ bản.'

        if not errors:
            # Tạo NguoiDung
            nd = NguoiDung.objects.create_user(
                username=username,
                email=email,
                password=pw1,
                last_name=last_name,
                first_name=first_name,
                vai_tro='nhan_vien',
                is_staff=True,
            )
            nd.so_dien_thoai = so_dt
            if 'anh_dai_dien' in request.FILES:
                nd.anh_dai_dien = request.FILES['anh_dai_dien']
            nd.save()

            # Tạo NhanVien
            nv = NhanVien(
                nguoi_dung=nd,
                ma_nhan_vien=ma_nv,
                chuc_vu=chuc_vu,
                ngay_vao_lam=ngay_vao,
                luong_co_ban=luong or 0,
                dang_lam_viec=dang_lam,
            )
            if cua_hang_id:
                nv.cua_hang_id = int(cua_hang_id)
            nv.save()

            messages.success(request, f'✅ Đã thêm nhân viên "{nd.get_full_name()}" ({ma_nv}) thành công!')
            return redirect('quan_ly_nhan_vien')

    return render(request, 'stores/form_nhan_vien.html', {
        'nhan_vien': None,
        'cua_hangs': cua_hangs,
        'chuc_vu_choices': NhanVien.CHUC_VU,
        'errors': errors,
    })


@login_required
def sua_nhan_vien(request, pk):
    """Admin: Sửa thông tin nhân viên"""
    if not request.user.la_quan_ly:
        messages.error(request, 'Bạn không có quyền truy cập.')
        return redirect('trang_chu')

    nv = get_object_or_404(
        NhanVien.objects.select_related('nguoi_dung', 'cua_hang'), pk=pk
    )
    cua_hangs = CuaHang.objects.filter(dang_hoat_dong=True).order_by('ten')
    errors = {}

    if request.method == 'POST':
        p = request.POST
        nd = nv.nguoi_dung

        # Cập nhật NguoiDung
        nd.last_name  = p.get('last_name', '').strip()
        nd.first_name = p.get('first_name', '').strip()
        nd.email      = p.get('email', '').strip()
        nd.so_dien_thoai = p.get('so_dien_thoai', '').strip()
        if 'anh_dai_dien' in request.FILES:
            nd.anh_dai_dien = request.FILES['anh_dai_dien']

        if not nd.last_name:
            errors['last_name'] = 'Vui lòng nhập họ.'
        if not nd.first_name:
            errors['first_name'] = 'Vui lòng nhập tên.'

        # Cập nhật NhanVien
        ma_nv    = p.get('ma_nhan_vien', '').strip()
        chuc_vu  = p.get('chuc_vu', '').strip()
        ngay_vao = p.get('ngay_vao_lam', '').strip()
        luong    = p.get('luong_co_ban', '').strip()
        ch_id    = p.get('cua_hang', '').strip()
        dang_lam = p.get('dang_lam_viec') == 'on'

        if not ma_nv:
            errors['ma_nhan_vien'] = 'Vui lòng nhập mã nhân viên.'
        elif NhanVien.objects.filter(ma_nhan_vien=ma_nv).exclude(pk=pk).exists():
            errors['ma_nhan_vien'] = f'Mã "{ma_nv}" đã được dùng bởi nhân viên khác.'
        if not chuc_vu:
            errors['chuc_vu'] = 'Vui lòng chọn chức vụ.'
        if not ngay_vao:
            errors['ngay_vao_lam'] = 'Vui lòng nhập ngày vào làm.'

        if not errors:
            nd.save()

            nv.ma_nhan_vien = ma_nv
            nv.chuc_vu      = chuc_vu
            nv.ngay_vao_lam = ngay_vao
            nv.luong_co_ban = luong or 0
            nv.dang_lam_viec = dang_lam
            nv.cua_hang_id  = int(ch_id) if ch_id else None
            nv.save()

            messages.success(request, f'✅ Đã cập nhật thông tin nhân viên "{nd.get_full_name()}"!')
            return redirect('quan_ly_nhan_vien')

    return render(request, 'stores/form_nhan_vien.html', {
        'nhan_vien': nv,
        'cua_hangs': cua_hangs,
        'chuc_vu_choices': NhanVien.CHUC_VU,
        'errors': errors,
    })


@login_required
def xoa_nhan_vien(request, pk):
    """Admin: Vô hiệu hoá nhân viên (soft delete)"""
    if not request.user.la_quan_ly:
        messages.error(request, 'Bạn không có quyền truy cập.')
        return redirect('trang_chu')

    nv = get_object_or_404(NhanVien.objects.select_related('nguoi_dung'), pk=pk)

    if request.method == 'POST':
        nv.dang_lam_viec = False
        nv.save()
        messages.success(request, f'Đã vô hiệu hoá nhân viên "{nv.nguoi_dung.get_full_name()}".')
        return redirect('quan_ly_nhan_vien')

    return render(request, 'stores/xac_nhan_xoa_nv.html', {'nv': nv})
