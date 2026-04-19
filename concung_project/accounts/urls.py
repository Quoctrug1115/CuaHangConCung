from django.urls import path
from . import views

urlpatterns = [
    path('dang-ky/', views.dang_ky, name='dang_ky'),
    path('dang-nhap/', views.dang_nhap, name='dang_nhap'),
    path('dang-xuat/', views.dang_xuat, name='dang_xuat'),
    path('ho-so/', views.ho_so, name='ho_so'),
    path('quan-ly/', views.quan_ly_nguoi_dung, name='quan_ly_nguoi_dung'),
    path('quan-ly/them/', views.them_nguoi_dung, name='them_nguoi_dung'),
    path('quan-ly/<int:pk>/', views.chi_tiet_nguoi_dung, name='chi_tiet_nguoi_dung'),
    path('quan-ly/<int:pk>/sua/', views.sua_nguoi_dung, name='sua_nguoi_dung'),
    path('quan-ly/<int:pk>/xoa/', views.xoa_nguoi_dung, name='xoa_nguoi_dung'),
    path('quan-ly/<int:pk>/doi-mat-khau/', views.doi_mat_khau_admin, name='doi_mat_khau_admin'),
]

