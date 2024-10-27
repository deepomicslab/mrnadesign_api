from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view

import json

from tantigen.models import tantigen
from tantigen.serializers import tantigenSerializer

class LargeResultsSetPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'pagesize'
    max_page_size = 10000


class tantigenViewSet(APIView):

    queryset = tantigen.objects.order_by('id')
    serializer_class = tantigenSerializer
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
        serializer = tantigenSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
def getstats(request):
    num = len(tantigen.objects.all())
    num_antigen_name = len(tantigen.objects.distinct('antigen_name'))
    num_gene_card = len(tantigen.objects.distinct('gene_card_id'))
    return Response({
        'num': num,
        'num_antigen_name': num_antigen_name,
        'num_gene_card': num_gene_card,
    })