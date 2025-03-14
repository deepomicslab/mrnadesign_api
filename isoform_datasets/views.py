from django.db.models import Q
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from isoform_datasets.models import Datasets
from isoform_datasets.serializers import DatasetsSerializer


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'pagesize'
    max_page_size = 10000

class isoformdbDatasetsViewSet(viewsets.ModelViewSet):
    queryset = Datasets.objects.order_by('id')
    serializer_class = DatasetsSerializer
    pagination_class = LargeResultsSetPagination

    def get(self, request):
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(self.queryset, request)
        serializer = DatasetsSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class DatasetsSearchView(APIView):
    pagination_class = LargeResultsSetPagination

    def get(self, request, *args, **kwargs):
        search_str = request.query_params.dict()['search']
        if search_str:
            datasets = Datasets.objects.filter(Q(name__icontains=search_str) | Q(cancer_name__icontains=search_str) | Q(
                database__icontains=search_str) | Q(data_type__icontains=search_str))
        else:
            datasets = Datasets.objects.order_by('id')
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(datasets, request)
        serializer = DatasetsSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class DatasetDetailView(APIView):
    def get(self, request: Request, *args, **kwargs):
        query_dict = request.query_params.dict()
        if 'id' in query_dict:
            datasets = Datasets.objects.get(id=query_dict['id'])
        elif 'name' in query_dict:
            datasets = Datasets.objects.get(name=query_dict['name'])
        else:
            return Response("Dataset detail not found!", status=404)
        datasets_data = DatasetsSerializer(datasets).data
        return Response(datasets_data)


# class datasetCreateView(APIView):
#     def post(self, request, *args, **kwargs):
#         name = request.data.get('name')
#         if Datasets.objects.filter(name=name).exists():
#             queryset = Datasets.objects.get(name=name)
#             serializer = DatasetsSerializer(queryset)
#             return Response(serializer.data, status=409)
#         serializer = DatasetsSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=201)
#         return Response(serializer.errors, status=400)
