from django.db.models import Q
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from isoform_datasets.models import Datasets
from isoform_samples.models import Samples
from isoform_samples.serializers import SamplesSerializer

import json


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'pagesize'
    max_page_size = 10000


class SamplesViewSet(viewsets.ModelViewSet):
    queryset = Samples.objects.order_by('id')
    serializer_class = SamplesSerializer
    pagination_class = LargeResultsSetPagination

    def get(self, request):
        print("SamplesViewSet Calling")
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(self.queryset, request)
        serializer = SamplesSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
class isoformdbSamplesDetailViewSet(APIView):
    def get(self, request: Request, *args, **kwargs):
        query_dict = request.query_params.dict()
        if 'id' in query_dict:
            sample = Samples.objects.get(id=query_dict['id'])
        elif 'name' in query_dict:
            sample = Samples.objects.get(name=query_dict['name'])
        else:
            return Response("Sample detail not found!", status=404)
        sample_data = SamplesSerializer(sample).data
        return Response(sample_data)

class SampleSearchView(APIView):
    pagination_class = LargeResultsSetPagination
    def get(self, request, *args, **kwargs):
        print("SampleSearchView Calling")
        query_dict = request.query_params.dict()
        search_str = query_dict.get('search')
        dataset_name = query_dict.get('dataset_name')
        dataset_id = query_dict.get('dataset_id')
        if dataset_id:
            samples = Samples.objects.filter(dataset_id=dataset_id)
        elif dataset_name:
            samples = Samples.objects.filter(dataset_name=dataset_name)
        elif search_str:
            samples = Samples.objects.filter(Q(name__icontains=search_str) | Q(cancer_name__icontains=search_str) | Q(
                dataset_name__icontains=search_str) | Q(primary_site__icontains=search_str))
            paginator = self.pagination_class()
            result_page = paginator.paginate_queryset(samples, request)
            serializer = SamplesSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)
        else:
            return Response("Related samples not found!", status=404)
        print("samples", samples)
        serializer = SamplesSerializer(samples, many=True)
        return Response(serializer.data)


class isoformdbSamplesViewSet(APIView):
    queryset = Samples.objects.order_by('id')
    serializer_class = SamplesSerializer
    pagination_class = LargeResultsSetPagination

    def get(self, request):
        querydict = request.query_params.dict()
        
        queryset = self.queryset
        
        if 'sorter' in querydict and querydict['sorter'] != '':
            sorterjson = json.loads(querydict['sorter'])
            order = sorterjson['order']
            columnKey = sorterjson['columnKey']
            if order == False:
                queryset = queryset.order_by('id')
            elif order == 'ascend':
                queryset = queryset.order_by(columnKey)
            else:  # 'descend
                queryset = queryset.order_by('-'+columnKey)

        if 'filter' in querydict and querydict['filter'] != '':
            filter = json.loads(querydict['filter'])
            q_expression = Q()
            for k, v in filter.items():
                if v:
                    q_expression &= Q(**{k + '__in': v})
            queryset = queryset.filter(q_expression)

        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = SamplesSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


# class sampleCreateView(APIView):
#     def post(self, request, *args, **kwargs):
#         name = request.data.get('name')
#         if Samples.objects.filter(name=name).exists():
#             queryset = Samples.objects.get(name=name)
#             serializer = SamplesSerializer(queryset)
#             return Response(serializer.data, status=409)
#         dataset_id = request.data.get('dataset_id')
#         dataset_name = request.data.get('dataset_name')
#         if not Datasets.objects.filter(id=dataset_id).exists():
#             return Response({'error': f'Dataset {dataset_name} not found, can not load related sample'}, status=404)
#         serializer = SamplesSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=201)
#         return Response(serializer.errors, status=400)
