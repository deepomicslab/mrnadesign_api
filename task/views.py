import utils.modules as taskmodules
import pandas as pd
from rest_framework import viewsets
from task.models import tasks
from task.serializers import taskSerializer,taskSerializer2
from rest_framework.response import Response
from django.http import FileResponse
import csv
from django.http import JsonResponse
from rest_framework.decorators import api_view
from Phage_api import settings_local as local_settings
import os
from django.core.files.base import ContentFile
from rest_framework.response import Response
from rest_framework.views import APIView
from utils import tools, task
import time
import random
import os
import json
from django.core.files.storage import default_storage
import traceback
import shutil
from utils import slurm_api

class taskViewSet(viewsets.ModelViewSet):
    queryset = tasks.objects.order_by('id')
    serializer_class = taskSerializer


class piplineView(APIView):
    def post(self, request, *args, **kwargs):
        res = {}

        usertask = str(int(time.time()))+'_' + \
            str(random.randint(1000, 9999))
        uploadfilepath = local_settings.USERTASKPATH+'/' + \
            usertask + '/upload/'

        os.makedirs(uploadfilepath, exist_ok=False)
        if request.data['rundemo'] == 'true':
            if 'demopath' in request.data:
                shutil.copy(
                    local_settings.DEMOFILE+request.data['demopath'], uploadfilepath+'sequence.fasta')
            else:
                shutil.copy(
                    local_settings.DEMOFILE+"sequence.fasta", uploadfilepath+'sequence.fasta')
            path = uploadfilepath+'sequence.fasta'
        else:
            if request.data['inputtype'] == 'upload':
                file = request.FILES['submitfile']
                path = default_storage.save(
                    uploadfilepath+'sequence.fasta', ContentFile(file.read()))
                
            elif request.data['inputtype'] == 'paste':
                path = uploadfilepath+'sequence.fasta'
                with open(path, 'w') as file:
                    file.write(request.data['file'])
            else:
                phageids = json.loads(request.data['phageid'])
                path = uploadfilepath+'sequence.fasta'
                tools.searchphagefasta(phageids, path)

        with open(path, 'r') as file:
            # file format check
            is_upload = tools.is_fasta(file)
            if is_upload:
                tools.uploadphagefastapreprocess(path)

                name = request.data['analysistype'] + \
                    " " + str(tasks.objects.last().id+1)
                modulejson = json.loads(request.data['modulelist'])
                modulelist = []
                for key, value in modulejson.items():
                    if value:
                        modulelist.append(key)
                if 'alignment' in modulelist:
                    tools.fixIdLong(path)
                # create task object
                newtask = tasks.objects.create(
                    name=name, user=request.data['userid'], uploadpath=usertask,
                    analysis_type=request.data['analysistype'], modulelist=modulelist, status='Created')
                userpath = local_settings.ABSUSERTASKPATH+'/' + usertask
                infodict = {'taskid': newtask.id, 'userpath': userpath, 'modulelist': modulelist,
                            'analysis_type': request.data['analysistype'], 'userid': request.data['userid']}
                taskdetail_dict = task.init_taskdetail_dict(
                    infodict)
                newtask.task_detail = json.dumps(taskdetail_dict)
                # run task
                try:
                    taskdetail_dict = task.run_annotation_pipline(
                        taskdetail_dict)
                    res['status'] = 'Success'
                    res['message'] = 'Pipline create successfully'
                    res['data'] = {'taskid': newtask.id}
                    newtask.task_detail = json.dumps(taskdetail_dict)
                    newtask.status = 'Running'
                    pass
                except Exception as e:
                    res['status'] = 'Failed'
                    res['message'] = 'Pipline create failed'
                    newtask.status = 'Failed'
                    traceback.print_exc()

                newtask.save()

            else:
                res['status'] = 'Failed'
                res['message'] = 'Pipline create failed: The file you uploaded is not a fasta file'
        return Response(res)



