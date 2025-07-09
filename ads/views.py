from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Vehicle, Favorite
from .forms import VehicleForm, VehicleImageFormSet
from django.http import JsonResponse
import re

# Create your views here.

def home_view(request):
    # Get urgent vehicle listings that are approved
    urgent_vehicles = Vehicle.objects.filter(status='approved', is_urgent=True).order_by('-created_at')
    return render(request, 'home.html', {
        'urgent_vehicles': urgent_vehicles
    })

def ad_list(request):
    return redirect('home')

def search_view(request):
    # Get all search parameters from the request
    vehicle_type = request.GET.get('type')
    make = request.GET.get('make')
    model = request.GET.get('model')
    condition = request.GET.get('condition')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    city = request.GET.get('city')
    fuel = request.GET.get('fuel')

    # Start with all approved vehicles
    vehicles = Vehicle.objects.filter(status='approved')

    # Apply filters based on search parameters
    if vehicle_type:
        vehicles = vehicles.filter(vehicle_type__iexact=vehicle_type)
    
    if make:
        vehicles = vehicles.filter(make__iexact=make)
    
    if model:
        normalized = re.sub(r'[^A-Za-z0-9]', '', model.lower())
        # Build a regex pattern that allows any number of spaces or hyphens between letters
        regex_parts = [re.escape(ch) + r'[-\s]*' for ch in normalized]
        regex_pattern = ''.join(regex_parts)
        vehicles = vehicles.filter(model__iregex=regex_pattern)
    
    if condition and condition != 'any':
        vehicles = vehicles.filter(condition=condition)
    
    if min_price:
        vehicles = vehicles.filter(price__gte=min_price)
    
    if max_price:
        vehicles = vehicles.filter(price__lte=max_price)
    
    if city and city != 'any':
        if city.startswith('any_'):
            # If it's "any city in province", extract the province name
            province = city.replace('any_', '')
            # You would need to map this to your actual location data structure
            # This is a simplified example
            vehicles = vehicles.filter(location__icontains=province)
        else:
            vehicles = vehicles.filter(location__icontains=city)
    
    if fuel and fuel != 'any':
        vehicles = vehicles.filter(fuel_type=fuel)

    # Order by most recent first
    vehicles = vehicles.order_by('-created_at')

    return render(request, 'ads/search_results.html', {
        'vehicles': vehicles,
        'search_params': {
            'type': vehicle_type,
            'make': make,
            'model': model,
            'condition': condition,
            'min_price': min_price,
            'max_price': max_price,
            'city': city,
            'fuel': fuel
        }
    })

def ad_detail(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    # Allow viewing if:
    # 1. Ad is approved
    # 2. User is the owner of the ad
    # 3. User is an admin/superuser
    if vehicle.status == 'approved' or vehicle.user == request.user or request.user.is_superuser:
        return render(request, 'ads/ad_detail.html', {
            'vehicle': vehicle
        })
    messages.error(request, 'This ad is not available.')
    return redirect('home')

@login_required
def create_ad(request):
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        image_formset = VehicleImageFormSet(request.POST, request.FILES)
        
        if form.is_valid() and image_formset.is_valid():
            try:
                # Save vehicle with the current user
                vehicle = form.save(commit=False)
                vehicle.user = request.user
                vehicle.status = 'pending'  # Set initial status as pending
                vehicle.save()
                
                # Save images
                image_formset.instance = vehicle
                image_formset.save()
                
                messages.success(request, 'Your vehicle ad has been submitted for review. You will be notified once it is approved.')
                return redirect('users:my_ads')
            except Exception as e:
                messages.error(request, f'Error creating ad: {str(e)}')
                # Delete the vehicle if image upload fails
                if vehicle.id:
                    vehicle.delete()
        else:
            # Show specific form errors
            if form.errors:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field.replace("_", " ").title()}: {error}')
            
            # Show formset errors
            if image_formset.errors:
                for form_num, form_errors in enumerate(image_formset.errors):
                    for field, errors in form_errors.items():
                        for error in errors:
                            messages.error(request, f'Image {form_num + 1} - {error}')
            
            # Show non-form errors (e.g., max number of forms)
            if image_formset.non_form_errors():
                for error in image_formset.non_form_errors():
                    messages.error(request, f'Image upload error: {error}')
    else:
        form = VehicleForm()
        image_formset = VehicleImageFormSet()
    
    return render(request, 'ads/create_ad.html', {
        'form': form,
        'image_formset': image_formset,
        'title': 'Create Vehicle Ad'
    })

