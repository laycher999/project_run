from django.contrib import admin
from django.urls import path, include

from rest_framework.routers import DefaultRouter
from debug_toolbar.toolbar import debug_toolbar_urls

from app_run.views import company_details, AthleteInfoViewSet, ChallengesViewSet
from app_run.views import RunViewSet, UserViewSet, RunStartViewSet, RunStopViewSet

router = DefaultRouter()
routes = [
           ('runs', RunViewSet),
           ('users', UserViewSet),
           ('challenges', ChallengesViewSet)
           ]
for prefix, viewset in routes:
    router.register(f'api/{prefix}', viewset)

urlpatterns = [
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
    path('api/company_details/', company_details),
    path('api/runs/<int:run_id>/start/', RunStartViewSet.as_view()),
    path('api/runs/<int:run_id>/stop/', RunStopViewSet.as_view()),
    path('api/athlete_info/<int:user_id>/', AthleteInfoViewSet),
    ] + debug_toolbar_urls()