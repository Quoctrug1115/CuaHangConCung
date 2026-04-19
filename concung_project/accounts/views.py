from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .forms import DangKyForm, DangNhapForm, CapNhatHoSoForm, AdminNguoiDungForm, DoiMatKhauAdminForm
from .models import NguoiDung


def dang_ky(request):
    """Đăng ký tài khoản khách hàng"""
    if request.user.is_authenticated:
        return redirect('trang_chu')

    if request.method == 'POST':
        form = DangKyForm(request.POST)
        if form.is_valid():
            nguoi_dung = form.save(commit=False)
            nguoi_dung.vai_tro = 'khach_hang'
            nguoi_dung.save()
            login(request, nguoi_dung)
            messages.success(request, f'Chào mừng {nguoi_dung.username} đã đăng ký thành công!')
            return redirect('trang_chu')
    else:
        form = DangKyForm()

    return render(request, 'accounts/dang_ky.html', {'form': form})


def dang_nhap(request):
    """Đăng nhập"""
    if request.user.is_authenticated:
        return redirect('trang_chu')

    if request.method == 'POST':
        form = DangNhapForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            nguoi_dung = authenticate(username=username, password=password)
            if nguoi_dung:
                login(request, nguoi_dung)
                next_url = request.GET.get('next', 'trang_chu')
                messages.success(request, f'Đăng nhập thành công! Xin chào {nguoi_dung.username}')
                return redirect(next_url)
        else:
            messages.error(request, 'Tên đăng nhập hoặc mật khẩu không đúng.')
    else:
        form = DangNhapForm()

    return render(request, 'accounts/dang_nhap.html', {'form': form})


@login_required
def dang_xuat(request):
    """Đăng xuất"""
    logout(request)
    messages.info(request, 'Bạn đã đăng xuất thành công.')
    return redirect('dang_nhap')


@login_required
def ho_so(request):
    """Xem và cập nhật hồ sơ"""
    if request.method == 'POST':
        form = CapNhatHoSoForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cập nhật hồ sơ thành công!')
            return redirect('ho_so')
    else:
        form = CapNhatHoSoForm(instance=request.user)

    return render(request, 'accounts/ho_so.html', {'form': form})


@login_required
def quan_ly_nguoi_dung(request):
    """Admin: Xem danh sách người dùng"""
    if not request.user.la_admin:
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('trang_chu')

    nguoi_dungs = NguoiDung.objects.all().order_by('-ngay_tao')

    # Stats cho template
    tong_nd = nguoi_dungs.count()
    so_admin = nguoi_dungs.filter(vai_tro='admin').count()
    dang_hoat_dong = nguoi_dungs.filter(is_active=True).count()
    so_khach = nguoi_dungs.filter(vai_tro='khach_hang').count()
    mot_tuan_truoc = timezone.now() - timezone.timedelta(days=7)
    moi_tuan = nguoi_dungs.filter(ngay_tao__gte=mot_tuan_truoc).count()

    return render(request, 'accounts/quan_ly_nguoi_dung.html', {
        'nguoi_dungs': nguoi_dungs,
        'tong_nd': tong_nd,
        'so_admin': so_admin,
        'dang_hoat_dong': dang_hoat_dong,
        'so_khach': so_khach,
        'moi_tuan': moi_tuan,
    })


@login_required
def them_nguoi_dung(request):
    """Admin: Thêm người dùng mới"""
    if not request.user.la_admin:
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('trang_chu')

    if request.method == 'POST':
        form = AdminNguoiDungForm(request.POST, request.FILES)
        if form.is_valid():
            nguoi_dung = form.save(commit=False)
            nguoi_dung.set_password(form.cleaned_data['password1'])
            nguoi_dung.save()
            messages.success(request, f'Đã tạo tài khoản "{nguoi_dung.username}" thành công!')
            return redirect('quan_ly_nguoi_dung')
        else:
            messages.error(request, 'Có lỗi trong form. Vui lòng kiểm tra lại.')
    else:
        form = AdminNguoiDungForm()

    return render(request, 'accounts/form_nguoi_dung.html', {
        'form': form,
        'tieu_de': 'Thêm người dùng mới',
        'la_them_moi': True,
        'vai_tros': NguoiDung.VAI_TRO,
    })


@login_required
def chi_tiet_nguoi_dung(request, pk):
    """Admin: Xem chi tiết người dùng"""
    if not request.user.la_admin:
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('trang_chu')

    nd = get_object_or_404(NguoiDung, pk=pk)
    return render(request, 'accounts/form_nguoi_dung.html', {
        'form': AdminNguoiDungForm(instance=nd),
        'tieu_de': f'Chi tiết: {nd.get_full_name() or nd.username}',
        'la_them_moi': False,
        'vai_tros': NguoiDung.VAI_TRO,
    })


@login_required
def sua_nguoi_dung(request, pk):
    """Admin: Sửa thông tin người dùng"""
    if not request.user.la_admin:
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('trang_chu')

    nd = get_object_or_404(NguoiDung, pk=pk)
    if request.method == 'POST':
        form = AdminNguoiDungForm(request.POST, request.FILES, instance=nd)
        if form.is_valid():
            form.save()
            messages.success(request, f'Đã cập nhật tài khoản "{nd.username}"!')
            return redirect('quan_ly_nguoi_dung')
        else:
            messages.error(request, 'Có lỗi trong form. Vui lòng kiểm tra lại.')
    else:
        form = AdminNguoiDungForm(instance=nd)

    return render(request, 'accounts/form_nguoi_dung.html', {
        'form': form,
        'tieu_de': f'Sửa: {nd.get_full_name() or nd.username}',
        'la_them_moi': False,
        'vai_tros': NguoiDung.VAI_TRO,
    })


@login_required
def xoa_nguoi_dung(request, pk):
    """Admin: Vô hiệu hóa tài khoản (xóa mềm)"""
    if not request.user.la_admin:
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('trang_chu')

    nd = get_object_or_404(NguoiDung, pk=pk)
    if nd == request.user:
        messages.error(request, 'Bạn không thể vô hiệu hóa tài khoản của chính mình.')
        return redirect('quan_ly_nguoi_dung')

    if request.method == 'POST':
        nd.is_active = False
        nd.save()
        messages.success(request, f'Đã vô hiệu hóa tài khoản "{nd.username}".')
        return redirect('quan_ly_nguoi_dung')

    return render(request, 'accounts/xac_nhan_xoa_nd.html', {'nd': nd})


@login_required
def doi_mat_khau_admin(request, pk):
    """Admin: Đặt lại mật khẩu cho người dùng bất kỳ"""
    if not request.user.la_admin:
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('trang_chu')

    nd = get_object_or_404(NguoiDung, pk=pk)
    if request.method == 'POST':
        form = DoiMatKhauAdminForm(request.POST)
        if form.is_valid():
            nd.set_password(form.cleaned_data['password1'])
            nd.save()
            messages.success(request, f'Đã đổi mật khẩu cho "{nd.username}"!')
            return redirect('sua_nguoi_dung', pk=nd.pk)
        else:
            messages.error(request, 'Mật khẩu không hợp lệ.')
    else:
        form = DoiMatKhauAdminForm()

    return render(request, 'accounts/doi_mat_khau_admin.html', {
        'form': form,
        'nd': nd,
        'tieu_de': f'Đổi mật khẩu: {nd.get_full_name() or nd.username}',
    })
