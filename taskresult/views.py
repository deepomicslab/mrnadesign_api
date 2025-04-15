from django.shortcuts import render
from django.http import FileResponse, HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination


from mrna_task.models import mrna_task
from mrna_task.serializers import mrna_taskSerializer
from mrnadesign_api import settings_local as local_settings

import pandas as pd
import json
import numpy as np
import os
import zipfile
from io import BytesIO
from datetime import datetime
from Bio import SeqIO
import glob

class LargeResultsSetPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'pagesize'
    max_page_size = 10000

def convert_to_mutation_type(num):
    types = ['control', 'rna-edit', 'indel', 'snp', 'GENE-FUSION', 'rmats', 'spe']
    return types[int(num)]

@api_view(['GET'])
def tsaresultView(request):
    querydict = request.query_params.dict()
    taskid = querydict['taskid']
    mrnatask_obj = mrna_task.objects.get(id=taskid)
    mutation_type = querydict['mutation_type'] if 'mutation_type' in querydict else convert_to_mutation_type(mrnatask_obj.parameters['mutation_type'][0])

    assert mrnatask_obj.analysis_type == 'TSA'

    f = mutation_type + '/' + mrnatask_obj.parameters['sample'] + '.control.jf.csv'
    if mutation_type == 'rmats': 
        f = 'rmats-' + mrnatask_obj.parameters['rmats_as_type'] + '/' + mrnatask_obj.parameters['sample'] + '.control.jf.csv'
    elif mutation_type == 'control':
        f = mrnatask_obj.parameters['sample'] + '.control.fasta.csv'

    merged_df = pd.read_csv(mrnatask_obj.output_result_path + 'annotation/' + f, sep='\t')
    merged_df.columns = [i.replace(' ', '_') for i in merged_df.columns]
    merged_df.fillna('', inplace=True)
    merged_df = merged_df.astype(str)

    if 'sorter' in querydict and querydict['sorter'] != '':
        sorterjson = json.loads(querydict['sorter'])
        order = sorterjson['order']
        columnKey = sorterjson['columnKey']
        if order == 'false':
            merged_df = merged_df.sort_values(by='id', ascending=True)
        elif order == 'ascend':
            merged_df = merged_df.sort_values(by=columnKey, ascending=True)
        else: # 'descend
            merged_df = merged_df.sort_values(by=columnKey, ascending=False)
    if 'filter' in querydict and querydict['filter'] != '':
        filterjson = json.loads(querydict['filter'])
        for k, v in filterjson.items():
            if v:
                merged_df = merged_df[merged_df[k].isin(v)]
                
    data = merged_df.to_dict(orient='records')
    paginator = LargeResultsSetPagination()
    result_page = paginator.paginate_queryset(data, request)
    response = paginator.get_paginated_response(result_page)
    response.data['mutation_types'] = [convert_to_mutation_type(i) for i in mrnatask_obj.parameters['mutation_type']]

    return response

@api_view(['GET'])
def safetyresultView(request):
    querydict = request.query_params.dict()
    taskid = querydict['taskid']
    mrnatask_obj = mrna_task.objects.get(id=taskid)

    assert mrnatask_obj.analysis_type == 'Safety'
    merged_df = pd.read_csv(mrnatask_obj.output_result_path + 'merged_file.csv', index_col=0)
    merged_df.columns = ['id', 'sequence', 'toxicity_score', 'toxicity', 'allergenicity_score', 'allergenicity', 'antigenicity_score', 'antigenicity', 's3_url']

    if 'sorter' in querydict and querydict['sorter'] != '':
        sorterjson = json.loads(querydict['sorter'])
        order = sorterjson['order']
        columnKey = sorterjson['columnKey']
        if order == 'false':
            merged_df = merged_df.sort_values(by='id', ascending=True)
        elif order == 'ascend':
            merged_df = merged_df.sort_values(by=columnKey, ascending=True)
        else: # 'descend
            merged_df = merged_df.sort_values(by=columnKey, ascending=False)
    if 'filter' in querydict and querydict['filter'] != '':
        filterjson = json.loads(querydict['filter'])
        for k, v in filterjson.items():
            if v:
                merged_df = merged_df[merged_df[k].isin(v)]
    return Response({'results': merged_df.to_dict(orient='records'), 'mutation_types': mrnatask_obj.parameters['mutation_type']})

@api_view(['GET'])
def sequencealignresultView(request):
    querydict = request.query_params.dict()
    taskid = querydict['taskid']
    mrnatask_obj = mrna_task.objects.get(id=taskid)

    assert mrnatask_obj.analysis_type == 'Sequence Align'
    with open(mrnatask_obj.output_result_path + 'result.json', "r") as result_file:
        context = json.load(result_file)
    results = context['results']
    # txt_files = context['txt_files']
    return Response({'results': results})

