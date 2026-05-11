from django.urls import path
from . import views

urlpatterns = [
    # Pages
    path('', views.trang_chu, name='trang_chu'),
    path('ban-do/', views.ban_do_tat_ca_cua_hang, name='ban_do'),
    path('ban-do/gis/', views.ban_do_gis_nang_cao, name='ban_do_gis'),
    path('dashboard/', views.thong_ke_dashboard, name='dashboard'),

    # ── API cũ ────────────────────────────────────────────────
    path('api/cua-hang-gan-nhat/', views.tim_cua_hang_gan_nhat, name='api_cua_hang_gan_nhat'),
    path('api/geocode/', views.geocode_dia_chi, name='api_geocode'),
    path('api/goi-y-dia-chi/', views.api_goi_y_dia_chi, name='api_goi_y_dia_chi'),
    path('api/duong-di/', views.api_duong_di, name='api_duong_di'),

    # ── API GIS nâng cao ──────────────────────────────────────
    path('api/cap-nhat-gps/<int:pk>/', views.api_cap_nhat_gps_cua_hang, name='api_cap_nhat_gps'),
    path('api/xoa-gps/<int:pk>/', views.api_xoa_gps_cua_hang, name='api_xoa_gps'),
    path('api/thong-ke-gis/', views.api_thong_ke_gis, name='api_thong_ke_gis'),
    path('api/vung-phu-song/', views.api_vung_phu_song, name='api_vung_phu_song'),

    # ── API mới ───────────────────────────────────────────────
    path('api/ton-kho-cua-hang/', views.api_san_pham_ton_kho_cua_hang, name='api_ton_kho_cua_hang'),
    path('api/isochrone/', views.api_isochrone_simple, name='api_isochrone'),
    path('api/cua-hangs/', views.api_tat_ca_cua_hang_json, name='api_cua_hangs_json'),
]
