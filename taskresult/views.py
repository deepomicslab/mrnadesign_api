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
    taskid = int(querydict['taskid'])
    mrnatask_obj = mrna_task.objects.filter(id=taskid)[0]

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
    querydict = request.query_params.dict()
    taskid = querydict['taskid']
    subtask_name = querydict['protein_subtask_name']
    task_obj = mrna_task.objects.filter(id = taskid)[0]
    fpath = task_obj.output_result_path + subtask_name + '/'
    df = pd.read_csv(fpath+'summary/results.tsv',sep='\t').replace({np.nan: None})
    data = df.to_dict(orient='records')
    with open(fpath + 'sequence.fasta', 'r') as fasfile:
        for record in SeqIO.parse(fasfile, 'fasta'):
                sequence = str(record.seq)
    return Response({'result': data, 'sequence':sequence})

@api_view(['GET'])
def viewprimarystructure(request):
    querydict = request.query_params.dict()
    taskid = querydict['taskid']
    subtask_name = querydict['protein_subtask_name']
    task_obj = mrna_task.objects.filter(id = taskid)[0]
    fpath = task_obj.output_result_path + subtask_name + '/'

    with open(fpath + 'sequence.fasta', 'r') as fasfile:
        for record in SeqIO.parse(fasfile, 'fasta'):
                sequence = str(record.seq)

    df = pd.read_csv(fpath+'summary/results.tsv',sep='\t').replace({np.nan: None})
    def _get_splitSeqData(df):
        grouping_key = 'component_type'
        result = {
            category: sorted([
                {col: row[col] for col in df.columns if col != grouping_key}
                for index, row in group.iterrows()
            ], key=lambda x: (x['start'], x['end']))
            for category, group in df.groupby(grouping_key)
        }
        return result
    def _get_render_info(splitSeqData):
        ddf_list = {}
        for type in list(splitSeqData.keys()):
            ddf = pd.DataFrame()
            color_info = [0] * len(sequence)
            belongings_info = [set() for _ in range(len(sequence))]
            highlight_info = [[1, 0] for _ in range(len(sequence))]
            
            type_result = splitSeqData.get(type, [])
            if type in ['main_regions', 'IRES', 'stem-loop_structure']:
                continue
            elif type == 'uORF':
                color_count = 1
                for entry_idx, entry in enumerate(type_result): # 第几段，段 entry
                    start = entry['start'] # start is from 1, not 0
                    end = entry['end']
                    for _i in range(start, end + 1):
                        i = _i - 1
                        if _i >= start and _i < start + 3 and _i <= end:
                            color_info[i] = color_count
                        belongings_info[i].add(entry_idx)
                        highlight_info[i][0] = min(highlight_info[i][0], start)
                        highlight_info[i][1] = max(highlight_info[i][1], end)
                    color_count += 1
            elif type == 'restriction_sites':
                color_count = 1
                for entry_idx, entry in enumerate(type_result): # 第几段，段 entry
                    start = entry['start'] # start is from 1, not 0
                    end = entry['end']
                    for _i in range(start, end + 1):
                        i = _i - 1
                        if _i == start:
                            color_info[i] = color_count
                        belongings_info[i].add(entry_idx)
                        highlight_info[i][0] = min(highlight_info[i][0], start)
                        highlight_info[i][1] = max(highlight_info[i][1], end)
                    color_count += 1

            ddf['node'] = [i for i in sequence] # ATCG 等
            ddf['color'] = color_info # 0 没有颜色, > 0 不同颜色
            ddf['belongings'] = belongings_info # 出现在哪些段
            ddf['highlight_range'] = highlight_info # hightlight 范围

            # Create a new column to track if a row can be grouped
            ddf['can_group'] = (ddf['color'].shift() == ddf['color']) & (ddf['belongings'].shift() == ddf['belongings']) & (ddf['highlight_range'].shift() == ddf['highlight_range'])
            ddf['group_id'] = (~ddf['can_group']).cumsum()

            # Group by the unique group id and aggregate
            ddf = ddf.groupby(['group_id']).agg({
                'color': 'first',  # Keep the first color
                'belongings': 'first',  # Keep the first belongings
                'highlight_range': 'first',  # Keep the first highlight_range
                'node': ''.join  # Concatenate node values
            }).reset_index(drop=True)

            ddf['belongings'] = [list(i) for i in ddf['belongings']]
            ddf['highlight_range'] = [list(i) for i in ddf['highlight_range']]
            ddf = ddf[['node', 'color', 'belongings', 'highlight_range']]

            ddf_list[type] = ddf.T

        return ddf_list
    
    split_seq_data = _get_splitSeqData(df)
    render_info = _get_render_info(split_seq_data)

    return Response({'splitSeqData': split_seq_data, 'render_info': render_info, 'sequence':sequence})

@api_view(['GET'])
def viewscoring(request):
    querydict = request.query_params.dict()
    taskid = querydict['taskid']
    task_obj = mrna_task.objects.filter(id = taskid)[0]
    fpath = task_obj.output_result_path
    scoring_df = pd.read_csv(fpath+'seq_score_results.tsv',sep='\t').replace({np.nan: None})
    
    # sorting
    sorted_scoring_df = scoring_df
    if 'sorter' in querydict.keys():
        sorterjson = json.loads(querydict['sorter'])
        order = sorterjson['order']
        columnKey = sorterjson['columnKey']
        sorted_scoring_df = sorted_scoring_df.sort_values(by=columnKey, ascending=order=='ascend')
    return Response({'result': sorted_scoring_df})

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
        'sequence': L[1][:-1],
        'structure': L[2].split(' ')[0],}) # [:-1] is to remove the '\n'