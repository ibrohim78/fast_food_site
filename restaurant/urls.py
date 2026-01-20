# restaurant/urls.py - to'liq tuzatilgan versiya

from django.urls import path
from . import views

app_name = 'restaurant'

urlpatterns = [
    # Asosiy sahifalar - FUNKSIYA VIEWLAR
    path('', views.home, name='home'),
    path('menu/', views.menu, name='menu'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    
    # Buyurtma va bron - FUNKSIYA VIEWLAR
    path('order/', views.order, name='order'),
    path('order/success/<int:order_id>/', views.order_success, name='order_success'),
    path('reservation/', views.reservation, name='reservation'),
    path('reservation/success/', views.reservation_success, name='reservation_success'),
    
    # Savat - FUNKSIYA VIEWLAR
    path('cart/', views.cart, name='cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    
    # API endpoints
    path('api/cart/count/', views.get_cart_count, name='api_cart_count'),
    path('api/cart/items/', views.get_cart_items, name='api_cart_items'),
    
    # Test sahifasi
    path('test-telegram/', views.test_telegram, name='test_telegram'),
]