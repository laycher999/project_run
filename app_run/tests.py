from django.test import TestCase

from .models import Run

# Create your tests here.
def jopa():
    runs = Run.objects.filter(id=1)
    total_distance = sum(runs.filter(status='finished').values_list('distance', flat=True))
    print(total_distance)
    return total_distance

print(jopa())