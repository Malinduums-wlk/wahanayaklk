from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('shop/', views.shop_setup, name='shop_setup'),
    path('shop/<int:user_id>/', views.shop_profile, name='shop_profile'),
    path('my-ads/', views.my_ads, name='my_ads'),
    path('my-favorites/', views.my_favorites, name='my_favorites'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.user_list, name='admin_user_list'),
    path('admin/badge-users/', views.badge_users, name='admin_badge_users'),
    path('admin/update-badge/<int:user_id>/', views.update_badge, name='update_badge'),
    path('admin/manage-ad/<int:vehicle_id>/', views.manage_ad, name='manage_ad'),
    path('admin/toggle-premium/<int:user_id>/', views.toggle_premium, name='toggle_premium'),
        path('admin/remove-user/<int:user_id>/', views.remove_user, name='remove_user'),
    path('admin/toggle-urgent/<int:vehicle_id>/', views.toggle_urgent, name='toggle_urgent'),
    path('admin/toggle-boost/<int:vehicle_id>/', views.toggle_boost, name='toggle_boost'),
    path('admin/update-boost-end-date/<int:vehicle_id>/', views.update_boost_end_date, name='update_boost_end_date'),
    path('admin/update-urgent-end-date/<int:vehicle_id>/', views.update_urgent_end_date, name='update_urgent_end_date'),
    path('admin/delete-ad/<int:vehicle_id>/', views.delete_ad, name='delete_ad'),
    

    # Password Reset URLs
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('otp-verification/', views.otp_verification, name='otp_verification'),
    path('new-password/', views.new_password, name='new_password'),
] 