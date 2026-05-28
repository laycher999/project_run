from django.contrib import admin
from django.urls import path, include

from rest_framework.routers import DefaultRouter
from debug_toolbar.toolbar import debug_toolbar_urls

from app_run.views import company_details, AthleteInfoViewSet, ChallengesViewSet, PositionsViewSet, \
    CollectibleItemViewSet, UploadFileViewSet, SubscribeViewSet, ChallengesSummaryViewSet
from app_run.views import RunViewSet, UserViewSet, RunStartViewSet, RunStopViewSet

router = DefaultRouter()
routes = [
    ('runs', RunViewSet),
    ('users', UserViewSet),
    ('challenges', ChallengesViewSet),
    ('positions', PositionsViewSet),
    ('collectible_item', CollectibleItemViewSet),
           ]
for prefix, viewset in routes:
    router.register(f'api/{prefix}', viewset)


router.register('api/challenges_summary', ChallengesSummaryViewSet, 'challenges-summary')

urlpatterns = [
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
    path('api/company_details/', company_details),
    path('api/runs/<int:run_id>/start/', RunStartViewSet.as_view()),
    path('api/runs/<int:run_id>/stop/', RunStopViewSet.as_view()),
    path('api/athlete_info/<int:user_id>/', AthleteInfoViewSet),
    path('api/upload_file/', UploadFileViewSet),
    path('api/subscribe_to_coach/<int:coach_id>/', SubscribeViewSet.as_view())
    ] + debug_toolbar_urls()