from django.contrib import admin
from django.urls import path, include

from rest_framework.routers import DefaultRouter
from debug_toolbar.toolbar import debug_toolbar_urls

from app_run.views import company_details
from app_run.views import RunViewSet, UserViewSet, RunStart, RunStop

router = DefaultRouter()
router.register('api/runs', RunViewSet)
router.register('api/users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
    path('api/company_details/', company_details),
    path('api/runs/<int:id>/start/', RunStart.as_view()),
    path('api/runs/<int:id>/stop/', RunStop.as_view())
    ] + debug_toolbar_urls()