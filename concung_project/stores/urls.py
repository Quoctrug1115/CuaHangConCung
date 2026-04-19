from django.urls import path
from . import views

urlpatterns = [
    # Public
    path('', views.danh_sach_cua_hang, name='danh_sach_cua_hang'),
    path('<int:pk>/', views.chi_tiet_cua_hang, name='chi_tiet_cua_hang'),

    # Store CRUD (admin)
    path('quan-ly/', views.quan_ly_cua_hang, name='quan_ly_cua_hang'),
    path('quan-ly/them/', views.them_cua_hang, name='them_cua_hang'),
    path('quan-ly/<int:pk>/sua/', views.sua_cua_hang, name='sua_cua_hang'),
    path('quan-ly/<int:pk>/xoa/', views.xoa_cua_hang, name='xoa_cua_hang'),

    # Staff CRUD (admin)
    path('nhan-vien/', views.quan_ly_nhan_vien, name='quan_ly_nhan_vien'),
    path('nhan-vien/them/', views.them_nhan_vien, name='them_nhan_vien'),
    path('nhan-vien/<int:pk>/sua/', views.sua_nhan_vien, name='sua_nhan_vien'),
    path('nhan-vien/<int:pk>/xoa/', views.xoa_nhan_vien, name='xoa_nhan_vien'),
]
