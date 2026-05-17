from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from django.conf import settings

from .serializers import RunSerializer, UserSerializer
from .models import Run, User

class RunViewSet(viewsets.ModelViewSet):
    queryset = Run.objects.all()
    serializer_class = RunSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        qs = self.queryset
        type = self.request.query_params.get('Type', None)
        if type:
            qs = qs.filter(is_staff=True)
        return qs

@api_view(['GET'])
def company_details(request):
    return Response(
        {"company_name": settings.COMPANY_NAME,
                     "slogan": settings.SLOGAN,
                     "contacts": settings.CONTACTS}, status=status.HTTP_200_OK)