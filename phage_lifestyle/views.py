from rest_framework import viewsets
from phage_lifestyle.models import phage_lifestyle
from phage_lifestyle.serializers import phage_lifestyleSerializer


class phage_lifestyleViewSet(viewsets.ModelViewSet):
    queryset = phage_lifestyle.objects.all()
    serializer_class = phage_lifestyleSerializer
