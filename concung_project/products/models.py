from django.db import models
from stores.models import CuaHang


class DanhMuc(models.Model):
    """Danh mục sản phẩm"""
    ten = models.CharField(max_length=100, verbose_name='Tên danh mục')
    slug = models.SlugField(unique=True)
    mo_ta = models.TextField(blank=True, verbose_name='Mô tả')
    hinh_anh = models.ImageField(upload_to='danh_muc/', blank=True, null=True)
    thu_tu = models.IntegerField(default=0, verbose_name='Thứ tự hiển thị')

    class Meta:
        verbose_name = 'Danh mục'
        verbose_name_plural = 'Danh mục'
        ordering = ['thu_tu', 'ten']

    def __str__(self):
        return self.ten


class SanPham(models.Model):
    """Model sản phẩm"""

    danh_muc = models.ForeignKey(
        DanhMuc,
        on_delete=models.SET_NULL,
        null=True,
        related_name='san_phams',
        verbose_name='Danh mục'
    )
    ten = models.CharField(max_length=200, verbose_name='Tên sản phẩm')
    ma_san_pham = models.CharField(max_length=50, unique=True, verbose_name='Mã sản phẩm')
    mo_ta_ngan = models.CharField(max_length=300, blank=True, verbose_name='Mô tả ngắn')
    mo_ta_chi_tiet = models.TextField(blank=True, verbose_name='Mô tả chi tiết')
    hinh_anh = models.ImageField(upload_to='san_pham/', blank=True, null=True)

    gia_ban = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='Giá bán (VNĐ)')
    gia_nhap = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='Giá nhập (VNĐ)')
    gia_khuyen_mai = models.DecimalField(
        max_digits=12, decimal_places=0,
        null=True, blank=True,
        verbose_name='Giá khuyến mãi'
    )

    thuong_hieu = models.CharField(max_length=100, blank=True, verbose_name='Thương hiệu')
    xuat_xu = models.CharField(max_length=100, blank=True, verbose_name='Xuất xứ')
    trong_luong = models.FloatField(null=True, blank=True, verbose_name='Trọng lượng (g)')

    dang_ban = models.BooleanField(default=True, verbose_name='Đang bán')
    ngay_tao = models.DateTimeField(auto_now_add=True)
    ngay_cap_nhat = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Sản phẩm'
        verbose_name_plural = 'Sản phẩm'
        ordering = ['-ngay_tao']

    def __str__(self):
        return f"{self.ma_san_pham} - {self.ten}"

    @property
    def gia_hien_thi(self):
        """Trả về giá hiển thị (ưu tiên giá khuyến mãi)"""
        return self.gia_khuyen_mai if self.gia_khuyen_mai else self.gia_ban

    @property
    def co_khuyen_mai(self):
        return bool(self.gia_khuyen_mai and self.gia_khuyen_mai < self.gia_ban)


class HinhAnhSanPham(models.Model):
    san_pham = models.ForeignKey(SanPham, on_delete=models.CASCADE, related_name='danh_sach_anh', verbose_name='Sản phẩm')
    anh = models.ImageField(upload_to='san_pham/gallery/', verbose_name='Ảnh kèm theo')
    ngay_tao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Hình ảnh sản phẩm'
        verbose_name_plural = 'Hình ảnh sản phẩm'

    def __str__(self):
        return f"Ảnh của {self.san_pham.ten}"

class TonKho(models.Model):
    """Model tồn kho theo từng cửa hàng"""

    san_pham = models.ForeignKey(
        SanPham,
        on_delete=models.CASCADE,
        related_name='ton_khos',
        verbose_name='Sản phẩm'
    )
    cua_hang = models.ForeignKey(
        CuaHang,
        on_delete=models.CASCADE,
        related_name='ton_khos',
        verbose_name='Cửa hàng'
    )
    so_luong = models.IntegerField(default=0, verbose_name='Số lượng tồn')
    so_luong_toi_thieu = models.IntegerField(default=5, verbose_name='Tồn kho tối thiểu')
    vi_tri_ke = models.CharField(max_length=50, blank=True, verbose_name='Vị trí kệ')
    ngay_cap_nhat = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tồn kho'
        verbose_name_plural = 'Tồn kho'
        unique_together = ('san_pham', 'cua_hang')

    def __str__(self):
        return f"{self.san_pham.ten} - {self.cua_hang.ten}: {self.so_luong}"

    @property
    def can_canh_bao(self):
        """Kiểm tra có dưới mức tồn kho tối thiểu không"""
        return self.so_luong <= self.so_luong_toi_thieu


class LichSuKho(models.Model):
    """Lịch sử nhập/xuất kho"""

    LOAI = [
        ('nhap', 'Nhập kho'),
        ('xuat', 'Xuất kho'),
        ('dieu_chinh', 'Điều chỉnh'),
    ]

    ton_kho = models.ForeignKey(
        TonKho,
        on_delete=models.CASCADE,
        related_name='lich_sus',
        verbose_name='Tồn kho'
    )
    loai = models.CharField(max_length=15, choices=LOAI, verbose_name='Loại')
    so_luong_thay_doi = models.IntegerField(verbose_name='Số lượng thay đổi')
    so_luong_truoc = models.IntegerField(verbose_name='Số lượng trước')
    so_luong_sau = models.IntegerField(verbose_name='Số lượng sau')
    ghi_chu = models.TextField(blank=True, verbose_name='Ghi chú')
    nguoi_thuc_hien = models.ForeignKey(
        'accounts.NguoiDung',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Người thực hiện'
    )
    ngay_tao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Lịch sử kho'
        verbose_name_plural = 'Lịch sử kho'
        ordering = ['-ngay_tao']
