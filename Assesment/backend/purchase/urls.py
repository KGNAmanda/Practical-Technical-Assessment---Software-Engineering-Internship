from django.urls import path
from . import views

urlpatterns = [
    path('', views.home),
    path('purchase/', views.purchase, name='purchase'),
    path('checkout/', views.checkout, name='checkout'),
    path('analytics/', views.analytics, name='analytics'),
    path('products/', views.get_products, name='products'),
]