def read_fasta(file_path):
    sequences = []
    for record in SeqIO.parse(file_path, "fasta"):
        sequences.append({
            "header": record.id,
            "sequence": str(record.seq).replace('\n', '')
        })
    return sequences[0] 

@api_view(['GET'])
def antigenscreeningresultView(request):
    querydict = request.query_params.dict()
    taskid = querydict['taskid']
    mrnatask_obj = mrna_task.objects.get(id=taskid)

    assert mrnatask_obj.analysis_type == 'Antigen Screening'
    df = pd.read_csv(mrnatask_obj.output_result_path + 'result.csv', index_col=0)

    info = {
        'input_fasta': read_fasta(mrnatask_obj.user_input_path['fasta'])['sequence'], # only allow input one protein seq in the fasta,
        'peptide_len_min': mrnatask_obj.parameters['peptide_len_min'],
        'peptide_len_max': mrnatask_obj.parameters['peptide_len_max'],
    }
    return Response({'info': info, 'results': df.to_dict(orient='records')})

def get_seq_dict(path):
    res_dict = {}
    with open(path, "r") as file:
        lines = file.readlines()
        for i in range(len(lines)):
            if '>' in lines[i]:
                res_dict[lines[i][:-1]] = [lines[i + 1][:-1], lines[i + 2].split(' ')[0]]
                i += 2
    return res_dict

@api_view(['GET'])
def lineardesignresultView(request):
    querydict = request.query_params.dict()
    taskid = querydict['taskid']
    mrnatask_obj = mrna_task.objects.get(id=taskid)

    assert mrnatask_obj.analysis_type == 'Linear Design'
    lineardesignanalysistype = mrnatask_obj.parameters['lineardesignanalysistype']
    
    with open(mrnatask_obj.output_result_path + 'result.txt', 'r') as fout:
        L = fout.readlines()

    seq_name = []
    sequence = []
    structure = []
    folding_free_energy = []
    cai = []
    for l in L:
        if '>' in l:
            seq_name.append(l[:-1]) # remove '\n'
        elif 'mRNA sequence' in l:
            sequence.append(l.split(' ')[-1][:-1])
        elif 'structure' in l:
            structure.append(l.split(' ')[-1][:-1])
        elif 'folding free energy' in l and 'CAI' in l:
            folding_free_energy.append(l.split(' ')[4])
            cai.append(l.split(' ')[8][:-1]) 

    merged_df = []
    if lineardesignanalysistype == 'cds_plus_35utr':
        utr3_dict = get_seq_dict(mrnatask_obj.output_result_path + '3utr_rnafold.output')
        utr5_dict = get_seq_dict(mrnatask_obj.output_result_path + '5utr_rnafold.output')
        for i in range(len(seq_name)):
            merged_df.append([
                seq_name[i], 
                utr3_dict[seq_name[i]][0], utr3_dict[seq_name[i]][1], 
                sequence[i], structure[i], 
                utr5_dict[seq_name[i]][0], utr5_dict[seq_name[i]][1], 
                float(folding_free_energy[i]), float(cai[i]),])
        merged_df = pd.DataFrame(merged_df, columns=['seq_name', 'utr3_seq', 'utr3_structure', 'sequence', 'structure', 'utr5_seq', 'utr5_structure', 'folding_free_energy', 'cai'])
    elif lineardesignanalysistype == 'cds_only':
        for i in range(len(seq_name)):
            merged_df.append([seq_name[i], sequence[i], structure[i], float(folding_free_energy[i]), float(cai[i]),])
        merged_df = pd.DataFrame(merged_df, columns=['seq_name', 'sequence', 'structure', 'folding_free_energy', 'cai'])

    if 'sorter' in querydict and querydict['sorter'] != '':
        sorterjson = json.loads(querydict['sorter'])
        order = sorterjson['order']
        columnKey = sorterjson['columnKey']
        if order == 'false':
            merged_df = merged_df.sort_values(by='id', ascending=True)
        elif order == 'ascend':
            merged_df = merged_df.sort_values(by=columnKey, ascending=True)
        else: # 'descend
            merged_df = merged_df.sort_values(by=columnKey, ascending=False)
    return Response({'results': merged_df.to_dict(orient='records'), 'lineardesignanalysistype': lineardesignanalysistype})

