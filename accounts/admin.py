from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, OTPCode, Province, City
from .forms import CustomUserCreationForm, CustomUserChangeForm


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
	search_fields = ['name']
	list_display = ('name',)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
	search_fields = ['name', 'province__name']
	list_display = ('name', 'province')
	list_filter = ('province',)


class CustomUserAdmin(UserAdmin):
	list_display = ('username', 'email', 'phone_number', 'is_staff', 'is_active')
	search_fields = ('username', 'email', 'phone_number')
	list_filter = ('is_staff', 'is_active', 'province')
	ordering = ('-date_joined',)

	fieldsets = (
		(None, {'fields': ('username', 'password')}),
		('اطلاعات شخصی', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'image_profile', 'age')}),
		('دسترسی‌ها', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
		('آدرس', {'fields': ('province', 'city', 'address', 'postal_code')}),
		('تاریخ‌ها', {'fields': ('last_login', 'date_joined')}),
	)

	# تنظیمات فیلدها در صفحه ایجاد کاربر جدید
	add_fieldsets = (
		(None, {
			'classes': ('wide',),
			'fields': (
				'username',
				'email',
				'password1',
				'password2',
				'first_name',
				'last_name',
				'age',
				'image_profile',
				'phone_number'
			),
		}),
	)


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(OTPCode)
