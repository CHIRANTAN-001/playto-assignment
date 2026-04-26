from django.urls import path, include

urlpatterns = [
    path('payouts/', include('payouts.urls')),
    path('merchants/', include('merchants.urls')),
]