from datetime import date

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import random
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class Province(models.Model):
	name = models.CharField(max_length=100, verbose_name='نام استان')

	class Meta:
		verbose_name = 'استان'
		verbose_name_plural = 'استان‌ها'

	def __str__(self):
		return self.name


class City(models.Model):
	province = models.ForeignKey(Province, on_delete=models.CASCADE, verbose_name='استان')
	name = models.CharField(max_length=100, verbose_name='نام شهر')

	class Meta:
		verbose_name = 'شهر'
		verbose_name_plural = 'شهرها'

	def __str__(self):
		return f"{self.name} - {self.province}"


class CustomUser(AbstractUser):
	age = models.DateField(default=date.today, null=True, blank=True, verbose_name='سن')
	phone_number = models.CharField(unique=True, max_length=11, null=True, blank=True, verbose_name='تلفن همراه')
	image_profile = models.ImageField(upload_to='profile_pics/', null=True, blank=True, verbose_name='عکس پروفایل')
	# بازنویسی فیلدهای موجود برای جلوگیری از تداخل
	first_name = models.CharField(max_length=50, null=True, blank=True, verbose_name='نام')
	last_name = models.CharField(max_length=50, null=True, blank=True, verbose_name='نام خانوادگی')
	email = models.EmailField(unique=True, verbose_name='ایمیل')  # اضافه کردن unique=True

	groups = models.ManyToManyField(
		'auth.Group',
		verbose_name='گروه‌ها',
		blank=True,
		help_text='گروه‌هایی که این کاربر به آن‌ها تعلق دارد. کاربر تمام دسترسی‌های گروه‌های خود را دریافت می‌کند.',
		related_name="customuser_groups",
		related_query_name="user",
	)
	user_permissions = models.ManyToManyField(
		'auth.Permission',
		verbose_name='دسترسی‌های کاربر',
		blank=True,
		help_text='دسترسی‌های خاص این کاربر.',
		related_name="customuser_user_permissions",  # related_name منحصر به فرد
		related_query_name="user",
	)
	# فیلدهای آدرس با کلید خارجی
	province = models.ForeignKey(
		Province,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		verbose_name='استان'
	)
	city = models.ForeignKey(
		City,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		verbose_name='شهر',

	)
	address = models.TextField(verbose_name='آدرس کامل', blank=True, null=True)
	postal_code = models.CharField(max_length=10, verbose_name='کد پستی', blank=True, null=True)


User = get_user_model()


class OTPCode(models.Model):
	user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
	code = models.CharField(max_length=6)  # تغییر به CharField
	created_at = models.DateTimeField(auto_now_add=True)
	expires_at = models.DateTimeField()

	@staticmethod
	def generate_code():
		return str(random.randint(100000, 999999))  # تولید کد 6 رقمی برای ارسال ایمیل

	@property
	def is_expired(self):
		return timezone.now() > self.expires_at


class Comment(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='seller_comments')
	writer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='writer_comments')
	text = models.TextField(max_length=500)
	points = models.IntegerField(default=0, validators=[MinValueValidator(1), MaxValueValidator(5)])
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f'{self.writer[:50]} : {self.text}'

