from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import NguoiDung


class DangKyForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')
    first_name = forms.CharField(max_length=50, required=True, label='Họ')
    last_name = forms.CharField(max_length=50, required=True, label='Tên')
    so_dien_thoai = forms.CharField(max_length=15, required=False, label='Số điện thoại')

    class Meta:
        model = NguoiDung
        fields = ('username', 'first_name', 'last_name', 'email',
                  'so_dien_thoai', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class DangNhapForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class CapNhatHoSoForm(forms.ModelForm):
    class Meta:
        model = NguoiDung
        fields = ('first_name', 'last_name', 'email', 'so_dien_thoai', 'dia_chi', 'anh_dai_dien')
        widgets = {
            'dia_chi': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
