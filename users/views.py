from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import CustomUserCreationForm, UserProfileForm, UserNameForm, ShopForm
from ads.models import Vehicle
from django.contrib.auth.models import User
from django.db.models import Count
from .models import UserProfile, Shop
from django.http import JsonResponse
import json
from datetime import datetime
from django.utils import timezone

# Create your views here.

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully!')
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
@user_passes_test(is_admin)
def admin_dashboard(request):
    section = request.GET.get('section', 'registered')  # Default to registered users
    total_users = User.objects.filter(is_superuser=False).count()
    pending_ads = Vehicle.objects.filter(status='pending').count()
    approved_ads = Vehicle.objects.filter(status='approved').count()
    
    context = {
        'section': section,
        'total_users': total_users,
        'pending_ads': pending_ads,
        'approved_ads': approved_ads,
    }

    # Add section-specific data
    if section == 'registered':
        recent_users = User.objects.filter(is_superuser=False).order_by('-date_joined')[:5]
        context['recent_users'] = [
            {
                'user': u,
                'profile': getattr(u, 'userprofile', None),
                'shop': Shop.objects.filter(user=u).first() if getattr(u, 'userprofile', None) and getattr(u, 'userprofile', None).is_premium else None
            } for u in recent_users
        ]
    elif section == 'pending':
        # Get pending vehicles with related user and image data
        context['pending_vehicles'] = Vehicle.objects.filter(
            status='pending'
        ).select_related(
            'user',
            'user__userprofile'
        ).prefetch_related(
            'images'
        ).order_by('-created_at')
    elif section == 'admgmt':
        # Get all vehicles with their status
        context['all_vehicles'] = Vehicle.objects.all().select_related(
            'user'
        ).prefetch_related(
            'images'
        ).order_by('-created_at')
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
    """Toggle the urgent status for a vehicle"""
    if request.method == 'POST':
        vehicle = get_object_or_404(Vehicle, id=vehicle_id)
        vehicle.is_urgent = not vehicle.is_urgent
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
