from django.shortcuts import render
from django.http import FileResponse, HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

from mrna_task.models import mrna_task
from mrna_task.serializers import mrna_taskSerializer
from taskresult.models import lineardesign_taskresult, prediction_taskresult
from taskresult.serializers import lineardesign_taskresultSerializer, prediction_taskresultSerializer
from mrnadesign_api import settings_local as local_settings

import pandas as pd
import json
import numpy as np
import os
import zipfile
from io import BytesIO
from datetime import datetime
from Bio import SeqIO

@api_view(['GET'])
def lineardesignresultView(request):
    querydict = request.query_params.dict()
    taskid = querydict['taskid']
    mrnatask_obj = mrna_task.objects.get(id=taskid)

    assert mrnatask_obj.analysis_type == 'Linear Design'
    queryset = lineardesign_taskresult.objects.filter(id__in = mrnatask_obj.task_results).order_by('id')

    if 'sorter' in querydict and querydict['sorter'] != '':
        sorterjson = json.loads(querydict['sorter'])
        order = sorterjson['order']
        columnKey = sorterjson['columnKey']
        if order == 'false':
            queryset = queryset.order_by('id')
        elif order == 'ascend':
            queryset = queryset.order_by(columnKey)
        else:  # 'descend
            queryset = queryset.order_by('-'+columnKey)
    
    serializer = lineardesign_taskresultSerializer(queryset, many=True)
    return Response({'results': serializer.data})

@api_view(['GET'])
def predictionresultView(request): #####################################################################
    querydict = request.query_params.dict()
    taskid = querydict['taskid']
    mrnatask_obj = mrna_task.objects.get(id=taskid)

    assert mrnatask_obj.analysis_type == 'Prediction'
    queryset = prediction_taskresult.objects.filter(id__in = mrnatask_obj.task_results).order_by('id')

    if 'sorter' in querydict and querydict['sorter'] != '':
        sorterjson = json.loads(querydict['sorter'])
        order = sorterjson['order']
        columnKey = sorterjson['columnKey']
        if order == 'false':
            queryset = queryset.order_by('id')
        elif order == 'ascend':
            queryset = queryset.order_by(columnKey)
        else:  # 'descend
            queryset = queryset.order_by('-'+columnKey)
    
    serializer = prediction_taskresultSerializer(queryset, many=True)
    return Response({'results': serializer.data})

@api_view(['GET'])
def getZipData(request):
    querydict = request.query_params.dict()
    taskid = querydict['taskid']
    mrnatask_obj = mrna_task.objects.get(id=taskid)
    filename = "AnalysisResult"
    fpath = mrnatask_obj.output_result_path + 'result.txt'

    s = BytesIO()
    zf = zipfile.ZipFile(s, "w")
    # server里的path, zip folder里面的目标path
    zf.write(fpath, 'result.txt')
    zf.close()

    now = datetime.now()
    timestamp = datetime.timestamp(now)

    response = HttpResponse(
        s.getvalue(), content_type="application/x-zip-compressed")
    filename += '_' + str(round(timestamp)) + '.zip'
    response['Content-Disposition'] = 'attachment; filename="'+filename
    return response

@api_view(['GET'])
def sequencemarker(request):
    res_path = local_settings.DEMO_ANALYSIS + 'demouser_prediction_full/prediction_results/SEQ000000/'
    df = pd.read_csv(res_path + 'summary/results.tsv',sep='\t').replace({np.nan: None})
    data = df.to_dict(orient='records')
    with open(res_path + 'sequence.fasta', 'r') as fasfile:
        for record in SeqIO.parse(fasfile, 'fasta'):
                sequence = str(record.seq)
    return Response({'result': data, 'sequence':sequence})

@api_view(['GET'])
def viewproteinstructure(request):
    querydict = request.query_params.dict()
    taskid = querydict['taskid']
    subtask_name = querydict['protein_subtask_name']
    task_obj = mrna_task.objects.filter(id = taskid)[0]
    fpath = task_obj.output_result_path + subtask_name + '/protein_structure.pdb'
    url='https://mrnaapi.deepomics.org/tasks/files/'+fpath
    return Response({'type': 'pdb', 'fileurl': url})

@api_view(['GET'])
def viewresultfile(request, path):
    file = open('/'+path, 'rb') # 是一个绝对路径，home/platform/...., 在前面加上根目录的 “/” 
    response = FileResponse(file)
    filename = file.name.split('/')[-1]
    response['Content-Disposition'] = "attachment; filename="+filename
    response['Content-Type'] = 'text/plain'
    response['Access-Control-Allow-Origin'] = 'https://www.ncbi.nlm.nih.gov' 
    response["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
    return response

@api_view(['GET'])
def viewsecondarystructure(request):
    querydict = request.query_params.dict()
    taskid = querydict['taskid']
    subtask_name = querydict['protein_subtask_name']
    task_obj = mrna_task.objects.filter(id = taskid)[0]
    fpath = task_obj.output_result_path + subtask_name + '/RNAfold.output'
    with open(fpath, 'r') as fin:
        L = fin.readlines()
    return Response({
        'subtask_name': L[0][1:-1], 
        'sequence': L[1][1:-1],
        'structure': L[2].split(' ')[0],}) # [:-1] is to remove the '\n'