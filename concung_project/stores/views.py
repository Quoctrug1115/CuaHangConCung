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