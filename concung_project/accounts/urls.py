from django.urls import path
from . import views

urlpatterns = [
    path('dang-ky/', views.dang_ky, name='dang_ky'),
    path('dang-nhap/', views.dang_nhap, name='dang_nhap'),
    path('dang-xuat/', views.dang_xuat, name='dang_xuat'),
    path('ho-so/', views.ho_so, name='ho_so'),
    path('quan-ly/', views.quan_ly_nguoi_dung, name='quan_ly_nguoi_dung'),
]
