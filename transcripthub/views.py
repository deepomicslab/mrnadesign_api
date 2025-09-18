from django.shortcuts import render
from django.db import models
from django.db.models import Q
from django.http import FileResponse
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view

import json

from mrnadesign_api import settings_local as local_settings
from transcripthub.models import transcripthub_assembly, transcripthub_annotation, genome_seq
from transcripthub.serializers import transcripthubAssemblySerializer, transcripthubAnnotationSerializer, genomeSeqSerializer

class LargeResultsSetPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'pagesize'
    max_page_size = 10000


class transcripthubAssemblyViewSet(APIView):

    queryset = transcripthub_assembly.objects.order_by('id')
    serializer_class = transcripthubAssemblySerializer
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
        serializer = transcripthubAssemblySerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

class transcripthubAnnotationViewSet(APIView):

    queryset = transcripthub_annotation.objects.all().order_by('id')
    serializer_class = transcripthubAnnotationSerializer
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
        result_page = paginator.paginate_queryset(self.queryset, request)
        serializer = transcripthubAnnotationSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
def transcripthubAnnotationSequenceView(request):
    querydict = request.query_params.dict()
    trans_id = querydict['id']
    trans_obj = transcripthub_annotation.objects.filter(id = trans_id)[0]
    genome_obj = trans_obj.genome_sequence
    s = trans_obj.start
    e = trans_obj.end
    return Response({'genome_sequence': genome_obj.sequence if genome_obj else '', 'start': s, 'end': e})