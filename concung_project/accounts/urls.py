from django.urls import path
from django.contrib.auth import views as auth_views
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
    
    # Trang nhập email để xin reset
    path('quen-mat-khau/',
         auth_views.PasswordResetView.as_view(
             template_name='accounts/quen_mat_khau.html',
             email_template_name='email/thong_diep_quen_mat_khau.html', # Template nội dung email gửi đi
             subject_template_name='email/tieu_de_quen_mat_khau.txt'
         ),
         name='quen_mat_khau'),

    # Trang thông báo "Đã gửi mail, hãy kiểm tra"
    path('quen-mat-khau/da-gui/',
         auth_views.PasswordResetDoneView.as_view(template_name='accounts/quen_mat_khau_gui_thanh_cong.html'),
         name='password_reset_done'),

    # Trang đặt lại pass (được gắn link trong email)
    path('dat-lai-mat-khau/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='accounts/dat_lai_mat_khau.html'),
         name='password_reset_confirm'),

    # Trang thông báo đổi pass thành công
    path('dat-lai-mat-khau/hoan-tat/',
         auth_views.PasswordResetCompleteView.as_view(template_name='accounts/dat_lai_mat_khau_thanh_cong.html'),
         name='password_reset_complete'),
]

