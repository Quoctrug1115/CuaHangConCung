from django.contrib.auth.models import AbstractUser
from django.db import models


class NguoiDung(AbstractUser):
    """Model người dùng mở rộng từ AbstractUser"""

    groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        related_name='nguoidung_set',
        verbose_name='Nhóm'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        blank=True,
        related_name='nguoidung_set',
        verbose_name='Quyền'
    )
    
    VAI_TRO = [
        ('admin', 'Quản trị viên'),
        ('quan_ly', 'Quản lý cửa hàng'),
        ('nhan_vien', 'Nhân viên'),
        ('shipper', 'Shipper'),
        ('khach_hang', 'Khách hàng'),
    ]

    vai_tro = models.CharField(
        max_length=20,
        choices=VAI_TRO,
        default='khach_hang',
        verbose_name='Vai trò'
    )
    so_dien_thoai = models.CharField(
        max_length=15,
        blank=True,
        verbose_name='Số điện thoại'
    )
    dia_chi = models.TextField(
        blank=True,
        verbose_name='Địa chỉ'
    )
    anh_dai_dien = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='Ảnh đại diện'
    )
    ngay_tao = models.DateTimeField(auto_now_add=True)
    ngay_cap_nhat = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Người dùng'
        verbose_name_plural = 'Người dùng'

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_vai_tro_display()})"

    @property
    def la_admin(self):
        return self.vai_tro == 'admin' or self.is_superuser

    @property
    def la_quan_ly(self):
        return self.vai_tro in ['admin', 'quan_ly'] or self.is_superuser

    @property
    def la_nhan_vien(self):
        return self.vai_tro in ['admin', 'quan_ly', 'nhan_vien'] or self.is_superuser
