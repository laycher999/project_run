from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from rest_framework.views import APIView

from django.conf import settings
from django.http import Http404
from .serializers import RunSerializer, UserSerializer, AthleteInfoSerializer, ChallengesSerializer
from .models import Run, User, AthleteInfo, Challenges


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
        runs = Run.objects.filter(id=run_id)
        if not runs:
            raise Http404
        return runs


class RunStartViewSet(BaseRunAction):
    def post(self, response, run_id):
        runs = self.get_run(run_id)
        run = runs[0]
        data = {'status': run.status}

        if run.status != Run.RunStatus.INIT:
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        run.status = Run.RunStatus.IN_PROGRESS
        run.save()
        data['status'] = Run.RunStatus.IN_PROGRESS

        return Response(data, status=status.HTTP_200_OK)


class RunStopViewSet(BaseRunAction):
    def post(self, response, run_id):
        runs = self.get_run(run_id)


        run = runs[0]
        data = {'status': run.status}

        if run.status != Run.RunStatus.IN_PROGRESS:
            return Response(data, status=status.HTTP_400_BAD_REQUEST)



        run.status = Run.RunStatus.FINISHED
        run.save()
        data['status'] = Run.RunStatus.FINISHED

        # Выполнение челенджа за 10 законченных забегов
        total_runs = Run.objects.filter(athlete=run.athlete).filter(status='finished').count()
        if total_runs == 10:
            Challenges.objects.get_or_create(full_name="Сделай 10 Забегов!", athlete=run.athlete)
            data['Achievement!'] = 'Challenge: do 10 runs'

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


class ChallengesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Challenges.objects.all()
    serializer_class = ChallengesSerializer

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['athlete']
    #ordering_fields = ['created_at']
    #pagination_class = RunPagination




