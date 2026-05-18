from django.test import TestCase

# Create your tests here.
def cords_range(value, cords_range):
    x, y = cords_range
    if value < x or value > y:
        return False
    return True

print(cords_range(555, (-90, 90)))