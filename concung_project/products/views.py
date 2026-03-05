from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import SanPham, DanhMuc, TonKho, LichSuKho
from .forms import SanPhamForm, TonKhoForm


def danh_sach_san_pham(request):
    """Trang danh sách sản phẩm (User)"""
    san_phams = SanPham.objects.filter(dang_ban=True)
    danh_mucs = DanhMuc.objects.all().order_by('thu_tu')

    danh_muc_id = request.GET.get('danh_muc')
    if danh_muc_id:
        san_phams = san_phams.filter(danh_muc_id=danh_muc_id)

    tu_khoa = request.GET.get('q', '').strip()
    if tu_khoa:
        san_phams = san_phams.filter(
            Q(ten__icontains=tu_khoa) |
            Q(ma_san_pham__icontains=tu_khoa) |
            Q(mo_ta_ngan__icontains=tu_khoa)
        )

    sap_xep = request.GET.get('sap_xep', '-ngay_tao')
    if sap_xep in ['gia_ban', '-gia_ban', '-ngay_tao', 'ten']:
        san_phams = san_phams.order_by(sap_xep)

    paginator = Paginator(san_phams, 12)
    page = request.GET.get('page', 1)

    return render(request, 'products/danh_sach.html', {
        'san_phams': paginator.get_page(page),
        'danh_mucs': danh_mucs,
        'tu_khoa': tu_khoa,
        'danh_muc_hien_tai': danh_muc_id,
    })


def chi_tiet_san_pham(request, pk):
    """Chi tiết sản phẩm - đầy đủ context"""
    san_pham = get_object_or_404(SanPham, pk=pk, dang_ban=True)
    ton_khos = TonKho.objects.filter(
        san_pham=san_pham, cua_hang__dang_hoat_dong=True
    ).select_related('cua_hang')

    san_pham_lien_quan = SanPham.objects.filter(
        danh_muc=san_pham.danh_muc, dang_ban=True
    ).exclude(pk=pk)[:8]

    # ── Đánh giá mẫu (demo) ──────────────────────────────
    danh_gias = [
        {
            'ten': 'Nguyễn Thị Lan',
            'ten_viet_tat': 'L',
            'sao': 5,
            'ngay': '20/02/2026',
            'noi_dung': 'Sản phẩm rất tốt, bé nhà mình dùng được 2 tháng rồi thấy hiệu quả rõ rệt. '
                        'Đóng gói cẩn thận, giao hàng nhanh. Sẽ ủng hộ tiếp.',
            'da_mua': True,
        },
        {
            'ten': 'Trần Minh Tuấn',
            'ten_viet_tat': 'T',
            'sao': 5,
            'ngay': '15/02/2026',
            'noi_dung': 'Mua về cho bé 8 tháng dùng. Chất lượng đúng như mô tả, hàng chính hãng '
                        '100%. Giá cả hợp lý, nhân viên tư vấn nhiệt tình.',
            'da_mua': True,
        },
        {
            'ten': 'Phạm Thu Hương',
            'ten_viet_tat': 'H',
            'sao': 4,
            'ngay': '10/02/2026',
            'noi_dung': 'Sản phẩm ok, bé chịu dùng. Giao hàng hơi lâu một chút nhưng chất lượng '
                        'sản phẩm rất ổn. Mình sẽ mua thêm khi hết.',
            'da_mua': True,
        },
        {
            'ten': 'Lê Thị Mai',
            'ten_viet_tat': 'M',
            'sao': 5,
            'ngay': '05/02/2026',
            'noi_dung': 'Mua lần thứ 3 rồi vẫn hài lòng. Con Cưng uy tín, hàng luôn đúng với mô '
                        'tả. Bé nhà mình rất thích.',
            'da_mua': True,
        },
    ]

    # ── Tổng quan đánh giá ────────────────────────────────
    danh_gia_summary = [
        {'sao': 5, 'so_luong': 98,  'pct': 77},
        {'sao': 4, 'so_luong': 22,  'pct': 17},
        {'sao': 3, 'so_luong': 5,   'pct': 4},
        {'sao': 2, 'so_luong': 2,   'pct': 1},
        {'sao': 1, 'so_luong': 1,   'pct': 1},
    ]

    # ── Cam kết Con Cưng ──────────────────────────────────
    cam_kets = [
        {'icon': '✅', 'tieu_de': 'Hàng chính hãng 100%',
         'mo_ta': 'Cam kết hàng thật, có tem nhãn đầy đủ'},
        {'icon': '🔄', 'tieu_de': 'Đổi trả trong 7 ngày',
         'mo_ta': 'Đổi trả miễn phí nếu sản phẩm lỗi'},
        {'icon': '🚚', 'tieu_de': 'Giao hàng toàn quốc',
         'mo_ta': 'Miễn phí cho đơn từ 500.000₫'},
        {'icon': '💳', 'tieu_de': 'Thanh toán đa dạng',
         'mo_ta': 'COD, chuyển khoản, thẻ tín dụng'},
        {'icon': '🎁', 'tieu_de': 'Tích điểm thành viên',
         'mo_ta': '1% giá trị đơn hàng quy đổi điểm'},
    ]

    return render(request, 'products/chi_tiet.html', {
        'san_pham': san_pham,
        'ton_khos': ton_khos,
        'san_pham_lien_quan': san_pham_lien_quan,
        'danh_gias': danh_gias,
        'danh_gia_summary': danh_gia_summary,
        'cam_kets': cam_kets,
    })


