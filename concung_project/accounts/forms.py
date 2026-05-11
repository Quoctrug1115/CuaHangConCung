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


class AdminNguoiDungForm(forms.ModelForm):
    """Form đầy đủ cho admin CRUD người dùng."""
    password1 = forms.CharField(
        label='Mật khẩu',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Ít nhất 8 ký tự'}),
        required=False,
        help_text='Bỏ trống để giữ nguyên mật khẩu cũ (khi sửa).'
    )
    password2 = forms.CharField(
        label='Xác nhận mật khẩu',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Nhập lại mật khẩu'}),
        required=False,
    )

    class Meta:
        model = NguoiDung
        fields = ('username', 'first_name', 'last_name', 'email',
                  'so_dien_thoai', 'dia_chi', 'anh_dai_dien', 'vai_tro', 'is_active')
        widgets = {
            'dia_chi': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name not in ('password1', 'password2', 'is_active'):
                field.widget.attrs['class'] = 'form-control'
        # Mật khẩu không bắt buộc khi sửa
        if self.instance and self.instance.pk:
            self.fields['password1'].required = False
            self.fields['password2'].required = False
        else:
            self.fields['password1'].required = True
            self.fields['password2'].required = True

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 or p2:
            if p1 != p2:
                raise forms.ValidationError('Hai mật khẩu không khớp.')
            if len(p1) < 8:
                raise forms.ValidationError('Mật khẩu phải có ít nhất 8 ký tự.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        p1 = self.cleaned_data.get('password1')
        if p1:
            user.set_password(p1)
        if commit:
            user.save()
        return user


class DoiMatKhauAdminForm(forms.Form):
    """Form đổi mật khẩu do admin thực hiện."""
    password1 = forms.CharField(
        label='Mật khẩu mới',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        min_length=8,
    )
    password2 = forms.CharField(
        label='Xác nhận mật khẩu',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Hai mật khẩu không khớp.')
        return cleaned_data
