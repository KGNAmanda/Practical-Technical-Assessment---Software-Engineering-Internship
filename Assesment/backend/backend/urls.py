from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def home(request):
    return JsonResponse({
        "message": "Backend is running 🚀",
        "endpoints": {
            "purchase": "/api/purchase/",
            "checkout": "/api/checkout/",
            "analytics": "/api/analytics/",
            "products": "/api/products/"
        }
    })

urlpatterns = [
    path('', home),
    path('admin/', admin.site.urls),
    path('api/', include('purchase.urls')),
]