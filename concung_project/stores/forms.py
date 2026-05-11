from django import forms
from .models import CuaHang, NhanVien


class CuaHangForm(forms.ModelForm):
    # Nhập tọa độ thủ công hoặc từ geocoding
    kinh_do = forms.FloatField(
        required=False,
        label='Kinh độ (Longitude)',
        help_text='Ví dụ: 106.6297'
    )
    vi_do = forms.FloatField(
        required=False,
        label='Vĩ độ (Latitude)',
        help_text='Ví dụ: 10.8231'
    )

    class Meta:
        model = CuaHang
        exclude = ['vi_tri', 'ngay_tao', 'ngay_cap_nhat']
        widgets = {
            'dia_chi': forms.Textarea(attrs={'rows': 2}),
            'gio_mo_cua': forms.TimeInput(attrs={'type': 'time'}),
            'gio_dong_cua': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Điền sẵn tọa độ nếu đã có
        if self.instance and self.instance.vi_tri:
            self.fields['kinh_do'].initial = self.instance.vi_tri.x
            self.fields['vi_do'].initial = self.instance.vi_tri.y
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        cua_hang = super().save(commit=False)
        kinh_do = self.cleaned_data.get('kinh_do')
        vi_do   = self.cleaned_data.get('vi_do')
        if kinh_do is not None and vi_do is not None:
            # Có tọa độ → lưu GPS (dùng is not None thay vì truthy check để tránh lỗi với 0.0)
            from django.contrib.gis.geos import Point
            cua_hang.vi_tri = Point(float(kinh_do), float(vi_do), srid=4326)
        else:
            # Không có tọa độ (user xóa ghim) → xóa GPS
            cua_hang.vi_tri = None
        if commit:
            cua_hang.save()
        return cua_hang


class NhanVienForm(forms.ModelForm):
    class Meta:
        model = NhanVien
        fields = ['nguoi_dung', 'cua_hang', 'ma_nhan_vien', 'chuc_vu',
                  'ngay_vao_lam', 'luong_co_ban', 'dang_lam_viec']
        widgets = {
            'ngay_vao_lam': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
