from django import forms
from .models import Vehicle, VehicleImage
from django.forms import inlineformset_factory
from datetime import datetime
from PIL import Image

class VehicleForm(forms.ModelForm):
    VEHICLE_TYPES = [
        ('', 'Select Type'),
        ('car', 'Car'),
        ('motorcycle', 'Motorcycle'),
        ('three-wheeler', '3-Wheeler'),
        ('van', 'Van'),
        ('suv', 'Suv/Jeep'),
        ('pickup', 'Pickup/Double Cab'),
        ('bus', 'Bus'),
        ('lorry', 'Lorry/Truck'),
        ('heavy-duty', 'Heavy Duty'),
        ('tractor', 'Tractor'),
        ('bicycle', 'Bicycle'),
        ('other', 'Other'),
    ]

    VEHICLE_MAKES = [
        ('', 'Select Make'),
        ('toyota', 'Toyota'),
        ('honda', 'Honda'),
        ('nissan', 'Nissan'),
        ('suzuki', 'Suzuki'),
        ('bmw', 'BMW'),
        ('mercedes', 'Mercedes-Benz'),
        ('audi', 'Audi'),
        ('volkswagen', 'Volkswagen'),
        ('ford', 'Ford'),
        ('chevrolet', 'Chevrolet'),
        ('hyundai', 'Hyundai'),
        ('kia', 'Kia'),
        ('mazda', 'Mazda'),
        ('mitsubishi', 'Mitsubishi'),
        ('lexus', 'Lexus'),
        ('other', 'Other'),
    ]

    LOCATION_CHOICES = [
        ('', 'Select City/Province'),
        ('Western Province', (
            ('any_western', 'Any City in Western Province'),
            ('colombo', 'Colombo'),
            ('gampaha', 'Gampaha'),
            ('kalutara', 'Kalutara'),
        )),
        ('Central Province', (
            ('any_central', 'Any City in Central Province'),
            ('kandy', 'Kandy'),
            ('matale', 'Matale'),
            ('nuwara_eliya', 'Nuwara Eliya'),
        )),
        ('Southern Province', (
            ('any_southern', 'Any City in Southern Province'),
            ('galle', 'Galle'),
            ('matara', 'Matara'),
            ('hambantota', 'Hambantota'),
        )),
    ]

    vehicle_type = forms.ChoiceField(choices=VEHICLE_TYPES, widget=forms.Select(attrs={'class': 'form-select'}))
    make = forms.ChoiceField(choices=VEHICLE_MAKES, widget=forms.Select(attrs={'class': 'form-select'}))
    status = forms.CharField(widget=forms.HiddenInput(), initial='pending')
    phone_number = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )
    whatsapp_number = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        }),
        label='WhatsApp Number'
    )
    location = forms.ChoiceField(choices=LOCATION_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = Vehicle
        fields = [
            'vehicle_type', 'make', 'model', 'condition',
            'mileage', 'fuel_type', 'engine', 'year', 'transmission', 'location',
            'description', 'price', 'phone_number', 'whatsapp_number',
            'air_condition', 'power_windows', 'power_mirrors', 'power_seats',
            'power_steering', 'sun_roof', 'abs', 'led', 'reverse_camera', 'air_bags',
            'registered'
        ]
        widgets = {
            'model': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Vehicle Model'}),
            'condition': forms.Select(attrs={
                'class': 'form-select'
            }, choices=[('', '')] + list(Vehicle.CONDITION_CHOICES)),
            'mileage': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter mileage'}),
            'fuel_type': forms.Select(attrs={
                'class': 'form-select'
            }, choices=[('', '')] + list(Vehicle.FUEL_CHOICES)),
            'engine': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'inputmode': 'numeric', 'pattern': '[0-9]*', 'step': '1'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Year'}),
            'registered': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Registration Year'}),
            'transmission': forms.Select(attrs={
                'class': 'form-select'
            }, choices=[('', '')] + list(Vehicle.TRANSMISSION_CHOICES)),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 12}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Price in Rs'}),
            
            # Features as checkboxes
            'air_condition': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'power_windows': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'power_mirrors': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'power_seats': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'power_steering': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sun_roof': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'abs': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'led': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'reverse_camera': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'air_bags': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'fuel_type': 'Fuel Type',
            'transmission': 'Transmission',
            'engine': 'Engine(cc)'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mark required fields
        required_fields = ['vehicle_type', 'make', 'model', 'condition', 'year', 'location', 'price', 'phone_number', 'fuel_type', 'transmission']
        for field in required_fields:
            self.fields[field].required = True
            if self.fields[field].label:
                self.fields[field].label = f"{self.fields[field].label}*"
        
        # Make other fields optional
        optional_fields = ['mileage', 'engine', 'description', 'whatsapp_number', 'registered']
        for field in optional_fields:
            self.fields[field].required = False

        # Set choices with empty defaults
        self.fields['condition'].choices = [('', '')] + list(Vehicle.CONDITION_CHOICES)
        self.fields['fuel_type'].choices = [('', '')] + list(Vehicle.FUEL_CHOICES)
        self.fields['transmission'].choices = [('', '')] + list(Vehicle.TRANSMISSION_CHOICES)
        
        # Remove empty labels
        self.fields['condition'].empty_label = None
        self.fields['fuel_type'].empty_label = None
        self.fields['transmission'].empty_label = None

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if not phone:
            raise forms.ValidationError("Phone number is required")
        
        if not phone.isdigit():
            raise forms.ValidationError("Phone number must contain only digits")
            
        if not phone.startswith('0'):
            raise forms.ValidationError("Phone number must start with '0'")
            
        if len(phone) != 10:
            raise forms.ValidationError("Phone number must be 10 digits long")
            
        return phone

    def clean_whatsapp_number(self):
        whatsapp = self.cleaned_data.get('whatsapp_number')
        if not whatsapp:  # If empty or None, return as is
            return whatsapp
            
        # Only validate if a number was provided
        if not whatsapp.isdigit():
            raise forms.ValidationError("WhatsApp number must contain only digits")
            
        if not whatsapp.startswith('0'):
            raise forms.ValidationError("WhatsApp number must start with '0'")
            
        if len(whatsapp) != 10:
            raise forms.ValidationError("WhatsApp number must be 10 digits long")
            
        return whatsapp

    def clean_year(self):
        year = self.cleaned_data.get('year')
        if year:
            current_year = datetime.now().year
            if year < 1900 or year > current_year + 1:
                raise forms.ValidationError(f"Year must be between 1900 and {current_year + 1}")
        return year

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price and price <= 0:
            raise forms.ValidationError("Price must be greater than 0")
        return price

class VehicleImageForm(forms.ModelForm):
    class Meta:
        model = VehicleImage
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if not image:
            return image

        # If it's a new file upload
        if hasattr(image, 'content_type'):
            allowed_types = ['image/jpeg', 'image/png', 'image/jpg']
            if image.content_type not in allowed_types:
                raise forms.ValidationError('Only JPEG and PNG files are allowed.')

            if image.size > 5 * 1024 * 1024:  # 5MB
                raise forms.ValidationError('Image file size should not exceed 5MB.')

        return image

# Create a formset for multiple images
VehicleImageFormSet = inlineformset_factory(
    Vehicle, VehicleImage,
    form=VehicleImageForm,
    extra=5,  # Number of empty forms to display
    max_num=5,  # Maximum number of forms
    validate_max=True,  # Enforce max_num
    can_delete=True
) 