#this pipline include cluster,comparison,tree
class clusterpiplineView(APIView):
    def post(self, request, *args, **kwargs):
        res = {}
        usertask = str(int(time.time()))+'_' + \
            str(random.randint(1000, 9999))
        uploadfilepath = local_settings.USERTASKPATH+'/' + \
            usertask + '/upload/'
        os.makedirs(uploadfilepath, exist_ok=False)
        neednum=int(request.data['neednum'])
        if request.data['rundemo'] == 'true':
            ##!!!need to use settings_local config
            shutil.copy(
                local_settings.DEMOFILE+"cluster_demo.fasta", uploadfilepath+'sequence.fasta')
            path = uploadfilepath+'sequence.fasta'
        else:
            if request.data['inputtype'] == 'upload':
                file = request.FILES['submitfile']
                path = default_storage.save(
                    uploadfilepath+'sequence.fasta', ContentFile(file.read()))
                
            #request.data['inputtype'] == 'paste'
            else :
                path = uploadfilepath+'sequence.fasta'
                with open(path, 'w') as file:
                    file.write(request.data['file'])
                

        with open(path, 'r') as file:
            # file format check
            is_upload = tools.is_fasta(path)
            if is_upload:
                if tools.sequence_count(path) >= neednum:
                    tools.uploadphagefastapreprocess(path)
                    name = request.data['analysistype'] + \
                        " " + str(tasks.objects.last().id+1)
                    modulejson = json.loads(request.data['modulelist'])
                    modulelist = []
                    for key, value in modulejson.items():
                        if value:
                            modulelist.append(key)
            
                    # create task object
                    newtask = tasks.objects.create(
                        name=name, user=request.data['userid'], uploadpath=usertask,
                        analysis_type=request.data['analysistype'], modulelist=modulelist, status='Created')
                    userpath = local_settings.ABSUSERTASKPATH+'/' + usertask
                    infodict = {'taskid': newtask.id, 'userpath': userpath, 'modulelist': modulelist,
                                'analysis_type': request.data['analysistype'], 'userid': request.data['userid']}
                    
                    taskdetail_dict = task.init_taskdetail_dict(
                        infodict)
                    
                    newtask.task_detail = json.dumps(taskdetail_dict)
                    # run task
                    try:
                        taskdetail_dict = task.run_cluster_pipline(
                            taskdetail_dict)
                        res['status'] = 'Success'
                        res['message'] = 'Pipline create successfully'
                        res['data'] = {'taskid': newtask.id}
                        print(taskdetail_dict)
                        newtask.task_detail = json.dumps(taskdetail_dict)
                        newtask.status = 'Running'
                        pass
                    except Exception as e:
                        res['status'] = 'Failed'
                        res['message'] = 'Pipline create failed'
                        newtask.status = 'Failed'
                        traceback.print_exc()
                    newtask.save()
                else:
                    res['status'] = 'Failed'
                    res['message'] = 'The number of file sequences you uploaded is less than '+str(neednum)

            else:
                res['status'] = 'Failed'
                res['message'] = 'Pipline create failed: The file you uploaded is not a fasta file'
        return Response(res)


@api_view(['GET'])
def viewtask(request):
    userid = request.query_params.dict()['userid']
    taskslist = tasks.objects.filter(user=userid)
    serializer = taskSerializer(taskslist, many=True)
    return Response({'results': serializer.data})


@api_view(['GET'])
def viewtaskdetail(request):
    # userid = request.query_params.dict()['userid']
    taskid = request.query_params.dict()['taskid']
    # taskslist = tasks.objects.filter(user=userid, id=taskid)
    taskslist = tasks.objects.filter(id=taskid)
    serializer = taskSerializer2(taskslist, many=True)
    return Response({'results': serializer.data[0]})

@api_view(['GET'])
def viewtasklog(request):
    # userid = request.query_params.dict()['userid']
    taskid = request.query_params.dict()['taskid']
    moudlename = request.query_params.dict()['moudlename']
    task_object = tasks.objects.get(id=taskid)
    task_detail=json.loads(task_object.task_detail)
    job_id=None
    for module in  task_detail['task_que']:
        if module['module']==moudlename:
            job_id=module['job_id']
            break
    task_log='no log'
    task_error='no log'
    if job_id != None:
        task_log=slurm_api.get_job_output(job_id)
        task_error=slurm_api.get_job_error(job_id)
    return Response({'task_log': task_log,'task_error':task_error})

