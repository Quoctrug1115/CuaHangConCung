from django.urls import path
from . import views

urlpatterns = [
    path('', views.danh_sach_san_pham, name='danh_sach_san_pham'),
    path('<int:pk>/', views.chi_tiet_san_pham, name='chi_tiet_san_pham'),
    path('quan-ly/', views.quan_ly_san_pham, name='quan_ly_san_pham'),
    path('quan-ly/them/', views.them_san_pham, name='them_san_pham'),
    path('quan-ly/<int:pk>/sua/', views.sua_san_pham, name='sua_san_pham'),
    path('kho/', views.quan_ly_kho, name='quan_ly_kho'),
    path('kho/<int:ton_kho_id>/nhap/', views.nhap_kho, name='nhap_kho'),
]
