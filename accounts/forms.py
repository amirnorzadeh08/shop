from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, City, Comment, User
from datetime import date
import typetype
class CustomUserCreationForm(UserCreationForm):
    age = forms.DateField(
        label='تاریخ تولد (میلادی)',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'id': 'id_age'
        })
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + (
            'age', 'phone_number', 'image_profile', 'province', 'city', 'address', 'postal_code', 'email',
            'first_name', 'last_name'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.TextInput, forms.EmailInput, forms.PasswordInput)):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})
            elif isinstance(field.widget, forms.FileInput):
                field.widget.attrs.update({'class': 'form-control'})
        self.fields['city'].queryset = City.objects.none()
        if 'province' in self.data:
            try:
                province_id = int(self.data.get('province'))
                self.fields['city'].queryset = City.objects.filter(province_id=province_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.province:
            self.fields['city'].queryset = self.instance.province.city_set.all()

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age:
            today = date.today()
            age_years = today.year - age.year - ((today.month, today.day) < (age.month, age.day))
            if age_years < 13:
                raise forms.ValidationError('سن باید حداقل 13 سال باشد.')
            if age_years > 120:
                raise forms.ValidationError('سن واردشده معتبر نیست.')
        return age

    def clean_postal_code(self):
        postal_code = self.cleaned_data.get('postal_code')
        if postal_code:
            if not postal_code.isdigit():
                raise forms.ValidationError('کد پستی باید فقط شامل ارقام باشد.')
            if len(postal_code) != 10:
                raise forms.ValidationError('کد پستی باید دقیقاً 10 رقم باشد.')
        return postal_code

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = UserChangeForm.Meta.fields

class ProfileEditForm(forms.ModelForm):
    age = forms.DateField(
        label='تاریخ تولد (میلادی)',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'id': 'id_age'
        })
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'age', 'phone_number', 'image_profile', 'province',
                  'city', 'address', 'postal_code']

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age:
            today = date.today()
            age_years = today.year - age.year - ((today.month, today.day) < (age.month, age.day))
            if age_years < 13:
                raise forms.ValidationError('سن باید حداقل 13 سال باشد.')
            if age_years > 120:
                raise forms.ValidationError('سن واردشده معتبر نیست.')
        return age

class RequestOTPForm(forms.Form):
    email = forms.EmailField(label='ایمیل')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("کاربری با این ایمیل وجود ندارد.")
        return email

class VerifyOTPForm(forms.Form):
    code = forms.CharField(
        label='کد تأیید',
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={'pattern': '[0-9]{6}'}),
        help_text='کد 6 رقمی ارسال شده به ایمیل خود را وارد کنید'
    )

class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['city'].queryset = City.objects.none()
        if 'province' in self.data:
            try:
                province_id = int(self.data.get('province'))
                self.fields['city'].queryset = City.objects.filter(province_id=province_id)
            except (ValueError, typetype):
                pass
        elif self.instance.pk and self.instance.province:
            self.fields['city'].queryset = self.instance.province.city_set.all()

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text', 'points']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4, 'placeholder': 'نظر خود را بنویسید...'}),
            'points': forms.NumberInput(attrs={'min': 1, 'max': 5, 'value': 1}),
        }
        labels = {
            'text': 'متن نظر',
            'points': 'امتیاز (1 تا 5)',
        }