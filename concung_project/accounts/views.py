from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import DangKyForm, DangNhapForm, CapNhatHoSoForm
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
    return render(request, 'accounts/quan_ly_nguoi_dung.html', {'nguoi_dungs': nguoi_dungs})
