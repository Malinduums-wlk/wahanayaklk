from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Shop
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Field

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    mobile_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your mobile number'
        })
    )
    
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'mobile_number', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove all help_texts
        for field in self.fields:
            self.fields[field].help_text = None
            
        # Setup crispy forms layout
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group col-md-6'),
                Column('last_name', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            Field('username'),
            Field('email'),
            Field('mobile_number'),
            Field('password1'),
            Field('password2'),
            Submit('submit', 'Register', css_class='btn btn-primary')
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()
            # Ensure a profile exists (created by signal) and update mobile number
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.contact_phone = self.cleaned_data['mobile_number']
            profile.save()

        return user

class UserProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # pop instance before super
        instance = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)

        # If the user is not premium, remove listing_type field
        if instance and not instance.is_premium:
            self.fields.pop('listing_type', None)
        # Make profile_picture optional directly
        self.fields['profile_picture'].required = False

    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'contact_phone', 'whatsapp_number', 'listing_type']
        widgets = {
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control',
                'style': 'display: none;',
                'accept': 'image/*'
            }),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Number', 'style': 'width: 200px;'}),
            'whatsapp_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'WhatsApp Number', 'style': 'width: 200px;'}),
            'listing_type': forms.Select(attrs={'class': 'form-control', 'style': 'width: 200px;'})
        }

class UserNameForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name', 'style': 'display:inline-block; width: 120px; margin-right: 8px;'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name', 'style': 'display:inline-block; width: 120px;'}),
        } 

class ShopForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False
    class Meta:
        model = Shop
        fields = ['cover_photo', 'company_name', 'contact_number1', 'contact_number2', 
                 'whatsapp_number', 'address', 'google_map_link', 'facebook_link', 'youtube_link']
        widgets = {
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter company name'
            }),
            'contact_number1': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Primary contact number'
            }),
            'contact_number2': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Secondary contact number'
            }),
            'whatsapp_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'WhatsApp number'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter address',
                'rows': 3
            }),
            'google_map_link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Google Maps location link'
            }),
            'facebook_link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Facebook profile/page link'
            }),
            'youtube_link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter YouTube channel link'
            })
        } 