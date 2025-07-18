from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import CustomUserCreationForm, UserProfileForm, UserNameForm, ShopForm, PasswordResetRequestForm, OTPVerificationForm, NewPasswordForm
from ads.models import Vehicle, Favorite
from django.contrib.auth.models import User
from django.db.models import Count
from .models import UserProfile, Shop
from django.http import JsonResponse
import json
from datetime import datetime
from django.utils import timezone
from django.db.models import Q
from django.urls import reverse
from .utils import send_welcome_email, send_admin_notification, send_otp_email

# Create your views here.

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Send welcome email to the new user
            try:
                send_welcome_email(user)
                messages.success(request, 'Account created successfully! Welcome email has been sent.')
            except Exception as e:
                # If email fails, still show success message but log the error
                print(f"Failed to send welcome email: {str(e)}")
                messages.success(request, 'Account created successfully!')
            
            # Send admin notification (optional)
            try:
                send_admin_notification(user)
            except Exception as e:
                print(f"Failed to send admin notification: {str(e)}")
            
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def is_admin(user):
    return user.is_superuser

@login_required
def profile(request):
    profile = getattr(request.user, 'userprofile', None)
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        name_form = UserNameForm(request.POST, instance=request.user)
        if profile_form.is_valid() and name_form.is_valid():
            profile = profile_form.save(commit=False)
            if request.POST.get('remove_profile_picture') == '1':
                if profile.profile_picture:
                    profile.profile_picture.delete(save=False)
                profile.profile_picture = None
            profile.save()
            name_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('users:profile')
    else:
        profile_form = UserProfileForm(instance=profile)
        name_form = UserNameForm(instance=request.user)
    return render(request, 'users/profile.html', {
        'profile': profile,
        'profile_form': profile_form,
        'name_form': name_form,
    })

@login_required
def shop_setup(request):
    # Check if user is premium
    profile = getattr(request.user, 'userprofile', None)
    if not profile or not profile.is_premium:
        messages.error(request, 'Only premium users can access shop setup.')
        return redirect('users:profile')

    # Get or create shop instance
    shop, created = Shop.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ShopForm(request.POST, request.FILES, instance=shop)
        if form.is_valid():
            shop = form.save(commit=False)
            if request.POST.get('remove_cover') == '1':
                if shop.cover_photo:
                    shop.cover_photo.delete(save=False)
                shop.cover_photo = None
            shop.save()
            messages.success(request, 'Shop details updated successfully!')
            return redirect('users:shop_setup')
    else:
        form = ShopForm(instance=shop)

    return render(request, 'users/shop_setup.html', {
        'form': form,
        'shop': shop,
        'profile': profile
    })

@login_required
def my_ads(request):
    pending_ads = Vehicle.objects.filter(user=request.user, status='pending').order_by('-created_at')
    approved_ads = Vehicle.objects.filter(user=request.user, status='approved').order_by('-created_at')
    rejected_ads = Vehicle.objects.filter(user=request.user, status='rejected').order_by('-created_at')
    
    return render(request, 'users/my_ads.html', {
        'pending_ads': pending_ads,
        'approved_ads': approved_ads,
        'rejected_ads': rejected_ads
    })