@login_required
def quan_ly_kho(request):
    if not request.user.la_nhan_vien:
        messages.error(request, 'Bạn không có quyền truy cập.')
        return redirect('trang_chu')

    ton_khos = TonKho.objects.select_related('san_pham', 'cua_hang').all()

    canh_bao = request.GET.get('canh_bao')
    if canh_bao:
        from django.db.models import F
        ton_khos = ton_khos.filter(so_luong__lte=F('so_luong_toi_thieu'))

    cua_hang_id = request.GET.get('cua_hang')
    if cua_hang_id:
        ton_khos = ton_khos.filter(cua_hang_id=cua_hang_id)

    paginator = Paginator(ton_khos, 20)
    page = request.GET.get('page', 1)

    from django.db.models import F
    so_canh_bao = TonKho.objects.filter(so_luong__lte=F('so_luong_toi_thieu')).count()

    return render(request, 'products/quan_ly_kho.html', {
        'ton_khos': paginator.get_page(page),
        'so_canh_bao': so_canh_bao,
    })


@login_required
def nhap_kho(request, ton_kho_id):
    if not request.user.la_nhan_vien:
        messages.error(request, 'Bạn không có quyền thực hiện.')
        return redirect('quan_ly_kho')

    ton_kho = get_object_or_404(TonKho, pk=ton_kho_id)

    if request.method == 'POST':
        so_luong = int(request.POST.get('so_luong', 0))
        ghi_chu = request.POST.get('ghi_chu', '')
        if so_luong > 0:
            so_luong_truoc = ton_kho.so_luong
            ton_kho.so_luong += so_luong
            ton_kho.save()
            LichSuKho.objects.create(
                ton_kho=ton_kho, loai='nhap',
                so_luong_thay_doi=so_luong,
                so_luong_truoc=so_luong_truoc,
                so_luong_sau=ton_kho.so_luong,
                ghi_chu=ghi_chu,
                nguoi_thuc_hien=request.user
            )
            messages.success(request, f'Đã nhập {so_luong} sản phẩm vào kho!')
        return redirect('quan_ly_kho')

    return render(request, 'products/nhap_kho.html', {'ton_kho': ton_kho})


@login_required
def quan_ly_san_pham(request):
    if not request.user.la_quan_ly:
        messages.error(request, 'Bạn không có quyền truy cập.')
        return redirect('trang_chu')

    san_phams = SanPham.objects.all().order_by('-ngay_tao')

    # Tìm kiếm
    q = request.GET.get('q', '').strip()
    if q:
        san_phams = san_phams.filter(
            Q(ten__icontains=q) | Q(ma_san_pham__icontains=q) | Q(thuong_hieu__icontains=q)
        )

    # Lọc danh mục
    danh_muc_id = request.GET.get('danh_muc', '').strip()
    if danh_muc_id:
        san_phams = san_phams.filter(danh_muc_id=danh_muc_id)

    # Lọc trạng thái
    dang_ban = request.GET.get('dang_ban', '').strip()
    if dang_ban == '1':
        san_phams = san_phams.filter(dang_ban=True)
    elif dang_ban == '0':
        san_phams = san_phams.filter(dang_ban=False)

    from django.db.models import F, Count
    tong_sp = SanPham.objects.count()
    dang_ban_count = SanPham.objects.filter(dang_ban=True).count()
    canh_bao = TonKho.objects.filter(so_luong__lte=F('so_luong_toi_thieu')).values('san_pham').distinct().count()
    het_hang = TonKho.objects.filter(so_luong=0).values('san_pham').distinct().count()
    so_danh_muc = DanhMuc.objects.count()

    paginator = Paginator(san_phams, 15)
    page = request.GET.get('page', 1)

    return render(request, 'products/quan_ly_san_pham.html', {
        'san_phams': paginator.get_page(page),
        'danh_mucs': DanhMuc.objects.all().order_by('thu_tu'),
        'tong_san_pham': tong_sp,
        'dang_ban': dang_ban_count,
        'canh_bao_kho': canh_bao,
        'het_hang': het_hang,
        'so_danh_muc': so_danh_muc,
    })


@login_required
def them_san_pham(request):
    if not request.user.la_quan_ly:
        return redirect('trang_chu')

    if request.method == 'POST':
        form = SanPhamForm(request.POST, request.FILES)
        if form.is_valid():
            sp = form.save()
            messages.success(request, f'Đã thêm sản phẩm "{sp.ten}"!')
            return redirect('quan_ly_san_pham')
    else:
        form = SanPhamForm()

    return render(request, 'products/form_san_pham.html', {
        'form': form, 'tieu_de': 'Thêm sản phẩm'
    })


@login_required
def sua_san_pham(request, pk):
    if not request.user.la_quan_ly:
        return redirect('trang_chu')

    san_pham = get_object_or_404(SanPham, pk=pk)
    if request.method == 'POST':
        form = SanPhamForm(request.POST, request.FILES, instance=san_pham)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật sản phẩm!')
            return redirect('quan_ly_san_pham')
    else:
        form = SanPhamForm(instance=san_pham)

    return render(request, 'products/form_san_pham.html', {
        'form': form, 'tieu_de': 'Sửa sản phẩm'
    })

@login_required
def xoa_san_pham(request, pk):
    if not request.user.la_quan_ly:
        messages.error(request, 'Bạn không có quyền thực hiện.')
        return redirect('trang_chu')

    san_pham = get_object_or_404(SanPham, pk=pk)
    if request.method == 'POST':
        ten = san_pham.ten
        san_pham.delete()
        messages.success(request, f'Đã xoá sản phẩm "{ten}"!')
        return redirect('quan_ly_san_pham')

    return render(request, 'products/xac_nhan_xoa_sp.html', {'san_pham': san_pham})
