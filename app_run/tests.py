from django.test import TestCase
from .serializers import CollectibleItemSerializer
from .models import CollectibleItem, User

t1 = CollectibleItem.objects.all()[0]
print(t1)
t2 = User.objects.all()[1]
print(t2)
#t1.user.add(t2)


