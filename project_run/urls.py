from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from app_run.views import company_details
from app_run.views import RunViewSet

router = DefaultRouter()
router.register('api/runs', RunViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
    path('api/company_details/', company_details)
    ]