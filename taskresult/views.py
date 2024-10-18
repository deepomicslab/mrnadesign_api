from django.shortcuts import render
from django.http import FileResponse, HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

from mrna_task.models import mrna_task
from mrna_task.serializers import mrna_taskSerializer
from taskresult.models import lineardesign_taskresult
from taskresult.serializers import lineardesign_taskresultSerializer

import pandas as pd
import json
from io import BytesIO
import zipfile
from datetime import datetime
import os

@api_view(['GET'])
def lineardesignresultView(request):
    querydict = request.query_params.dict()
    taskid = querydict['taskid']
    mrnatask_obj = mrna_task.objects.get(id=taskid)

    if mrnatask_obj.analysis_type == 'Linear Design':
        queryset = lineardesign_taskresult.objects.filter(id__in = mrnatask_obj.task_results).order_by('id')
    # else mrnatask_obj.analysis_type == 'Prediction':

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

