from django.urls import include, path
from rest_framework.routers import DefaultRouter

v1_router = DefaultRouter()



urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]