@api_view(['GET'])
def viewphage(request):
    taskid = request.query_params.dict()['taskid']
    task = tasks.objects.get(id=taskid)
    path = local_settings.USERTASKPATH+'/' + \
        task.uploadpath+'/output/result/phage.tsv'

    phagelist = []
    with open(path, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        for id, row in enumerate(reader):
            dictr = dict(row)
            dictr['id'] = id+1
            phagelist.append(dictr)
    return Response({'results': phagelist})


@api_view(['GET'])
def viewphagedetail(request):
    taskid = request.query_params.dict()['taskid']
    phageid = request.query_params.dict()['phageid']
    task = tasks.objects.get(id=taskid)
    path = local_settings.USERTASKPATH+'/' + \
        task.uploadpath+'/output/result/phage.tsv'
    phages = pd.read_csv(path, sep='\t', index_col=False)
    phage = phages[phages['Acession_ID'] == phageid].to_dict(orient='records')
    return Response({'results': phage[0]})


@api_view(['GET'])
def viewprotein(request):
    params_dict=request.query_params.dict()
    taskid = request.query_params.dict()['taskid']
    task = tasks.objects.get(id=taskid)
    path = local_settings.USERTASKPATH+'/' + \
            task.uploadpath+'/output/result/protein.tsv'
    if 'phageid' in params_dict:
        phageid = request.query_params.dict()['phageid']
        proteins = pd.read_csv(path, sep='\t', index_col=False)
        proteindict = proteins[proteins['phageid']
                            == phageid].to_dict(orient='records')
        return Response({'results': proteindict})
    else:
        proteins = pd.read_csv(path, sep='\t', index_col=False)
        #for heatmap
        proteindict =  proteins[['Protein_id', 'phageid','Protein_function_classification']].to_dict(orient='records')
        return Response({'results': proteindict})

@api_view(['GET'])
def viewphageterminators(request):
    taskid = request.query_params.dict()['taskid']
    phageid = request.query_params.dict()['phageid']
    task = tasks.objects.get(id=taskid)
    #workspace/user_task/1690380527_6812/output/rawdata/terminator
    path = local_settings.USERTASKPATH+'/' + \
        task.uploadpath+'/output/rawdata/terminator/transterm_output.txt'
    terminators = pd.read_csv(path, sep='\t', index_col=False,names=['Phage_id','Terminator_Id','Start','Stop','Sense','Loc','Confidence']).astype(str)
    terminatorsdict = terminators[terminators['Phage_id']
                        == phageid].to_dict(orient='records')
    return Response({'results': terminatorsdict})

@api_view(['GET'])
def viewphagetrnas(request):
    taskid = request.query_params.dict()['taskid']
    phageid = request.query_params.dict()['phageid']
    task = tasks.objects.get(id=taskid)
    path = local_settings.USERTASKPATH+'/' + \
        task.uploadpath+'/output/result/trna.tsv'
    trnas = pd.read_csv(path, sep='\t', index_col=False).astype(str)
    trnasdict = trnas[trnas['phage_accid']
                        == phageid].to_dict(orient='records')
    return Response({'results': trnasdict})


@api_view(['GET'])
def viewphagecrisprs(request):
    taskid = request.query_params.dict()['taskid']
    phageid = request.query_params.dict()['phageid']
    task = tasks.objects.get(id=taskid)
    path = local_settings.USERTASKPATH+'/' + \
        task.uploadpath+'/output/rawdata/crispr/output/TSV/Crisprs_REPORT.tsv'
    crisprs = pd.read_csv(path, sep='\t', index_col=False).astype(str)
    crisprs = crisprs[crisprs['Sequence']
                        == phageid]
    crisprs.rename(columns={'Sequence': 'Phage_id'}, inplace=True)
    crisprs.rename(columns={'Potential_Orientation (AT%)': 'Potential_Orientation_AT'}, inplace=True)
    crisprsdict=crisprs.to_dict(orient='records')
    return Response({'results': crisprsdict})

@api_view(['GET'])
def viewphagearvgs(request):
    taskid = request.query_params.dict()['taskid']
    phageid = request.query_params.dict()['phageid']
    task = tasks.objects.get(id=taskid)
    def split_and_join(protein_id):
        return '_'.join(protein_id.split('_')[:-1])
    taskpath = local_settings.USERTASKPATH+'/' + task.uploadpath
    arvg_argpath = taskpath+'/output/rawdata/arvf/antimicrobial_resistance_gene_result/antimicrobial_resistance_gene_results.tsv'
    arvg_arg = pd.read_csv(arvg_argpath, sep='\t', index_col=False,names=[
                        'Protein_id', 'Aligned_Protein_in_CARD']).astype(str)
    arvg_arg['Phage_id'] = arvg_arg['Protein_id'].apply(split_and_join)
    arvg_vfrpath = taskpath+'/output/rawdata/arvf/virulence_factor_result/virulent_factor_results.tsv'
    arvg_vfr = pd.read_csv(arvg_vfrpath, sep='\t', index_col=False,names=[
                        'Protein_id', 'Aligned_Protein_in_VFDB']).astype(str)
    arvg_vfr['Phage_id'] = arvg_vfr['Protein_id'].apply(split_and_join)
    arvg_vfr = arvg_vfr[arvg_vfr['Phage_id']== phageid]
    arvg_arg = arvg_arg[arvg_arg['Phage_id']== phageid]
    arvg_arg = arvg_arg.reset_index().rename(columns={'index':'id'})
    arvg_vfr = arvg_vfr.reset_index().rename(columns={'index':'id'})

    arvg_vfr = arvg_vfr.to_dict(orient='records')
    arvg_arg = arvg_arg.to_dict(orient='records')
    return Response({'results': {'ar':arvg_arg,'vf':arvg_vfr}})

@api_view(['GET'])
def viewphagetransmembranes(request):
    taskid = request.query_params.dict()['taskid']
    phageid = request.query_params.dict()['phageid']
    task = tasks.objects.get(id=taskid)
    transmembranepath = local_settings.USERTASKPATH+'/' + \
        task.uploadpath+'/output/result/transmembrane.tsv'
    transmembranes = pd.read_csv(transmembranepath, sep='\t', index_col=False).astype(
        str)
    transmembranes = transmembranes[transmembranes['Phage_Acession_ID']
                        == phageid]
    transmembranes = transmembranes.reset_index().rename(columns={'index':'id'})
    result = transmembranes.to_dict(orient='records')
    return Response({'results': result})

@api_view(['GET'])
def viewphageanticrisprs(request):
    taskid = request.query_params.dict()['taskid']
    phageid = request.query_params.dict()['phageid']
    task = tasks.objects.get(id=taskid)
    anticrisprpath = local_settings.USERTASKPATH+'/' + \
        task.uploadpath+'/output/result/anticrispr.tsv'
    anticrisprs = pd.read_csv(anticrisprpath, sep='\t',
                            index_col=False).astype(str)
    anticrisprs = anticrisprs[anticrisprs['phageid']
                        == phageid]
    anticrisprs.rename(columns={'phageid': 'Phage_Acession_ID'}, inplace=True)
    anticrisprs.rename(columns={'antiresource': 'Source'}, inplace=True)
    result = anticrisprs.to_dict(orient='records')
    return Response({'results': result})

@api_view(['GET'])
def viewheatmap(request):
    taskid = request.query_params.dict()['taskid']
    task = tasks.objects.get(id=taskid)
    path = local_settings.USERTASKPATH+'/' + \
        task.uploadpath+'/output/result/phage.tsv'
    file = open(path, 'rb')
    response = FileResponse(file)
    response['Content-Disposition'] = 'attachment; filename="phage.tsv"'
    response['Content-Type'] = 'text/plain'
    return response


@api_view(['GET'])
def phagefasta(request):
    taskid = request.query_params.dict()['taskid']
    phageid = request.query_params.dict()['phageid']
    task = tasks.objects.get(id=taskid)
    path = local_settings.USERTASKPATH+'/' + \
        task.uploadpath+'/output/result/' + phageid + '/sequence.fasta'
    file = open(path, 'rb')
    response = FileResponse(file)
    response['Content-Disposition'] = 'attachment; filename="sequence.fasta"'
    response['Content-Type'] = 'text/plain'
    return response


@api_view(['GET'])
def viewmodulesdetail(request):
    taskid = request.query_params.dict()['taskid']
    phageid = request.query_params.dict()['phageid']
    task = tasks.objects.get(id=taskid)
    path = local_settings.USERTASKPATH+'/' + \
        task.uploadpath
    modulelist = eval(task.modulelist)
    results = {}
    for module in modulelist:
        if module == 'quality':
            results['quality'] = taskmodules.qualitydetail(path, phageid)
        elif module == 'host':
            results['host'] = taskmodules.hostdetail(path, phageid)
        elif module == 'trna':
            results['trna'] = taskmodules.trnadetail(path, phageid)
        elif module == 'anticrispr':
            results['anticrispr'] = taskmodules.phageanticrisprdetail(path, phageid)
        elif module == 'crisprcas':
            results['crisprcas'] = taskmodules.crisprcasdetail(path, phageid)
        elif module == 'transmembrane':
            results['transmembrane'] = taskmodules.transmembranedetail(
                path, phageid)
    return Response({'results': results})


@api_view(['GET'])
def viewmodules(request):
    taskid = request.query_params.dict()['taskid']
    module = request.query_params.dict()['module']
    task = tasks.objects.get(id=taskid)
    path = local_settings.USERTASKPATH+'/' + \
        task.uploadpath

    if module == 'lifestyle':
        results = taskmodules.lifestyle(path)
    elif module == 'host':
        results = taskmodules.host(path)
    elif module == 'transmembrane':
        results = taskmodules.transmembrane(path)
    elif module == 'cluster':
        results = taskmodules.cluster(path)
    elif module == 'trna':
        results = taskmodules.trna(path)
    elif module == 'alignment':
        if 'phageids' in request.query_params.dict() :
            phageids=request.query_params.dict()['phageids'].split(', ')
        else:
            phageids=None
        if 'clusterid' in  request.query_params.dict() :
            cid=request.query_params.dict()['clusterid']
            results = taskmodules.alignmentdetail(
                path,cid,pids=phageids)
        elif 'subclusterid' in request.query_params.dict() :
            cid=request.query_params.dict()['subclusterid']
            results = taskmodules.alignmentdetail(
                path,cid,pids=phageids)
        else:
            results = taskmodules.alignmentdetail(
                    path,pids=phageids)
    elif module == 'terminator':
        results = taskmodules.terminatordetail(
                path)
    elif module == 'taxonomic':
        results = taskmodules.taxonomicdetail(path)
    elif module == 'crispr':
        results = taskmodules.crisprdetail(path)
    elif module == 'arvf':
        results = taskmodules.arvgdetail(path)
    elif module == 'anticrispr':
        results = taskmodules.anticrisprdetail(path)
    else:
        results = []
    return Response({'results': results})


@api_view(['GET'])
def viewquality(request):
    taskid = request.query_params.dict()['taskid']
    task = tasks.objects.get(id=taskid)
    path = local_settings.USERTASKPATH+'/' + \
        task.uploadpath+'/output/rawdata/quality/'
    checkv_result = pd.read_csv(
        path+'checkv_result.txt', sep='\t', index_col=False, header=None, names=[
            'phageid', 'Completeness', 'Taxonomy']).astype(str)
    completeness = pd.read_csv(
        path+'completeness.tsv', sep='\t', index_col=False).astype(str)
    quality_summary = pd.read_csv(
        path+'quality_summary.tsv', sep='\t', index_col=False).astype(str)
    return Response({'results': {'checkv_result': checkv_result.to_dict(orient='records'), 'completeness': completeness.to_dict(orient='records'), 'quality_summary': quality_summary.to_dict(orient='records')}})


@api_view(['GET'])
def getoutputfile(request, path):
    file_path = local_settings.USERTASKPATH + '/' + path
    file = open(file_path, 'rb')
    response = FileResponse(file)
    filename = file.name.split('/')[-1]
    response['Content-Disposition'] = "attachment; filename="+filename
    response['Content-Type'] = 'text/plain'
    return response



#home/platform/phage_db/phage_api/workspace/user_task/1690114330_5263/output/rawdata/tree/cluster_1/sequence.phy
@api_view(['GET'])
def viewtree(request):
    query_params = request.query_params.dict()
    taskid = query_params['taskid']
    task = tasks.objects.get(id=taskid)
    if 'clsuter_id' in query_params:
        clsuter_id = request.query_params.dict()['clsuter_id']
        file_path =local_settings.USERTASKPATH+'/' + \
            task.uploadpath+'/output/rawdata/tree/'+clsuter_id+'/sequence.phy'
    else:
        file_path = local_settings.USERTASKPATH+'/' + \
            task.uploadpath+'/output/rawdata/tree/sequence.phy'

    if os.path.exists(file_path):
        file = open(file_path, 'rb')
        return Response( file.read().decode('utf-8'))
    else:
        return Response('')