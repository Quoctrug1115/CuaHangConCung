from django.contrib.gis.db import models as gis_models
from django.db import models
from accounts.models import NguoiDung


class CuaHang(models.Model):
    """Model cửa hàng Con Cưng"""

    ten = models.CharField(max_length=200, verbose_name='Tên cửa hàng')
    ma_cua_hang = models.CharField(max_length=20, unique=True, verbose_name='Mã cửa hàng')
    dia_chi = models.TextField(verbose_name='Địa chỉ')
    quan_huyen = models.CharField(max_length=100, verbose_name='Quận/Huyện')
    tinh_thanh = models.CharField(max_length=100, verbose_name='Tỉnh/Thành phố')
    so_dien_thoai = models.CharField(max_length=15, verbose_name='Số điện thoại')
    email = models.EmailField(blank=True, verbose_name='Email')

    # Tọa độ GIS - PointField lưu (kinh độ, vĩ độ)
    vi_tri = gis_models.PointField(
        srid=4326,
        null=True,
        blank=True,
        verbose_name='Vị trí (tọa độ)'
    )

    gio_mo_cua = models.TimeField(verbose_name='Giờ mở cửa')
    gio_dong_cua = models.TimeField(verbose_name='Giờ đóng cửa')
    ngay_lam_viec = models.CharField(
        max_length=100,
        default='Thứ 2 - Chủ nhật',
        verbose_name='Ngày làm việc'
    )

    dien_tich = models.FloatField(null=True, blank=True, verbose_name='Diện tích (m²)')
    so_luong_nhan_vien = models.IntegerField(default=0, verbose_name='Số nhân viên')

    dang_hoat_dong = models.BooleanField(default=True, verbose_name='Đang hoạt động')
    ngay_tao = models.DateTimeField(auto_now_add=True)
    ngay_cap_nhat = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cửa hàng'
        verbose_name_plural = 'Cửa hàng'
        ordering = ['ten']

    def __str__(self):
        return f"{self.ten} - {self.dia_chi}"

    @property
    def kinh_do(self):
        return self.vi_tri.x if self.vi_tri else None

    @property
    def vi_do(self):
        return self.vi_tri.y if self.vi_tri else None


class NhanVien(models.Model):
    """Model nhân viên"""

    CHUC_VU = [
        ('quan_ly', 'Quản lý cửa hàng'),
        ('thu_ngan', 'Thu ngân'),
        ('ban_hang', 'Nhân viên bán hàng'),
        ('kho', 'Nhân viên kho'),
        ('giao_hang', 'Shipper'),
    ]

    nguoi_dung = models.OneToOneField(
        NguoiDung,
        on_delete=models.CASCADE,
        related_name='nhan_vien',
        verbose_name='Tài khoản'
    )
    cua_hang = models.ForeignKey(
        CuaHang,
        on_delete=models.SET_NULL,
        null=True,
        related_name='nhan_viens',
        verbose_name='Cửa hàng'
    )
    ma_nhan_vien = models.CharField(max_length=20, unique=True, verbose_name='Mã nhân viên')
    chuc_vu = models.CharField(max_length=20, choices=CHUC_VU, verbose_name='Chức vụ')
    ngay_vao_lam = models.DateField(verbose_name='Ngày vào làm')
    luong_co_ban = models.DecimalField(
        max_digits=12, decimal_places=0,
        verbose_name='Lương cơ bản (VNĐ)'
    )
    dang_lam_viec = models.BooleanField(default=True, verbose_name='Đang làm việc')

    class Meta:
        verbose_name = 'Nhân viên'
        verbose_name_plural = 'Nhân viên'

    def __str__(self):
        return f"{self.ma_nhan_vien} - {self.nguoi_dung.get_full_name()} ({self.get_chuc_vu_display()})"


class CaLamViec(models.Model):
    """Model lịch phân ca"""

    THU = [
        (0, 'Thứ 2'), (1, 'Thứ 3'), (2, 'Thứ 4'),
        (3, 'Thứ 5'), (4, 'Thứ 6'), (5, 'Thứ 7'), (6, 'Chủ nhật'),
    ]

    nhan_vien = models.ForeignKey(
        NhanVien,
        on_delete=models.CASCADE,
        related_name='ca_lam_viecs',
        verbose_name='Nhân viên'
    )
    thu_trong_tuan = models.IntegerField(choices=THU, verbose_name='Thứ trong tuần')
    gio_bat_dau = models.TimeField(verbose_name='Giờ bắt đầu')
    gio_ket_thuc = models.TimeField(verbose_name='Giờ kết thúc')

    class Meta:
        verbose_name = 'Ca làm việc'
        verbose_name_plural = 'Ca làm việc'
        unique_together = ('nhan_vien', 'thu_trong_tuan', 'gio_bat_dau')

    def __str__(self):
        return f"{self.nhan_vien} - {self.get_thu_trong_tuan_display()}"
