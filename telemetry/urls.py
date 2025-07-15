from django.urls import path
from .views import CompareDriverDriverView, home, CompareDriverDriverViewV2

urlpatterns = [
    path('api/compare/', CompareDriverDriverViewV2.as_view(), name='compare-drivers'),
    path('', home, name='compare')
]