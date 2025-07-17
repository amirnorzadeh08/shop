from django.urls import path

from accounts import views
from accounts.views import get_cities

urlpatterns = [
    path('register/', views.register, name='register'),
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('check-username/', views.check_username1, name='check_username'),
    path('check-email/', views.check_email, name='check_email'),
    path('check-phone/', views.check_phone, name='check_phone'),
    path('check-age/', views.check_age, name='check_age'),
    path('manage_products_admin/', views.manage_products_admin, name='manage_products_admin'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/profile/', views.edit_profile, name='edit_profile'),
    path('dashboard/products/', views.manage_products, name='manage_products'),
    path('dashboard/auctions/', views.user_auctions, name='user_auctions'),
    path('dashboard/bids/', views.user_bids, name='user_bids'),
    path('profile/<str:username>/', views.private_profile, name='profile'),
    path('public_profile/<str:username>/', views.public_profile, name='public_profile'),
    path('users-list/', views.user_list, name='user_list'),
    path('admin-admins/', views.admin_list, name='admin_list'),
    path('admin-edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('request-otp/', views.request_otp, name='request_otp'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('api/cities/', get_cities, name='get_cities'),
]
