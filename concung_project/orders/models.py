from django.db import models
from accounts.models import NguoiDung
from products.models import SanPham
from stores.models import CuaHang


class DonHang(models.Model):
    """Model đơn hàng"""

    TRANG_THAI = [
        ('cho_xac_nhan', 'Chờ xác nhận'),
        ('da_xac_nhan', 'Đã xác nhận'),
        ('dang_dong_goi', 'Đang đóng gói'),
        ('ban_giao_van_chuyen', 'Bàn giao vận chuyển'),
        ('dang_giao', 'Đang giao hàng'),
        ('da_giao', 'Đã giao hàng'),
        ('huy', 'Đã hủy'),
    ]

    PHUONG_THUC_GIAO = [
        ('nhan_tai_cua_hang', 'Nhận tại cửa hàng'),
        ('giao_tan_noi', 'Giao tận nơi'),
    ]

    PHUONG_THUC_THANH_TOAN = [
        ('tien_mat', 'Tiền mặt'),
        ('chuyen_khoan', 'Chuyển khoản'),
        ('the_ngan_hang', 'Thẻ ngân hàng'),
    ]

    ma_don_hang = models.CharField(max_length=20, unique=True, verbose_name='Mã đơn hàng')
    khach_hang = models.ForeignKey(
        NguoiDung,
        on_delete=models.SET_NULL,
        null=True,
        related_name='don_hangs',
        verbose_name='Khách hàng'
    )
    cua_hang = models.ForeignKey(
        CuaHang,
        on_delete=models.SET_NULL,
        null=True,
        related_name='don_hangs',
        verbose_name='Cửa hàng'
    )

    # Thông tin giao hàng
    ho_ten_nguoi_nhan = models.CharField(max_length=100, verbose_name='Họ tên người nhận')
    so_dien_thoai_nhan = models.CharField(max_length=15, verbose_name='Số điện thoại nhận')
    dia_chi_giao_hang = models.TextField(verbose_name='Địa chỉ giao hàng')

    phuong_thuc_giao = models.CharField(
        max_length=20, choices=PHUONG_THUC_GIAO,
        default='giao_tan_noi', verbose_name='Phương thức giao'
    )
    phuong_thuc_thanh_toan = models.CharField(
        max_length=20, choices=PHUONG_THUC_THANH_TOAN,
        default='tien_mat', verbose_name='Phương thức thanh toán'
    )

    trang_thai = models.CharField(
        max_length=25, choices=TRANG_THAI,
        default='cho_xac_nhan', verbose_name='Trạng thái'
    )

    # Tài chính
    tong_tien_san_pham = models.DecimalField(
        max_digits=15, decimal_places=0,
        verbose_name='Tổng tiền sản phẩm'
    )
    phi_giao_hang = models.DecimalField(
        max_digits=10, decimal_places=0,
        default=0, verbose_name='Phí giao hàng'
    )
    giam_gia = models.DecimalField(
        max_digits=10, decimal_places=0,
        default=0, verbose_name='Giảm giá'
    )

    # Vận chuyển
    ma_van_don = models.CharField(
        max_length=100, blank=True,
        verbose_name='Mã vận đơn'
    )
    ghi_chu = models.TextField(blank=True, verbose_name='Ghi chú')

    ngay_tao = models.DateTimeField(auto_now_add=True)
    ngay_cap_nhat = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Đơn hàng'
        verbose_name_plural = 'Đơn hàng'
        ordering = ['-ngay_tao']

    def __str__(self):
        return f"Đơn #{self.ma_don_hang} - {self.get_trang_thai_display()}"

    @property
    def tong_thanh_toan(self):
        return self.tong_tien_san_pham + self.phi_giao_hang - self.giam_gia

    def tao_ma_don_hang(self):
        """Tự động tạo mã đơn hàng"""
        import datetime
        prefix = datetime.datetime.now().strftime('CC%Y%m%d')
        so_thu_tu = DonHang.objects.filter(
            ma_don_hang__startswith=prefix
        ).count() + 1
        return f"{prefix}{so_thu_tu:04d}"

    def save(self, *args, **kwargs):
        if not self.ma_don_hang:
            self.ma_don_hang = self.tao_ma_don_hang()
        super().save(*args, **kwargs)


class ChiTietDonHang(models.Model):
    """Chi tiết từng sản phẩm trong đơn hàng"""

    don_hang = models.ForeignKey(
        DonHang,
        on_delete=models.CASCADE,
        related_name='chi_tiets',
        verbose_name='Đơn hàng'
    )
    san_pham = models.ForeignKey(
        SanPham,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Sản phẩm'
    )
    so_luong = models.IntegerField(verbose_name='Số lượng')
    gia_tai_thoi_diem = models.DecimalField(
        max_digits=12, decimal_places=0,
        verbose_name='Giá tại thời điểm đặt'
    )

    class Meta:
        verbose_name = 'Chi tiết đơn hàng'
        verbose_name_plural = 'Chi tiết đơn hàng'

    def __str__(self):
        ten_sp = self.san_pham.ten if self.san_pham else 'Sản phẩm đã xóa'
        return f"{self.don_hang.ma_don_hang} - {ten_sp}"

    @property
    def thanh_tien(self):
        return self.so_luong * self.gia_tai_thoi_diem


class LichSuTrangThai(models.Model):
    """Lịch sử thay đổi trạng thái đơn hàng"""

    don_hang = models.ForeignKey(
        DonHang,
        on_delete=models.CASCADE,
        related_name='lich_su_trang_thais',
        verbose_name='Đơn hàng'
    )
    trang_thai_cu = models.CharField(
        max_length=25,
        choices=DonHang.TRANG_THAI,
        verbose_name='Trạng thái cũ'
    )
    trang_thai_moi = models.CharField(
        max_length=25,
        choices=DonHang.TRANG_THAI,
        verbose_name='Trạng thái mới'
    )
    ghi_chu = models.TextField(blank=True, verbose_name='Ghi chú')
    nguoi_thuc_hien = models.ForeignKey(
        NguoiDung, on_delete=models.SET_NULL,
        null=True, verbose_name='Người thực hiện'
    )
    thoi_gian = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Lịch sử trạng thái'
        verbose_name_plural = 'Lịch sử trạng thái'
        ordering = ['-thoi_gian']


class GioHang(models.Model):
    """Giỏ hàng (lưu trong DB, có thể dùng session thay thế)"""

    nguoi_dung = models.ForeignKey(
        NguoiDung, on_delete=models.CASCADE,
        related_name='gio_hangs', verbose_name='Người dùng'
    )
    san_pham = models.ForeignKey(
        SanPham, on_delete=models.CASCADE,
        verbose_name='Sản phẩm'
    )
    so_luong = models.IntegerField(default=1, verbose_name='Số lượng')
    ngay_them = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Giỏ hàng'
        unique_together = ('nguoi_dung', 'san_pham')

    @property
    def thanh_tien(self):
        return self.so_luong * self.san_pham.gia_hien_thi
