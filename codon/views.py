from django.shortcuts import render
from django.db import models
from django.http import FileResponse, HttpResponse
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view

import json
import pandas as pd
import numpy as np

from mrnadesign_api import settings_local as local_settings
from codon.models import CodonPair
from codon.serializers import CodonPairSerializer

class LargeResultsSetPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'pagesize'
    max_page_size = 10000

class codonpairViewSet(APIView):

    queryset = CodonPair.objects.order_by('id')
    serializer_class = CodonPairSerializer
    pagination_class = LargeResultsSetPagination

    def get(self, request):
        querydict = request.query_params.dict()
        tissue = querydict['tissue']
        calculation_type = querydict['calculation_type']

        if tissue == 'ALL':
            queryset = self.queryset.filter(calculation_type=calculation_type)
        else:
            queryset = self.queryset.filter(calculation_type=calculation_type).values('Dinucleotide', tissue)
        
        if 'sorter' in querydict and querydict['sorter'] != '':
            sorterjson = json.loads(querydict['sorter'])
            order = sorterjson['order'] 
            columnKey = sorterjson['columnKey']
            if order == 'false' or order == False: 
                queryset = queryset.order_by('id')
            elif order == 'ascend':
                queryset = queryset.order_by(columnKey)
            else:  # 'descend
                queryset = queryset.order_by('-'+columnKey)

        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(queryset, request)

        if tissue == 'ALL':
            serializer = CodonPairSerializer(result_page, many=True)
        else:
            class DynamicFieldsModelSerializer(CodonPairSerializer):
                class Meta(CodonPairSerializer.Meta):
                    model = CodonPair
                    fields = ('Dinucleotide', tissue)
            serializer = DynamicFieldsModelSerializer(result_page, many=True, context={'fields': ('Dinucleotide', tissue)})
        return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
def codonpairHeatmapViewSet(request):
    querydict = request.query_params.dict()
    calculation_type = querydict['calculation_type']
    tissue = querydict['tissue']
    queryset = CodonPair.objects.filter(calculation_type=calculation_type).values('Dinucleotide', tissue)

    dinucleotides = [i['Dinucleotide'] for i in queryset]
    codons = np.unique([codon for dinucleotide in dinucleotides for codon in dinucleotide.split('-')])

    mat = []
    for i in queryset:
        codon1, codon2 = i['Dinucleotide'].split('-')
        # the x and y axises seems reversed in the frontend heatmap (vue echarts)
        mat.append([np.where(codons == codon2)[0][0], np.where(codons == codon1)[0][0], i[tissue]]) 
    
    return Response({'mat': mat, 'codons': codons.tolist()})

@api_view(['GET'])
def codonpairDownloadViewSet(request):
    querydict = request.query_params.dict()
    calculation_type = querydict['calculation_type']
    tissue = querydict['tissue']
    filename = 'codonpair_' + calculation_type + '_' + tissue

    if tissue == 'ALL':
        fields_to_exclude = {'id', 'basetissue_ptr', 'calculation_type'}
        fields = [field.name for field in CodonPair._meta.get_fields() if field.name not in fields_to_exclude]
        fields_to_include = ['Dinucleotide'] + [field for field in fields if field != 'Dinucleotide']
        queryset = CodonPair.objects.filter(calculation_type=calculation_type).values(*fields_to_include)
    else:
        queryset = CodonPair.objects.filter(calculation_type=calculation_type).values('Dinucleotide', tissue)

    df = pd.DataFrame(list(queryset))

    response = HttpResponse(content_type='text/csv')
    from datetime import datetime
    now = datetime.now()
    timestamp = datetime.timestamp(now)
    filename += '_' + str(round(timestamp)) + '.csv'
    response['Content-Disposition'] = 'attachment; filename="'+filename
    df.to_csv(path_or_buf=response)
    return response