@login_required
def my_favorites(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('vehicle').prefetch_related('vehicle__images').order_by('-created_at')
    favorite_vehicles = [favorite.vehicle for favorite in favorites if favorite.vehicle.status == 'approved']
    
    return render(request, 'users/my_favorites.html', {
        'favorite_vehicles': favorite_vehicles
    })

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    section = request.GET.get('section', 'registered')  # Default to registered users
    search_query = request.GET.get('search', '')
    
    total_users = User.objects.filter(is_superuser=False).count()
    pending_ads = Vehicle.objects.filter(status='pending').count()
    approved_ads = Vehicle.objects.filter(status='approved').count()
    
    context = {
        'section': section,
        'total_users': total_users,
        'pending_ads': pending_ads,
        'approved_ads': approved_ads,
        'search_query': search_query,
    }

    # Add section-specific data
    if section == 'registered':
        from django.core.paginator import Paginator
        users_query = User.objects.filter(is_superuser=False).select_related('userprofile')
        
        # Apply search if query exists
        if search_query:
            users_query = users_query.filter(
                Q(username__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(userprofile__contact_phone__icontains=search_query) |
                Q(userprofile__whatsapp_number__icontains=search_query) |
                Q(userprofile__unique_id__icontains=search_query) |
                Q(shop__company_name__icontains=search_query)
            ).distinct().select_related('shop')
        
        users_query = users_query.order_by('-date_joined')
        
        # Pagination for registered users
        paginator = Paginator(users_query, 40)  # Show 5 users per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['recent_users'] = [
            {
                'user': u,
                'profile': u.userprofile if hasattr(u, 'userprofile') else None,
                'shop': getattr(u, 'shop', None) if hasattr(u, 'userprofile') and u.userprofile and u.userprofile.is_premium else None
            } for u in page_obj
        ]
        context['recent_users_page'] = page_obj
    elif section == 'pending':
        from django.core.paginator import Paginator
        # Get pending vehicles with related user and image data
        pending_query = Vehicle.objects.filter(
            status='pending'
        ).select_related(
            'user',
            'user__userprofile'
        ).prefetch_related(
            'images'
        )
        # Apply search if query exists
        if search_query:
            pending_query = pending_query.filter(
                Q(ad_id__icontains=search_query) |
                Q(make__icontains=search_query) |
                Q(model__icontains=search_query) |
                Q(location__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(vehicle_type__icontains=search_query) |
                Q(user__username__icontains=search_query) |
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(user__userprofile__unique_id__icontains=search_query) |
                Q(phone_number__icontains=search_query) |
                Q(whatsapp_number__icontains=search_query)
            ).distinct()
        pending_query = pending_query.order_by('-created_at')
        paginator = Paginator(pending_query, 40)  # Show 40 ads per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['pending_vehicles'] = page_obj
        context['pending_vehicles_page'] = page_obj
    elif section == 'admgmt':
        from django.core.paginator import Paginator
        all_vehicles_query = Vehicle.objects.all().select_related(
            'user'
        ).prefetch_related(
            'images'
        )
        # Apply search if query exists
        if search_query:
            all_vehicles_query = all_vehicles_query.filter(
                Q(ad_id__icontains=search_query) |
                Q(make__icontains=search_query) |
                Q(model__icontains=search_query) |
                Q(location__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(vehicle_type__icontains=search_query) |
                Q(user__username__icontains=search_query) |
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(user__userprofile__unique_id__icontains=search_query) |
                Q(phone_number__icontains=search_query) |
                Q(whatsapp_number__icontains=search_query)
            ).distinct()
        all_vehicles_query = all_vehicles_query.order_by('-created_at')
        paginator = Paginator(all_vehicles_query, 40)  # Show 40 ads per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['all_vehicles'] = page_obj
        context['all_vehicles_page'] = page_obj
    elif section == 'badge':
        # Badge users section data
        from django.core.paginator import Paginator
        profiles_qs = UserProfile.objects.filter(
            user__is_superuser=False
        ).select_related('user').order_by('-user__date_joined')
        paginator = Paginator(profiles_qs, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['profiles'] = page_obj
    
    return render(request, 'users/admin_dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def manage_ad(request, vehicle_id):
    if request.method == 'POST':
        vehicle = get_object_or_404(Vehicle, id=vehicle_id)
        action = request.POST.get('action')
        
        if action == 'approve':
            vehicle.status = 'approved'
            messages.success(request, 'Ad approved successfully')
        elif action == 'reject':
            vehicle.status = 'rejected'
            messages.success(request, 'Ad rejected successfully')
        
        vehicle.save()
        
        # Get the current section from referer URL or default to 'pending'
        current_section = request.GET.get('section', 'pending')
        return redirect(f'{reverse("users:admin_dashboard")}?section={current_section}')
        
    return redirect('users:admin_dashboard')

@login_required
@user_passes_test(is_admin)
def user_list(request):
    users = User.objects.filter(is_superuser=False).annotate(
        ad_count=Count('vehicle')
    ).order_by('-date_joined')
    # Attach profile info
    users = [
        {
            'user': u,
            'profile': getattr(u, 'userprofile', None),
            'ad_count': u.ad_count
        } for u in users
    ]
    return render(request, 'users/admin_user_list.html', {'users': users})

@login_required
@user_passes_test(is_admin)
def toggle_premium(request, user_id):
    """Set the premium status for a user based on dropdown selection"""
    if request.method == 'POST':
        target_user = get_object_or_404(User, id=user_id, is_superuser=False)
        profile, _ = UserProfile.objects.get_or_create(user=target_user)
        status = request.POST.get('status')
        if status == 'premium':
            profile.is_premium = True
        else:
            profile.is_premium = False
        profile.save()
        status_label = 'Premium' if profile.is_premium else 'Free'
        messages.success(request, f"{target_user.username} is now {status_label} user")
    return redirect('users:admin_dashboard')

@login_required
@user_passes_test(is_admin)
def remove_user(request, user_id):
    """Delete a user (non-superuser) from the system"""
    if request.method == 'POST':
        target_user = get_object_or_404(User, id=user_id, is_superuser=False)
        username = target_user.username
        target_user.delete()
        messages.success(request, f"User '{username}' has been removed")
    return redirect('users:admin_dashboard')

@login_required
@user_passes_test(is_admin)
def badge_users(request):
    """Display and manage user badges"""
    from django.core.paginator import Paginator
    
    # Get all non-superuser profiles
    profiles = UserProfile.objects.filter(
        user__is_superuser=False
    ).select_related('user').order_by('-user__date_joined')
    
    # Pagination
    paginator = Paginator(profiles, 10)  # Show 10 profiles per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'users/admin_badge_users.html', {
        'profiles': page_obj,
    })

@login_required
@user_passes_test(is_admin)
def update_badge(request, user_id):
    """Update badge status and end date for a user"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            profile = get_object_or_404(UserProfile, user_id=user_id)
            
            badge_type = data.get('badge_type')
            is_active = data.get('is_active')
            end_date = data.get('end_date')
            
            if end_date:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            if badge_type == 'verified':
                profile.has_verified_badge = is_active
                if end_date:
                    profile.verified_badge_end_date = end_date
            elif badge_type == 'premium':
                profile.has_premium_badge = is_active
                if end_date:
                    profile.premium_badge_end_date = end_date
            elif badge_type == 'trusted':
                profile.has_trusted_badge = is_active
                if end_date:
                    profile.trusted_badge_end_date = end_date
            
            profile.save()
            return JsonResponse({'status': 'success'})
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@login_required
@user_passes_test(is_admin)
def toggle_urgent(request, vehicle_id):
    """Toggle the urgent status for a vehicle. When enabling urgent, also ensure the ad is approved so it appears on the homepage urgent section."""
    if request.method == 'POST':
        vehicle = get_object_or_404(Vehicle, id=vehicle_id)

        try:
            data = json.loads(request.body or '{}')
            # Determine desired urgent status; if not provided, flip current
            desired_urgent = data.get('is_urgent')
            if desired_urgent is None:
                desired_urgent = not vehicle.is_urgent
        except json.JSONDecodeError:
            desired_urgent = not vehicle.is_urgent

        vehicle.is_urgent = bool(desired_urgent)

        # Ensure the vehicle is approved when marking as urgent so it shows on homepage
        if vehicle.is_urgent and vehicle.status != 'approved':
            vehicle.status = 'approved'

        vehicle.save()
        return JsonResponse({'status': 'success', 'is_urgent': vehicle.is_urgent})
    return JsonResponse({'status': 'error'}, status=400)

def shop_profile(request, user_id):
    """
    Display a premium user's shop profile and their listings
    """
    shop_owner = get_object_or_404(User, id=user_id)
    
    # Check if user is premium and has a shop
    if not shop_owner.userprofile.is_premium:
        messages.error(request, "This user does not have a premium shop.")
        return redirect('home')
    
    shop = get_object_or_404(Shop, user=shop_owner)
    
    # Get all active listings by this user
    vehicles = Vehicle.objects.filter(
        user=shop_owner,
        status='approved'
    ).order_by('-created_at')
    
    context = {
        'shop': shop,
        'vehicles': vehicles,
    }
    
    return render(request, 'users/shop_profile.html', context)

# Password Reset Views
def password_reset_request(request):
    """Step 1: User enters email to request password reset"""
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                profile = user.userprofile
                
                # Generate OTP
                otp = profile.generate_otp()
                
                # Send OTP email
                if send_otp_email(user, otp):
                    messages.success(request, f'Password reset OTP has been sent to {email}. Please check your email.')
                    return redirect('users:otp_verification')
                else:
                    messages.error(request, 'Failed to send OTP. Please try again.')
            except User.DoesNotExist:
                # Don't reveal if email exists or not for security
                messages.success(request, 'If an account with this email exists, a password reset OTP has been sent.')
                return redirect('users:otp_verification')
    else:
        form = PasswordResetRequestForm()
    
    return render(request, 'users/password_reset_request.html', {'form': form})

def otp_verification(request):
    """Step 2: User enters OTP for verification"""
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp']
            
            # Find user with this OTP
            try:
                profile = UserProfile.objects.get(reset_otp=otp)
                if profile.verify_otp(otp):
                    # Store user_id in session for next step
                    request.session['reset_user_id'] = profile.user.id
                    messages.success(request, 'OTP verified successfully. Please enter your new password.')
                    return redirect('users:new_password')
                else:
                    messages.error(request, 'Invalid or expired OTP. Please try again.')
            except UserProfile.DoesNotExist:
                messages.error(request, 'Invalid OTP. Please try again.')
    else:
        form = OTPVerificationForm()
    
    return render(request, 'users/otp_verification.html', {'form': form})

def new_password(request):
    """Step 3: User sets new password"""
    # Check if user_id is in session (from previous step)
    user_id = request.session.get('reset_user_id')
    if not user_id:
        messages.error(request, 'Please request a password reset first.')
        return redirect('users:password_reset_request')
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'Invalid user. Please request a password reset again.')
        return redirect('users:password_reset_request')
    
    if request.method == 'POST':
        form = NewPasswordForm(request.POST)
        if form.is_valid():
            # Set new password
            user.set_password(form.cleaned_data['password1'])
            user.save()
            
            # Clear OTP
            user.userprofile.clear_otp()
            
            # Clear session
            if 'reset_user_id' in request.session:
                del request.session['reset_user_id']
            
            messages.success(request, 'Password has been reset successfully. You can now login with your new password.')
            return redirect('login')
    else:
        form = NewPasswordForm()
    
    return render(request, 'users/new_password.html', {'form': form})
