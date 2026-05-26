# from django.test import TestCase
# from .serializers import CollectibleItemSerializer
# from .models import CollectibleItem, User
#
# t1 = CollectibleItem.objects.all()[0]
# print(t1)
# t2 = User.objects.all()[1]
# print(t2)
# #t1.user.add(t2)
#
#

from geopy.distance import geodesic


a = geodesic((50,50), (40,40))
print(a.kilometers*1000)