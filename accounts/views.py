from cProfile import Profile

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import PasswordResetView
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Avg, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib.auth import login
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import OTPCode, City, Province, Comment
from .forms import RequestOTPForm, VerifyOTPForm
from django.http import JsonResponse
from datetime import timedelta, date
from accounts.forms import CustomUserCreationForm, ProfileEditForm
from accounts.models import CustomUser, User
from app.models import Product, Bid


# Create your views here.

def check_username(request):
	username = request.GET.get('username', None)
	data = {
		'is_taken': User.objects.filter(username__iexact=username).exists()
	}
	if data['is_taken']:
		data['error_message'] = 'نام کاربری قبلاً استفاده شده است.'
	else:
		data['success_message'] = 'نام کاربری مناسب است.'
	return JsonResponse(data)


def register(request):
	provinces = Province.objects.all()
	if request.method == 'POST':
		form = CustomUserCreationForm(request.POST, request.FILES)
		if form.is_valid():
			user = form.save()
			login(request, user)  # ورود خودکار کاربر
			return redirect('dashboard')
		else:
			print("Form errors:", form.errors)  # چاپ خطاها در کنسول برای دیباگ
	else:
		form = CustomUserCreationForm()
	return render(request, 'registration/register.html', {'form': form, 'provinces': provinces})


@login_required
def dashboard(request):
	return render(request, 'dashboard/dashboard.html')


@login_required
def edit_profile(request):
	if request.method == 'POST':
		form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
		if form.is_valid():
			form.save()
			return redirect('dashboard')
	else:
		form = ProfileEditForm(instance=request.user)
	return render(request, 'registration/edit_profile.html', {'form': form})


@login_required
def manage_products(request):
	products = Product.objects.filter(user=request.user, is_deleted=False)
	return render(request, 'dashboard/manage_products.html', {'products': products})

@staff_member_required
def manage_products_admin(request):
	query = request.GET.get('q', '')
	products = Product.objects.filter(is_deleted=False)
	if query:
		products = products.filter(
			Q(productName__icontains=query)
		)

	return render(request, 'admin/manage_products_admin.html', {'products': products})


@login_required
def user_auctions(request):
	auctions = Product.objects.filter(user=request.user, selltype='auction', is_deleted=False)
	return render(request, 'dashboard/user_auctions.html', {'auctions': auctions})


@login_required
def user_bids(request):
	bids = Bid.objects.filter(user=request.user).select_related('product')
	return render(request, 'dashboard/user_bids.html', {'bids': bids})


@login_required
def private_profile(request, username):
	user = get_object_or_404(CustomUser, username=username)
	return render(request, 'dashboard/private_profile.html', {'user_profile': user})


def public_profile(request, username):
	user = get_object_or_404(CustomUser, username=username)
	avg_rating = Comment.objects.filter(user=user).aggregate(
		avg_points=Avg('points')
	)['avg_points']


	average_rating = round(avg_rating, 1) if avg_rating else None
	context = {
		'user_profile': user,
		'avg_rating': avg_rating,
		'average_rating': average_rating
	}
	return render(request, 'dashboard/public_profile.html', context)


def request_otp(request):
	if request.method == 'POST':
		form = RequestOTPForm(request.POST)
		if form.is_valid():
			email = form.cleaned_data['email']

			try:
				user = User.objects.get(email=email)
			except User.DoesNotExist:
				form.add_error('email', 'کاربری با این ایمیل وجود ندارد')
				return render(request, 'auth/request_otp.html', {'form': form})

			# ایجاد کد 6 رقمی و ذخیره آن
			code = OTPCode.generate_code()
			expires_at = timezone.now() + timedelta(minutes=10)
			OTPCode.objects.create(user=user, code=code, expires_at=expires_at)

			# ارسال ایمیل
			subject = 'کد ورود شما'
			html_content = render_to_string('auth/otp_email.html', {'code': code})
			text_content = f'کد ورود شما: {code}'

			msg = EmailMultiAlternatives(subject, text_content, 'noreply@example.com', [email])
			msg.attach_alternative(html_content, "text/html")
			msg.send()

			return redirect('verify_otp')

	else:
		form = RequestOTPForm()
	return render(request, 'auth/request_otp.html', {'form': form})


def verify_otp(request):
	if request.method == 'POST':
		form = VerifyOTPForm(request.POST)
		if form.is_valid():
			code = form.cleaned_data['code']
			now = timezone.now()

			with transaction.atomic():
				otp = OTPCode.objects.select_for_update().filter(
					code=code,
					expires_at__gt=now
				).first()

				if otp:
					login(request, otp.user)
					otp.delete()
					return redirect('home')
				else:
					form.add_error('code', 'کد نامعتبر یا منقضی شده است')
	else:
		form = VerifyOTPForm()
	return render(request, 'auth/verify_otp.html', {'form': form})


