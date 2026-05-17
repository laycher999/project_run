from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.views import APIView

from django.conf import settings
from django.http import Http404, HttpResponseBadRequest, BadHeaderError
from .serializers import RunSerializer, UserSerializer
from .models import Run, User


@api_view(['GET'])
def company_details(request):
    return Response(
        {"company_name": settings.COMPANY_NAME,
                     "slogan": settings.SLOGAN,
                     "contacts": settings.CONTACTS}, status=status.HTTP_200_OK)


class RunPagination(PageNumberPagination):
    page_size = 0
    page_size_query_param = 'size'
    max_page_size = 50


class UserPagination(PageNumberPagination):
    page_size = 0
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
    def get_run(self, id):
        run = Run.objects.filter(id=id).first()
        if not run:
            raise Http404

        return run


class RunStart(BaseRunAction):
    def post(self, response, id):
        run = self.get_run(id)

        data = {'status': run.status}

        if run.status != Run.RunStatus.INIT:
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        run.status = Run.RunStatus.IN_PROGRESS
        run.save()
        data['status'] = Run.RunStatus.IN_PROGRESS

        return Response(data, status=status.HTTP_200_OK)


class RunStop(BaseRunAction):
    def post(self, response, id):
        run = self.get_run(id)

        data = {'status': run.status}

        if run.status != Run.RunStatus.IN_PROGRESS:
            print('Hello')
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        run.status = Run.RunStatus.FINISHED
        run.save()
        data['status'] = Run.RunStatus.FINISHED
        return Response(data, status=status.HTTP_200_OK)

