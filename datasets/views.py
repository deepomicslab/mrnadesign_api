from rest_framework import viewsets
from datasets.models import datasets
from datasets.serializers import datasetsSerializer

class datasetsViewSet(viewsets.ModelViewSet):
    queryset = datasets.objects.all()
    serializer_class = datasetsSerializer
