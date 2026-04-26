from django.urls import path
from .views import PayoutView

urlpatterns = [
    path('', PayoutView.as_view()),
]