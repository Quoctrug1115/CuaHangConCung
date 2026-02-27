from django import forms
from .models import SanPham, TonKho


class SanPhamForm(forms.ModelForm):
    class Meta:
        model = SanPham
        exclude = ['ngay_tao', 'ngay_cap_nhat']
        widgets = {
            'mo_ta_ngan': forms.TextInput(),
            'mo_ta_chi_tiet': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class TonKhoForm(forms.ModelForm):
    class Meta:
        model = TonKho
        fields = ['so_luong', 'so_luong_toi_thieu', 'vi_tri_ke']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
