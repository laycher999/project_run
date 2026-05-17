from django.contrib import admin
from django.urls import path, include

from rest_framework.routers import DefaultRouter
from debug_toolbar.toolbar import debug_toolbar_urls

from app_run.views import company_details
from app_run.views import RunViewSet, UserViewSet

router = DefaultRouter()
router.register('api/runs', RunViewSet)
router.register('api/users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
    path('api/company_details/', company_details)
    ] + debug_toolbar_urls()