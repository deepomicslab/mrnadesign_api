from django.shortcuts import render
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view

from mrnadesign_api import settings_local as local_settings
from utils import tools, task
from mrna_task.models import mrna_task
from mrna_task.serializers import mrna_taskSerializer
from antigen.models import antigen
from tantigen.models import tantigen
from utils import tools, task, slurm_api


import time
import os
import shutil
import random
import json
import traceback
import string

def generate_id():
    id = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return id

# Create your views here.
class lineardesignView(APIView):
    def post(self, request, *args, **kwargs):
        codonusage = request.data['codonusage']
        lambda_ = request.data['lambda']
        analysistype = request.data['analysistype']
        user_id = request.data['userid']
        inputtype = request.data['inputtype']
        is_demo_input = (request.data['rundemo'] == 'true')

        usertask = str(int(time.time()))+'_' + generate_id()
        path = local_settings.USER_PATH + usertask + '/input/' + 'sequence.fasta'
        os.makedirs(local_settings.USER_PATH + usertask, exist_ok=False)
        os.makedirs(local_settings.USER_PATH +
                    usertask + '/input', exist_ok=False)
        os.makedirs(local_settings.USER_PATH + usertask +
                    '/output/result', exist_ok=False)
        os.makedirs(local_settings.USER_PATH + usertask +
                    '/output/log', exist_ok=False)

        if inputtype == 'upload':
            submitfile = request.FILES['submitfile']
            path = local_settings.USER_PATH + usertask + '/input/' + submitfile.name
            _path = default_storage.save(path, ContentFile(submitfile.read()))
        elif inputtype == 'paste':
            with open(path, 'w') as file:
                file.write(request.data['file'])
        elif inputtype == 'enter':
            queryids = set(json.loads(request.data['queryids']))
            datatable = request.data['datatable']
            with open(path, 'w') as file:
                for idx, id in enumerate(queryids):
                    if datatable == 'antigen':
                        antigen_obj = antigen.objects.get(id=id)
                        file.write('>seq' + str(id) + '\n')
                        file.write(antigen_obj.sequence + '\n')
                    elif datatable == 'tantigen':
                        tantigen_obj = tantigen.objects.get(id=id)
                        file.write('>seq' + str(id) + '\n')
                        file.write(tantigen_obj.antigen_sequence + '\n')
        elif inputtype == 'rundemo':
            shutil.copy(local_settings.DEMO_ANALYSIS + 'demouser_lineardesign/input/sequence.fasta', path)

        with open(path, 'r') as file:
            # file format check
            is_upload = tools.is_fasta(file)
            if is_upload:
                tools.uploadphagefastapreprocess(path)

                # create task object
                newtask = mrna_task.objects.create(
                    user_id=user_id,
                    user_input_path={
                        'fasta': path,
                    },
                    is_demo_input=is_demo_input,
                    output_result_path=local_settings.USER_PATH + usertask + '/output/result/',
                    output_log_path=local_settings.USER_PATH + usertask + '/output/log/',
                    analysis_type=analysistype,
                    parameters={
                        'lambda': lambda_,
                        'codonusage': codonusage,
                    },
                    status='Created',
                    task_results=[],
                )

                # run task
                res = {
                    'task_id': newtask.id,
                    'user_id': newtask.user_id,
                    'analysis_type': newtask.analysis_type,
                }
                sbatch_dict = {
                    'user_input_path': newtask.user_input_path,
                    'parameters': {
                        'lambda': lambda_,
                        'codonusage': codonusage,
                    },
                    'output_result_path': newtask.output_result_path,
                    'output_log_path': newtask.output_log_path,
                }
                try:
                    taskdetail_dict = task.run_lineardesign(sbatch_dict)
                    res['status'] = 'Create Success'
                    res['message'] = 'Job create successfully'
                    newtask.job_id = taskdetail_dict['job_id']
                    newtask.status = taskdetail_dict['status']
                    newtask.status = 'Running'
                except Exception as e:
                    res['status'] = 'Create Failed'
                    res['message'] = 'Job create failed'
                    newtask.status = 'Failed'
                    traceback.print_exc()

                newtask.save()

            else:
                res = {
                    'status': 'Failed',
                    'message': 'Pipline create failed: The file you uploaded is not a fasta file',
                }
        return Response(res)

@api_view(['GET'])
def viewtask(request):
    userid = request.query_params.dict()['userid']
    taskslist = mrna_task.objects.filter(user_id=userid)
    serializer = mrna_taskSerializer(taskslist, many=True)
    return Response({'results': serializer.data})

@api_view(['GET'])
def viewtaskdetail(request):
    taskid = request.query_params.dict()['taskid']
    taskslist = mrna_task.objects.filter(id=taskid)
    serializer = mrna_taskSerializer(taskslist, many=True)
    return Response({'results': serializer.data[0]})

@api_view(['GET'])
def viewtasklog(request):
    taskid = request.query_params.dict()['taskid']
    task_obj = mrna_task.objects.get(id=taskid)

    sbatch_log = slurm_api.get_job_output(task_obj.output_log_path)
    sbatch_error = slurm_api.get_job_error(task_obj.output_log_path)
    if task_obj.analysis_type in ['Linear Design']:
        task_log = task.get_job_output(task_obj.output_log_path)
    return Response({
        'sbatch_log': sbatch_log,
        'sbatch_error': sbatch_error,
        'task_log': task_log,
    })

class lineardesigninputcheckView(APIView):
    def post(self, request, *args, **kwargs):
        
        res = {}
        datatable = request.data['datatable']
        _queryids = request.data['antigen_tantigen_ids']
        if _queryids[-1] == ';':
            _queryids = _queryids[:-1]
        queryids = []
        try:
            for i in _queryids.split(';'):
                queryids.append(int(i))
        except ValueError:
            res['idlist']=None
            res['message']='Please confirm your input IDs are integers, valid, and separated by semicolon'
            res['status']='failed'
            return Response(res)

        search_pids=[]
        if datatable == 'antigen':
            try:
                for id in queryids:
                    antigen_obj = antigen.objects.get(id=id)
                    search_pids.append(antigen_obj.id)
            except antigen.DoesNotExist:
                res['idlist']=None
                res['message']='The ID ' + str(id) + ' does not exist in the Table ' + datatable.upper() + '. Please check again.'
                res['status']='failed'
                return Response(res)
        elif datatable == 'tantigen':
            try:
                for id in queryids:
                    tantigen_obj = tantigen.objects.get(id=id)
                    search_pids.append(tantigen_obj.id)
            except tantigen.DoesNotExist:
                res['idlist']=None
                res['message']='The ID ' + str(id) + ' does not exist in the Table ' + datatable.upper() + '. Please check again.'
                res['status']='failed'
                return Response(res)
        
        res['idlist'] = search_pids
        res['message'] = None
        res['status'] = 'success'
        return Response(res)