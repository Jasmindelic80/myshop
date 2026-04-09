from .views import *
from django.urls import path
from . import views
from .views import (
    api_products,
    add_to_cart,
    get_cart,
    remove_from_cart,
    clear_cart
)
from .views import register, login
from .views import checkout,update_quantity
app_name = 'shop'

urlpatterns = [
    # 🌐 WEB (HTML)
    path('', views.product_list, name='product_list'),
    path('<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),

    # 📦 API
    path('api/products/', api_products),

    # 🛒 CART API
    path('api/cart/', get_cart),
    path('api/cart/add/', add_to_cart),
    path('api/cart/remove/', remove_from_cart),
    path('api/cart/clear/', clear_cart),
    path('api/register/', register),
    path('api/login/', login),
    path('api/checkout/', checkout),
    path('api/cart/update/', update_quantity),
    path('api/categories/', api_categories),
]
