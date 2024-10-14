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
        # print('-----------------------------------request.data', request.data)
        codonusage = request.data['codonusage']
        lambda_ = request.data['lambda']
        analysistype = request.data['analysistype']
        user_id = request.data['userid']
        inputtype = request.data['inputtype']
        is_demo_input = (request.data['rundemo'] == 'true')

        usertask = str(int(time.time()))+'_' + generate_id()
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
        elif request.data['inputtype'] == 'paste':
            path =local_settings.USER_PATH + usertask + '/input/' + 'sequence.fasta'
            with open(path, 'w') as file:
                file.write(request.data['file'])

        # if request.data['rundemo'] == 'true':
        #     if 'demopath' in request.data:
        #         shutil.copy(
        #             local_settings.DEMOFILE+request.data['demopath'], uploadfilepath+'sequence.fasta')
        #     else:
        #         shutil.copy(
        #             local_settings.DEMOFILE+"sequence.fasta", uploadfilepath+'sequence.fasta')
        #     path = uploadfilepath+'sequence.fasta'
        # else:
        #     if request.data['inputtype'] == 'upload':
        #         file = request.FILES['submitfile']
        #         path = default_storage.save(
        #             uploadfilepath+'sequence.fasta', ContentFile(file.read()))
                
        #     elif request.data['inputtype'] == 'paste':
        #         path = uploadfilepath+'sequence.fasta'
        #         with open(path, 'w') as file:
        #             file.write(request.data['file'])
        #     else:
        #         phageids = json.loads(request.data['phageid'])
        #         path = uploadfilepath+'sequence.fasta'
        #         tools.searchphagefasta(phageids, path)

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