def get_cities(request):
	province_id = request.GET.get('province_id')
	if not province_id:
		return JsonResponse([], safe=False)

	cities = City.objects.filter(province_id=province_id).values('id', 'name')
	return JsonResponse(list(cities), safe=False)


class CustomPasswordResetForm(PasswordResetForm):
	def clean_email(self):
		email = self.cleaned_data['email']
		if not User.objects.filter(email__iexact=email, is_active=True).exists():
			raise ValidationError("ایمیل وارد شده در سیستم ثبت نشده است")
		return email


class CustomPasswordResetView(PasswordResetView):
	form_class = CustomPasswordResetForm
	template_name = 'registration/password_reset_form.html'


@staff_member_required
def user_list(request):
	query = request.GET.get('q', '')
	users = CustomUser.objects.all().order_by('-date_joined')
	if query:
		users = users.filter(
			Q(username__icontains=query) |
			Q(first_name__icontains=query)|
			Q(last_name__icontains=query)|
			Q(email__icontains=query)

		)

	context = {
		'users': users,
		'page_title': 'لیست کاربران',
		'query': query
	}
	return render(request, 'admin/user_list.html', context)


@staff_member_required
def admin_list(request):
	admins = CustomUser.objects.filter(is_staff=True).order_by('-date_joined')
	context = {
		'admins': admins,
		'page_title': 'لیست ادمین‌ها'
	}
	return render(request, 'admin/admin_user_list.html', context)


@staff_member_required
def edit_user(request, user_id):
	user = get_object_or_404(CustomUser, id=user_id)
	provinces = Province.objects.all()
	cities = City.objects.all()

	if request.method == 'POST':
		# پردازش داده‌های فرم
		user.first_name = request.POST.get('first_name')
		user.last_name = request.POST.get('last_name')
		user.email = request.POST.get('email')
		user.phone_number = request.POST.get('phone_number')
		user.is_active = request.POST.get('is_active') == 'on'
		user.is_staff = request.POST.get('is_staff') == 'on'
		user.is_superuser = request.POST.get('is_superuser') == 'on'

		# پردازش فیلدهای مرتبط
		province_id = request.POST.get('province')
		if province_id:
			user.province = Province.objects.get(id=province_id)

		city_id = request.POST.get('city')
		if city_id:
			user.city = City.objects.get(id=city_id)

		user.save()
		messages.success(request, 'تغییرات با موفقیت ذخیره شد')
		return redirect('user_list')

	context = {
		'user': user,
		'provinces': provinces,
		'cities': cities,
		'page_title': 'ویرایش کاربر'
	}
	return render(request, 'admin/edit_user.html', context)


def check_username1(request):
	username = request.GET.get('username', None)
	data = {
		'is_taken': User.objects.filter(username__iexact=username).exists()
	}
	if data['is_taken']:
		data['error_message'] = 'نام کاربری قبلاً استفاده شده است.'
	else:
		data['success_message'] = 'نام کاربری مناسب است.'
	return JsonResponse(data)


def check_email(request):
	email = request.GET.get('email', None)
	data = {
		'is_taken': CustomUser.objects.filter(email__iexact=email).exists()
	}
	if data['is_taken']:
		data['error_message'] = 'این ایمیل قبلاً استفاده شده است.'
	else:
		data['success_message'] = 'ایمیل مناسب است.'
	return JsonResponse(data)


def check_phone(request):
	phone = request.GET.get('phone', None)
	data = {
		'is_taken': CustomUser.objects.filter(phone_number=phone).exists()
	}
	if data['is_taken']:
		data['error_message'] = 'این شماره تلفن قبلاً استفاده شده است.'
	else:
		data['success_message'] = 'شماره تلفن مناسب است.'
	return JsonResponse(data)


def check_age(request):
	age_str = request.GET.get('age', None)
	if not age_str:
		return JsonResponse({'message': 'لطفاً تاریخ تولد را وارد کنید.', 'valid': False})
	try:
		# تبدیل تاریخ به فرمت قابل فهم (YYYY-MM-DD)
		age = date.fromisoformat(age_str)
		today = date.today()
		age_years = today.year - age.year - ((today.month, today.day) < (age.month, age.day))
		if age_years < 13:
			return JsonResponse({'message': 'سن باید حداقل 13 سال باشد.', 'valid': False})
		if age_years > 120:
			return JsonResponse({'message': 'سن واردشده معتبر نیست.', 'valid': False})
		return JsonResponse({'message': 'تاریخ تولد معتبر است.', 'valid': True})
	except ValueError:
		return JsonResponse({'message': 'فرمت تاریخ نامعتبر است.', 'valid': False})