@api_view(['GET'])
def predictionresultView(request): #####################################################################
    querydict = request.query_params.dict()
    taskid = int(querydict['taskid'])
    mrnatask_obj = mrna_task.objects.filter(id=taskid)[0]

    assert mrnatask_obj.analysis_type == 'Prediction'
    subpaths = glob.glob(mrnatask_obj.output_result_path + '*')
    df = []
    for p in subpaths:
        if 'tsv' in p: continue
        df.append(p.split('/')[-1])
    merged_df = pd.DataFrame(df, columns=['task_name'])

    if 'sorter' in querydict and querydict['sorter'] != '':
        sorterjson = json.loads(querydict['sorter'])
        order = sorterjson['order']
        columnKey = sorterjson['columnKey']
        if order == 'ascend':
            merged_df = merged_df.sort_values(by=columnKey, ascending=True)
        else: # 'descend
            merged_df = merged_df.sort_values(by=columnKey, ascending=False)
    return Response({'results': merged_df.to_dict(orient='records')})

def get_all_files(directory):
    from pathlib import Path
    return [str(file) for file in Path(directory).rglob('*') if file.is_file()]

@api_view(['GET'])
def getZipData(request):
    querydict = request.query_params.dict()
    taskid = querydict['taskid']
    mrnatask_obj = mrna_task.objects.get(id=taskid)
    fpath = mrnatask_obj.output_result_path
    filename = "AnalysisResult"
    
    s = BytesIO()
    zf = zipfile.ZipFile(s, "w")
    assert mrnatask_obj.analysis_type in ['Linear Design', 'Prediction', 'Safety', 'Sequence Align', 'Antigen Screening', 'TSA']
    for i in get_all_files(fpath):
        zf.write(i, i.replace(fpath, '')) # server里的path, zip folder里面的目标path
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
def viewprimarystructuremainregion(request):
    querydict = request.query_params.dict()
    taskid = querydict['taskid']
    subtask_name = querydict['protein_subtask_name']
    task_obj = mrna_task.objects.filter(id = taskid)[0]
    fpath = task_obj.output_result_path + subtask_name + '/'

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
    
    split_seq_data = _get_splitSeqData(df)

    return Response({'splitSeqData': split_seq_data, })

def util_primarystructure_type(fpath, component_type, offset):
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
    def _get_render_info(splitSeqData, type):
        ddf_list = {}
        
        ddf = pd.DataFrame()
        color_info = [0] * len(sequence)
        belongings_info = [set() for _ in range(len(sequence))]
        highlight_info = [[_, _] for _ in range(len(sequence))]
        
        type_result = splitSeqData.get(type, [])

        color_count = 1
        for entry_idx, entry in enumerate(type_result): # 第几段，段 entry
            start = entry['start'] # start is from 1, not 0
            end = entry['end']
            for _i in range(start, end + 1):
                i = _i - 1
                if _i >= start and _i < start + offset and _i <= end:
                    color_info[i] = color_count
                belongings_info[i].add(entry_idx)
                highlight_info[i][0] = min(highlight_info[i][0], start)
                highlight_info[i][1] = max(highlight_info[i][1], end)
            color_count += 1

        ddf['node'] = [i for i in sequence] # ATCG 等
        ddf['color'] = color_info # 0 没有颜色, > 0 不同颜色
        ddf['belongings'] = belongings_info # 出现在哪些段
        ddf['highlight_range'] = highlight_info # hightlight 范围

        ddf_list[type] = ddf.T

        return ddf_list
    
    split_seq_data = _get_splitSeqData(df)
    render_info = _get_render_info(split_seq_data, type=component_type)

    return split_seq_data, render_info
    

@api_view(['GET'])
def viewprimarystructureuorf(request):
    querydict = request.query_params.dict()
    taskid = querydict['taskid']
    subtask_name = querydict['protein_subtask_name']
    task_obj = mrna_task.objects.filter(id = taskid)[0]
    fpath = task_obj.output_result_path + subtask_name + '/'
    split_seq_data, render_info = util_primarystructure_type(fpath=fpath, component_type='uORF', offset=3)
    return Response({'splitSeqData': split_seq_data, 'render_info': render_info})

@api_view(['GET'])
def viewprimarystructureres(request):
    querydict = request.query_params.dict()
    taskid = querydict['taskid']
    subtask_name = querydict['protein_subtask_name']
    task_obj = mrna_task.objects.filter(id = taskid)[0]
    fpath = task_obj.output_result_path + subtask_name + '/'
    split_seq_data, render_info = util_primarystructure_type(fpath=fpath, component_type='IRES', offset=1)
    return Response({'splitSeqData': split_seq_data, 'render_info': render_info})

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
    url='https://mrnaapi.deepomics.org/analysis/files/'+fpath+'/'
    return Response({'type': 'pdb', 'fileurl': url})

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