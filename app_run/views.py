from typing import List

from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings
from django.http import Http404

from rest_framework import viewsets, status, serializers
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from rest_framework.views import APIView

from .serializers import RunSerializer, UserSerializer, AthleteInfoSerializer, ChallengesSerializer, PositionsSerializer
from .models import Run, User, AthleteInfo, Challenges, Positions

from geopy.distance import geodesic


@api_view(['GET'])
def company_details(request):
    return Response(
        {"company_name": settings.COMPANY_NAME,
                     "slogan": settings.SLOGAN,
                     "contacts": settings.CONTACTS}, status=status.HTTP_200_OK)


class RunPagination(PageNumberPagination):
    page_size_query_param = 'size'
    max_page_size = 50


class UserPagination(PageNumberPagination):
    page_size_query_param = 'size'
    max_page_size = 50


class RunViewSet(viewsets.ModelViewSet):
    queryset = Run.objects.select_related('athlete').all()
    serializer_class = RunSerializer

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'athlete']
    ordering_fields = ['created_at']
    pagination_class = RunPagination


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.filter(is_superuser=False)
    serializer_class = UserSerializer

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['first_name', 'last_name']
    ordering_fields = ['date_joined']
    pagination_class = UserPagination

    def get_queryset(self):
        qs = self.queryset
        type = self.request.query_params.get('type', None)

        if type == 'coach':
            qs = qs.filter(is_staff=True)
        elif type == 'athlete':
            qs = qs.filter(is_staff=False)
        return qs


class BaseRunAction(APIView):
    def get_run(self, run_id):
        run = Run.objects.filter(id=run_id).first()
        if not run:
            raise Http404
        return run


class RunStartViewSet(BaseRunAction):
    def post(self, response, run_id):
        run = self.get_run(run_id)
        data = {'status': run.status}

        if run.status != Run.RunStatus.INIT:
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        run.status = Run.RunStatus.IN_PROGRESS
        run.save()
        data['status'] = Run.RunStatus.IN_PROGRESS

        return Response(data, status=status.HTTP_200_OK)


class RunStopViewSet(BaseRunAction):
    def score_run_distance(self, run_id):
        positions = Positions.objects.filter(run=run_id)
        total = 0
        for i, pos in enumerate(positions):
            if i == len(positions)-1:
                continue
            cords1 = (pos.latitude, pos.longitude)
            cords2 = (positions[i+1].latitude, positions[i+1].longitude)
            total += geodesic(cords1, cords2).kilometers
        return total

    def post(self, response, run_id):
        run = self.get_run(run_id)

        data = {'status': run.status}

        if run.status != Run.RunStatus.IN_PROGRESS:
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        run.status = Run.RunStatus.FINISHED
        run.distance = self.score_run_distance(run.id)
        run.save()
        data['distance'] = run.distance

        # Выполнение челенджа за 10 законченных забегов
        total_runs = Run.objects.filter(athlete=run.athlete).filter(status='finished').count()
        if total_runs == 10:
            Challenges.objects.get_or_create(full_name="Сделай 10 Забегов!", athlete=run.athlete)
            data['Challenge complete!!'] = 'Do 10 runs'

        created = Challenges.objects.get(full_name="Пробеги 50 километров!", athlete=run.athlete)
        if not created:
            total_distance = sum(Run.objects.filter(status='finished', athlete=run.athlete).values_list('distance', flat=True))
            if total_distance >= 50:
                data['Challenge complete!'] = 'Run 50 km!'
                Challenges.objects.create(full_name="Пробеги 50 километров!", athlete=run.athlete)


        return Response(data, status=status.HTTP_200_OK)


@api_view(['PUT', 'GET'])
def AthleteInfoViewSet(request, user_id):
    user = User.objects.filter(id=user_id).select_related('athleteinfo').first()

    if user == None:
        raise Http404

    athleteinfo, created = AthleteInfo.objects.get_or_create(user=user,defaults={'weight': None, 'goals': None},)

    if request.method == 'GET':
        serializer = AthleteInfoSerializer(athleteinfo)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = AthleteInfoSerializer(athleteinfo, data=request.data)

        if serializer.is_valid():
            weight = serializer.validated_data['weight']
            if weight <= 0 or weight >= 900:
                return Response({'Error': 'Weight must be > 0 and < 900'}, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChallengesViewSet(viewsets.ModelViewSet):
    queryset = Challenges.objects.all()
    serializer_class = ChallengesSerializer

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['athlete']
    #ordering_fields = ['created_at']
    #pagination_class = RunPagination


class PositionsViewSet(viewsets.ModelViewSet):
    queryset = Positions.objects.all()
    serializer_class = PositionsSerializer

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['run', 'id']







