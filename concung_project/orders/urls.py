from django.urls import path
from . import views

urlpatterns = [
    # Giỏ hàng
    path('gio-hang/', views.xem_gio_hang, name='xem_gio_hang'),
    path('gio-hang/them/<int:san_pham_id>/', views.them_vao_gio, name='them_vao_gio'),
    path('gio-hang/cap-nhat/<int:item_id>/', views.cap_nhat_gio, name='cap_nhat_gio'),
    path('gio-hang/xoa/<int:item_id>/', views.xoa_khoi_gio, name='xoa_khoi_gio'),

    # Đặt hàng
    path('dat-hang/', views.dat_hang, name='dat_hang'),
    path('cua-toi/', views.don_hang_cua_toi, name='don_hang_cua_toi'),
    path('theo-doi/<str:ma>/', views.theo_doi_don_hang, name='theo_doi_don_hang'),
    path('don-hang/<int:pk>/huy/', views.huy_don_hang, name='huy_don_hang'),

    # Quản lý (Admin)
    path('quan-ly/', views.quan_ly_don_hang, name='quan_ly_don_hang'),
    path('quan-ly/<int:pk>/cap-nhat/', views.cap_nhat_trang_thai, name='cap_nhat_trang_thai'),
]
