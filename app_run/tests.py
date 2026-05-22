from django.test import TestCase
from .serializers import CollectibleItemSerializer
from .models import CollectibleItem

from openpyxl import load_workbook

wb = load_workbook(filename='/Users/laycher/Downloads/upload_example.xlsx')

wb = wb.worksheets[0].values
failed = []

for i, row in enumerate(wb):
    if i == 0:
        continue
    name, uid, value, latitude, longitude, url = row
    try:
        CollectibleItem.objects.create(name=name, uid=uid, value=value, latitude=latitude, longitude=longitude, picture=url)
    except:
        failed.append(list(row))


