from django.urls import path
from . import views

app_name = 'ads'

urlpatterns = [
    path('create/', views.create_ad, name='create'),
    path('list/', views.ad_list, name='list'),
    path('detail/<int:pk>/', views.ad_detail, name='detail'),
    path('edit/<int:pk>/', views.edit_ad, name='edit'),
    path('delete/<int:pk>/', views.delete_ad, name='delete'),
    path('search/', views.search_view, name='search'),
    path('search/<str:vehicle_type>/', views.vehicle_type_view, name='vehicle_type'),
    path('toggle-favorite/<int:vehicle_id>/', views.toggle_favorite, name='toggle-favorite'),
] 