@login_required
def edit_ad(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    
    # Check if the user owns this ad
    if vehicle.user != request.user:
        messages.error(request, "You don't have permission to edit this ad.")
        return redirect('users:my_ads')
        
    if request.method == 'POST':
        form = VehicleForm(request.POST, instance=vehicle)
        image_formset = VehicleImageFormSet(request.POST, request.FILES, instance=vehicle)
        
        if form.is_valid() and image_formset.is_valid():
            # Save the vehicle form
            vehicle = form.save(commit=False)
            # If the ad was previously rejected or approved, set it back to pending for admin review
            vehicle.status = 'pending'
            vehicle.save()
            
            # Save the image formset
            images = image_formset.save(commit=False)
            for image in images:
                image.vehicle = vehicle
                image.save()
                
            # Delete marked images
            for image_form in image_formset.deleted_forms:
                if image_form.instance.pk:
                    image_form.instance.delete()
            
            messages.success(request, 'Your ad has been updated successfully.')
            return redirect('users:my_ads')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = VehicleForm(instance=vehicle)
        image_formset = VehicleImageFormSet(instance=vehicle)
    
    context = {
        'form': form,
        'image_formset': image_formset,
        'vehicle': vehicle
    }
    return render(request, 'ads/edit_ad.html', context)

@login_required
def delete_ad(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk, user=request.user)
    
    if request.method == 'POST':
        # Delete associated images first
        vehicle.images.all().delete()
        # Delete the vehicle
        vehicle.delete()
        messages.success(request, 'Your ad has been deleted successfully.')
        return redirect('users:my_ads')
    
    return render(request, 'ads/delete_confirm.html', {
        'vehicle': vehicle
    })

@login_required
def toggle_favorite(request, vehicle_id):
    try:
        vehicle = Vehicle.objects.get(id=vehicle_id)
        favorite, created = Favorite.objects.get_or_create(user=request.user, vehicle=vehicle)
        
        if not created:
            favorite.delete()
            is_favorite = False
        else:
            is_favorite = True
            
        return JsonResponse({
            'status': 'success',
            'is_favorite': is_favorite
        })
    except Vehicle.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Vehicle not found'
        }, status=404)

def vehicle_type_view(request, vehicle_type):
    # Map URL slugs to actual vehicle types
    type_mapping = {
        'cars': 'car',
        'motorcycles': 'motorcycle',
        'three-wheelers': 'three-wheeler',
        'vans': 'van',
        'suvs': 'suv',
        'pickups': 'pickup',
        'buses': 'bus',
        'lorries': 'lorry',
        'heavy-duty': 'heavy-duty',
        'tractors': 'tractor',
        'bicycles': 'bicycle',
        'others': 'other'
    }

    # Get the actual vehicle type from the mapping
    actual_type = type_mapping.get(vehicle_type)
    if not actual_type:
        return redirect('ads:search')  # Redirect to main search if type not found

    # Start with approved vehicles
    vehicles = Vehicle.objects.filter(status='approved')

    # Apply vehicle type filter
    vehicles = vehicles.filter(vehicle_type=actual_type)

    # Get other search parameters
    make = request.GET.get('make')
    model = request.GET.get('model')
    condition = request.GET.get('condition')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    city = request.GET.get('city')
    fuel = request.GET.get('fuel')

    # Apply other filters
    if make:
        vehicles = vehicles.filter(make__iexact=make)
    
    if model:
        normalized = re.sub(r'[^A-Za-z0-9]', '', model.lower())
        regex_parts = [re.escape(ch) + r'[-\s]*' for ch in normalized]
        regex_pattern = ''.join(regex_parts)
        vehicles = vehicles.filter(model__iregex=regex_pattern)
    
    if condition and condition != 'any':
        vehicles = vehicles.filter(condition=condition)
    
    if min_price:
        vehicles = vehicles.filter(price__gte=min_price)
    
    if max_price:
        vehicles = vehicles.filter(price__lte=max_price)
    
    if city and city != 'any':
        if city.startswith('any_'):
            province = city.replace('any_', '')
            vehicles = vehicles.filter(location__icontains=province)
        else:
            vehicles = vehicles.filter(location__icontains=city)
    
    if fuel and fuel != 'any':
        vehicles = vehicles.filter(fuel_type=fuel)

    # Order by most recent first
    vehicles = vehicles.order_by('-created_at')

    return render(request, 'ads/search_results.html', {
        'vehicles': vehicles,
        'search_params': {
            'type': actual_type,
            'make': make,
            'model': model,
            'condition': condition,
            'min_price': min_price,
            'max_price': max_price,
            'city': city,
            'fuel': fuel
        }
    })
