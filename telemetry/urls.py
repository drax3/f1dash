from django.urls import path
from .views import CompareDriverDriverView, home

urlpatterns = [
    path('api/compare/', CompareDriverDriverView.as_view(), name='compare-drivers'),
    path('', home, name='compare')
]