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
from gtrnadb.models import gtrnadb_genome, gtrnadb_data
from gtrnadb.serializers import gtrnadbGenomeSerializer, gtrnadbDataSerializer


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'pagesize'
    max_page_size = 10000


class gtrnadbViewSet(APIView):

    queryset = gtrnadb_genome.objects.order_by('id')
    serializer_class = gtrnadbGenomeSerializer
    pagination_class = LargeResultsSetPagination

    def get(self, request):
        querydict = request.query_params.dict()
        queryset = self.queryset

        if 'sorter' in querydict and querydict['sorter'] != '':
            sorterjson = json.loads(querydict['sorter'])
            order = sorterjson['order']
            columnKey = sorterjson['columnKey']
            if order == 'false':
                queryset = self.queryset.order_by('id')
            elif order == 'ascend':
                queryset = self.queryset.order_by(columnKey)
            else:  # 'descend
                queryset = self.queryset.order_by('-'+columnKey)

        if 'filter' in querydict and querydict['filter'] != '':
            filter = json.loads(querydict['filter'])
            q_expression = Q()
            for k, v in filter.items():
                if v:
                    q_expression &= Q(**{k + '__in': v})
            queryset = queryset.filter(q_expression)

        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = gtrnadbGenomeSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

class gtrnadbDetailViewSet(APIView):

    queryset = gtrnadb_data.objects.order_by('id')
    serializer_class = gtrnadbDataSerializer
    pagination_class = LargeResultsSetPagination

    def get(self, request):
        querydict = request.query_params.dict()
        genomeid = querydict['genomeid']
        queryset = self.queryset.filter(genomeid = genomeid)

        if 'sorter' in querydict and querydict['sorter'] != '':
            sorterjson = json.loads(querydict['sorter'])
            order = sorterjson['order']
            columnKey = sorterjson['columnKey']
            if order == 'false':
                queryset = self.queryset.order_by('id')
            elif order == 'ascend':
                queryset = self.queryset.order_by(columnKey)
            else:  # 'descend
                queryset = self.queryset.order_by('-'+columnKey)

        if 'filter' in querydict and querydict['filter'] != '':
            filter = json.loads(querydict['filter'])
            q_expression = Q()
            for k, v in filter.items():
                if v:
                    q_expression &= Q(**{k + '__in': v})
            queryset = queryset.filter(q_expression)

        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = gtrnadbDataSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
class gtrnadbDetailCommonViewSet(APIView):

    queryset = gtrnadb_genome.objects.order_by('id')
    serializer_class = gtrnadbGenomeSerializer
    pagination_class = LargeResultsSetPagination

    def get(self, request):
        querydict = request.query_params.dict()
        genomeid = querydict['genomeid']
        queryset = self.queryset.filter(genomeid = genomeid)

        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = gtrnadbGenomeSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data[0])