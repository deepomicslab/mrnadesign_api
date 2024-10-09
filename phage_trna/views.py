from rest_framework import viewsets
from phage_trna.models import phage_trna
from phage_trna.serializers import phage_trnaSerializer
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'pagesize'
    max_page_size = 10000


class phage_trnaViewSet(viewsets.ModelViewSet):
    queryset = phage_trna.objects.all()
    serializer_class = phage_trnaSerializer


class phage_trnasViewSet(viewsets.ModelViewSet):
    queryset = phage_trna.objects.order_by('id')
    serializer_class = phage_trnaSerializer
    pagination_class = LargeResultsSetPagination


class trnaView(APIView):
    def get(self, request, *args, **kwargs):
        query_dict = request.query_params.dict()
        phageid = int(query_dict['phageid'])
        queryset = phage_trna.objects.filter(phage_id=phageid)
        serializer = phage_trnaSerializer(queryset, many=True)
        return Response(serializer.data)
