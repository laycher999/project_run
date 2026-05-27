from django.conf import settings
from django.db.models import QuerySet, Count, Q, Avg
from django.http import Http404
from openpyxl import load_workbook

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from rest_framework.views import APIView

from .serializers import RunSerializer, UserSerializer, AthleteInfoSerializer, ChallengesSerializer, \
    PositionsSerializer, CollectibleItemSerializer, UserSerializerDetailed
from .models import Run, User, AthleteInfo, Challenges, Positions, CollectibleItem

from geopy.distance import geodesic, Distance


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
    queryset = User.objects.filter(is_superuser=False).annotate(runs_finished=Count('run', filter=Q(run__status='finished')))
    serializer_class = UserSerializer

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['first_name', 'last_name']
    ordering_fields = ['date_joined']
    pagination_class = UserPagination

    def get_serializer_class(self):
        # Возвращаем базовый сериализатор для метода list
        if self.action == 'list':
            return UserSerializer
        # Возвращаем детализированный сериализатор для метода retrieve
        elif self.action == 'retrieve':
            return UserSerializerDetailed
        return super().get_serializer_class() # Если ни одно из условий не выполнено, вызываем базовую реализацию


    def get_queryset(self):
        qs = self.queryset
        user_type = self.request.query_params.get('type', None)

        if user_type == 'coach':
            qs = qs.filter(is_staff=True)
        elif user_type == 'athlete':
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
    def score_run_distance(self, positions) -> Distance:
        total = 0
        for i, pos in enumerate(positions):
            if i == len(positions)-1:
                continue
            cords1 = (pos.latitude, pos.longitude)
            cords2 = (positions[i+1].latitude, positions[i+1].longitude)
            total += geodesic(cords1, cords2).kilometers
        return total

    def score_run_time(self, positions: QuerySet[Positions]):
        if positions:
            start = positions.first().date_time
            end = positions.last().date_time
            duration = end - start
            return duration.total_seconds()
        else:
            return None

    def post(self, response, run_id):
        run = self.get_run(run_id)
        positions = Positions.objects.filter(run=run_id).order_by('date_time')
        data = {'status': run.status}
        if run.status != Run.RunStatus.IN_PROGRESS:
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        run.status = Run.RunStatus.FINISHED
        distance = self.score_run_distance(positions)
        run.distance = distance
        run.run_time_seconds = self.score_run_time(positions)
        run.speed = round(positions.aggregate(Avg('speed'))['speed__avg'], 2)
        run.save()
        data['distance'] = run.distance


        # Выполнение челенджа за 10 законченных забегов
        total_runs = Run.objects.filter(athlete=run.athlete).filter(status='finished').count()
        if total_runs == 10:
            Challenges.objects.get_or_create(full_name="Сделай 10 Забегов!", athlete=run.athlete)
            data['Challenge complete!!'] = 'Do 10 runs'

        # Челендж 50 км
        created = Challenges.objects.filter(full_name="Пробеги 50 километров!", athlete=run.athlete).exists()
        if not created:
            total_distance = sum(Run.objects.filter(status='finished', athlete=run.athlete).values_list('distance', flat=True))
            if total_distance >= 50:
                data['Challenge complete!'] = 'Run 50 km!'
                Challenges.objects.create(full_name="Пробеги 50 километров!", athlete=run.athlete)

        # 2 километра за 10 минут!
        created = Challenges.objects.filter(full_name="# 2 километра за 10 минут!", athlete=run.athlete).exists()
        if not created:
            if run.distance >= 10 and run.run_time_seconds <= 600:
                data['Challenge complete!'] = 'New'
                Challenges.objects.create(full_name="2 километра за 10 минут!", athlete=run.athlete)




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

    def create(self, request, *args, **kwargs):
        self.get_collectible_item(request.data)
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        current_position = serializer.validated_data
        run_id = current_position['run'].id
        positions_in_run = list(Positions.objects.filter(run=run_id).order_by('date_time'))
        print(positions_in_run)
        if len(positions_in_run) == 0:
            serializer.save()
            return
        current_pos_cords = (current_position['latitude'], current_position['longitude'])
        prev_pos = positions_in_run[-1]
        prev_pos_cords = (prev_pos.latitude, prev_pos.longitude)
        runned_distance = geodesic(current_pos_cords, prev_pos_cords)
        runned_time = (current_position['date_time'] - prev_pos.date_time).total_seconds()
        speed = round(runned_distance.m / runned_time, 2) # V METPAX/SEC
        total_distance = round(runned_distance.km + prev_pos.distance, 2) # V KILOMETPAX
        serializer.save(speed=speed, distance=total_distance)

    def get_collectible_item(self, data):
        user = Run.objects.filter(id=data['run'])[0].athlete
        run_cords = (data['latitude'], data['longitude'])
        items = CollectibleItem.objects.all()
        for item in items:
            try:
                item_cords = (item.latitude, item.longitude)
                distance = geodesic(run_cords, item_cords).meters
                if distance <= 100:
                    item.user.add(user)
                    return True
            except:
                pass
        return False



class CollectibleItemViewSet(viewsets.ModelViewSet):
    queryset = CollectibleItem.objects.all()
    serializer_class = CollectibleItemSerializer


@api_view(['POST'])
def UploadFileViewSet(request):
    uploaded_file = request.FILES.get('file')

    if uploaded_file is None:
        return Response({'error': 'Файл не передан'}, status=400)

    wb = load_workbook(uploaded_file)
    wb = wb.worksheets[0].values
    failed = []
    for i, row in enumerate(wb):
        if i == 0:
            continue

        name, uid, value, latitude, longitude, url = row

        data = {
            'name': name,
            'uid': uid,
            'value': value,
            'latitude': latitude,
            'longitude': longitude,
            'picture': url,
        }
        serializer = CollectibleItemSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
        else:
            failed.append(list(row))


    return Response(failed)


