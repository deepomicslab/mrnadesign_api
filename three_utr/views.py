from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

import json

from three_utr.models import three_utr
from three_utr.serializers import three_utrSerializer

class LargeResultsSetPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'pagesize'
    max_page_size = 10000


class three_utrViewSet(APIView):

    queryset = three_utr.objects.order_by('id')
    serializer_class = three_utrSerializer
    pagination_class = LargeResultsSetPagination

    def get(self, request):
        querydict = request.query_params.dict()
        
        if 'sorter' in querydict and querydict['sorter'] != '':
            sorterjson = json.loads(querydict['sorter'])
            order = sorterjson['order']
            columnKey = sorterjson['columnKey']
            if order == 'false':
                self.queryset = self.queryset.order_by('id')
            elif order == 'ascend':
                self.queryset = self.queryset.order_by(columnKey)
            else:  # 'descend
                self.queryset = self.queryset.order_by('-'+columnKey)

        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(self.queryset, request)
        serializer = three_utrSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
