from django.urls import path
from . import views

urlpatterns = [
    path('', views.trang_chu, name='trang_chu'),
    path('ban-do/', views.ban_do_tat_ca_cua_hang, name='ban_do'),
    path('dashboard/', views.thong_ke_dashboard, name='dashboard'),
    path('api/cua-hang-gan-nhat/', views.tim_cua_hang_gan_nhat, name='api_cua_hang_gan_nhat'),
    path('api/geocode/', views.geocode_dia_chi, name='api_geocode'),
    path('api/goi-y-dia-chi/', views.api_goi_y_dia_chi, name='api_goi_y_dia_chi'),
    path('api/duong-di/', views.api_duong_di, name='api_duong_di'),
]
