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
import pandas as pd

def generate_id():
    id = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return id

# Create your views here.

class lineardesignView(APIView):
    def post(self, request, *args, **kwargs):
        parameters = json.loads(request.data['parameters'])
        codonusage = parameters['codonusage']
        lambda_ = parameters['lambda']
        analysistype = request.data['analysistype']
        user_id = request.data['userid']
        inputtype = request.data['inputtype']
        is_demo_input = (request.data['rundemo'] == 'true')
        lineardesignanalysistype = request.data['lineardesignanalysistype']

        usertask = str(int(time.time()))+'_' + generate_id()
        os.makedirs(local_settings.USER_PATH + usertask, exist_ok=False)
        os.makedirs(local_settings.USER_PATH +
                    usertask + '/input', exist_ok=False)
        os.makedirs(local_settings.USER_PATH + usertask +
                    '/output/result', exist_ok=False)
        os.makedirs(local_settings.USER_PATH + usertask +
                    '/output/log', exist_ok=False)

        utr3_path = local_settings.USER_PATH + usertask + '/input/' + 'utr3.fasta' 
        cds_path = local_settings.USER_PATH + usertask + '/input/' + 'sequence.fasta' 
        utr5_path = local_settings.USER_PATH + usertask + '/input/' + 'utr5.fasta' 

        if inputtype == 'upload':
            if lineardesignanalysistype == 'cds_only':
                submitfile1 = request.FILES['submitfile1']
                _path = default_storage.save(cds_path, ContentFile(submitfile1.read()))
            elif lineardesignanalysistype == 'cds_plus_35utr':
                submitfile1 = request.FILES['submitfile1']
                submitfile2 = request.FILES['submitfile2']
                submitfile3 = request.FILES['submitfile3']
                for f in [submitfile1, submitfile2, submitfile3]:
                    if f.name == 'cds.fasta' or f.name == 'cds.fa': _path = default_storage.save(cds_path, ContentFile(f.read()))
                    elif f.name == 'utr3.fasta' or f.name == 'utr3.fa': _path = default_storage.save(utr3_path, ContentFile(f.read()))
                    elif f.name == 'utr5.fasta' or f.name == 'utr5.fa': _path = default_storage.save(utr5_path, ContentFile(f.read()))
        
        elif inputtype == 'paste':
            seq_dict_list = json.loads(request.data['seq'])

            cds_seq_data = ''
            for idx, entry in enumerate(seq_dict_list):
                cds_seq_data += '>' + entry['name'] + '\n' + entry['cds'] + '\n'
            with open(cds_path, 'w') as file: file.write(cds_seq_data)

            if lineardesignanalysistype == 'cds_plus_35utr':
                utr3_seq_data = ''
                utr5_seq_data = ''
                for idx, entry in enumerate(seq_dict_list):
                    utr3_seq_data += '>' + entry['name'] + '\n' + entry['utr3'] + '\n'
                    utr5_seq_data += '>' + entry['name'] + '\n' + entry['utr5'] + '\n'
                with open(utr3_path, 'w') as file: file.write(utr3_seq_data)
                with open(utr5_path, 'w') as file: file.write(utr5_seq_data)

        elif inputtype == 'rundemo':
            if lineardesignanalysistype == 'cds_only':
                shutil.copy(local_settings.DEMO_ANALYSIS + 'demouser_lineardesign_cds_only/input/sequence.fasta', cds_path)
            elif lineardesignanalysistype == 'cds_plus_35utr':
                shutil.copy(local_settings.DEMO_ANALYSIS + 'demouser_lineardesign_cds_plus_35utr/input/utr3.fasta', utr3_path)
                shutil.copy(local_settings.DEMO_ANALYSIS + 'demouser_lineardesign_cds_plus_35utr/input/sequence.fasta', cds_path)
                shutil.copy(local_settings.DEMO_ANALYSIS + 'demouser_lineardesign_cds_plus_35utr/input/utr5.fasta', utr5_path)

        with open(cds_path, 'r') as file:
            # file format check
            is_upload = tools.is_fasta(file)
            if is_upload:
                tools.uploadphagefastapreprocess(cds_path)

                # create task object
                newtask = mrna_task.objects.create(
                    user_id=user_id,
                    user_input_path={
                        'utr3_path': utr3_path,
                        'fasta': cds_path,
                        'utr5_path': utr5_path,
                    },
                    is_demo_input=is_demo_input,
                    output_result_path=local_settings.USER_PATH + usertask + '/output/result/',
                    output_log_path=local_settings.USER_PATH + usertask + '/output/log/',
                    analysis_type=analysistype,
                    parameters={
                        # task parameter
                        'lineardesignanalysistype': lineardesignanalysistype,
                        # script parameter
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
                        'lineardesignanalysistype': lineardesignanalysistype,
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


class predictionView(APIView):
    def write_config(self, path, config_dict):
        import configparser
        file = open(path,"w")
        parser = configparser.ConfigParser()

        sections = config_dict.keys()
        for section in sections:
            parser.add_section(section)
        for section in sections:
            inner_dict = config_dict[section]
            fields = inner_dict.keys()
            for field in fields:
                value = inner_dict[field]
                parser.set(section, field, str(value))
        parser.write(file)
        file.close()

    def post(self, request, *args, **kwargs):    
        analysistype = request.data['analysistype']
        user_id = request.data['userid']
        inputtype = request.data['inputtype']
        is_demo_input = (request.data['rundemo'] == 'true')

        usertask = str(int(time.time()))+'_' + generate_id()
        task_dir = local_settings.USER_PATH + usertask + '/'
        os.makedirs(task_dir, exist_ok=False)
        os.makedirs(task_dir + 'sequences', exist_ok=False)
        os.makedirs(task_dir + 'log', exist_ok=False)
        
        seq_path = task_dir + 'sequences/input_seq.tsv'

        if inputtype == 'rundemo':
            shutil.copy(local_settings.DEMO_ANALYSIS + 'demouser_prediction_task0001/sequences/input_seq.tsv', seq_path)
            config_path = task_dir + 'task_prediction_config.ini'
            shutil.copy(local_settings.DEMO_ANALYSIS + 'demouser_prediction_task0001/task_prediction_config.ini', config_path)
        else:
            parameters = json.loads(request.data['parameters'])
            if inputtype == 'upload':
                # sequence
                submitfile = request.FILES['submitfile']
                # seq_path = task_dir + 'sequences/' + submitfile.name
                _seq_path = default_storage.save(seq_path, ContentFile(submitfile.read()))
                # config
                config_path = task_dir + 'task_prediction_config.ini'
                self.write_config(path = config_path, config_dict = parameters)
            elif inputtype == 'paste':
                # sequence
                seq_dict_list = json.loads(request.data['seq'])
                seq_data = []
                for idx, entry in enumerate(seq_dict_list):
                    seq_data.append([idx, entry['utr3'], entry['cds'], entry['utr5'], entry['name']])
                pd.DataFrame(seq_data, columns=['seq_id', '5utr', 'cds', '3utr', 'seq_acc']).to_csv(seq_path, sep='\t', index=False)
                # config
                config_path = task_dir + 'task_prediction_config.ini'
                self.write_config(path = config_path, config_dict = parameters)
            # elif inputtype == 'enter':
            #     queryids = set(json.loads(request.data['queryids']))
            #     datatable = request.data['datatable']
            #     with open(path, 'w') as file:
            #         for idx, id in enumerate(queryids):
            #             if datatable == 'antigen':
            #                 antigen_obj = antigen.objects.get(id=id)
            #                 file.write('>seq' + str(id) + '\n')
            #                 file.write(antigen_obj.sequence + '\n')
            #             elif datatable == 'tantigen':
            #                 tantigen_obj = tantigen.objects.get(id=id)
            #                 file.write('>seq' + str(id) + '\n')
            #                 file.write(tantigen_obj.antigen_sequence + '\n')


        # create task object
        newtask = mrna_task.objects.create(
            user_id=user_id,
            user_input_path={
                'sequence': seq_path,
                'config': config_path,
            },
            is_demo_input=is_demo_input,
            output_result_path=local_settings.USER_PATH + usertask + '/prediction_results/',
            output_log_path=local_settings.USER_PATH + usertask + '/log/',
            analysis_type=analysistype,
            parameters={},
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
            'task_dir': task_dir,
            'user_input_path': newtask.user_input_path,
            'output_log_path': newtask.output_log_path,
        }
        try:
            taskdetail_dict = task.run_prediction(sbatch_dict)
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

        return Response(res)

class safetyView(APIView):
    def post(self, request, *args, **kwargs):
        is_demo_input = (request.data['rundemo'] == 'true')
        analysistype = request.data['analysistype']
        user_id = request.data['userid']
        inputtype = request.data['inputtype']
        toxicity_model = request.data['toxicity_model']
        toxicity_threshold = request.data['toxicity_threshold']
        allergencity_model = request.data['allergencity_model']
        allergencity_threshold = request.data['allergencity_threshold']
        usertask = str(int(time.time())) + '_' + generate_id()
        path = local_settings.USER_PATH + usertask + '/input/' + 'sequence.fasta'
        os.makedirs(local_settings.USER_PATH + usertask, exist_ok=False)
        os.makedirs(local_settings.USER_PATH +
                    usertask + '/input', exist_ok=False)
        os.makedirs(local_settings.USER_PATH + usertask +
                    '/output/result', exist_ok=False)
        os.makedirs(local_settings.USER_PATH + usertask +
                    '/output/log', exist_ok=False)
        os.makedirs(local_settings.USER_PATH + usertask +
                    '/output/intermediate', exist_ok=False) # intermediate files

        if inputtype == 'upload':
            submitfile = request.FILES['submitfile']
            # path = local_settings.USER_PATH + usertask + '/input/' + submitfile.name
            _path = default_storage.save(path, ContentFile(submitfile.read()))
            with open(path, 'r') as fin:
                print(fin.readlines())
        elif inputtype == 'paste':
            with open(path, 'w') as file:
                file.write(request.data['file'])
        elif inputtype == 'rundemo':
            shutil.copy(local_settings.DEMO_ANALYSIS + 'demouser_safety/input/sequence.fasta', path)

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
                    # output_intermediate_path=local_settings.USER_PATH + usertask + '/output/intermediate/',
                    analysis_type=analysistype,
                    parameters={
                        'toxicity_model': '1' if toxicity_model == 'ML Model' else '2', # 'HybridModel'
                        'toxicity_threshold': toxicity_threshold,
                        'allergencity_model': '1' if allergencity_model == 'AAC based RF' else '2', # 'HybridModel'
                        'allergencity_threshold': allergencity_threshold,
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
                    'output_result_path': newtask.output_result_path,
                    'output_log_path': newtask.output_log_path,
                    'output_intermediate_path': local_settings.USER_PATH + usertask + '/output/intermediate/',
                    'parameters': {
                        'toxicity_model': newtask.parameters['toxicity_model'],
                        'toxicity_threshold': newtask.parameters['toxicity_threshold'],
                        'allergencity_model': newtask.parameters['allergencity_model'],
                        'allergencity_threshold': newtask.parameters['allergencity_threshold'],
                    },}
                try:
                    taskdetail_dict = task.run_safety(sbatch_dict)
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
                print('================== failed')
                res = {
                    'status': 'Failed',
                    'message': 'Pipline create failed: The file you uploaded is not a fasta file',
                }
        return Response(res)
    
class sequencealignView(APIView):
    def post(self, request, *args, **kwargs):
        is_demo_input = (request.data['rundemo'] == 'true')
        analysistype = request.data['analysistype']
        user_id = request.data['userid']
        inputtype = request.data['inputtype']
        window_size = request.data['window_size']
        step_size = request.data['step_size']
        evalue = request.data['evalue']
        usertask = str(int(time.time())) + '_' + generate_id()
        path = local_settings.USER_PATH + usertask + '/input/' + 'sequence.fasta'
        os.makedirs(local_settings.USER_PATH + usertask, exist_ok=False)
        os.makedirs(local_settings.USER_PATH +
                    usertask + '/input', exist_ok=False)
        os.makedirs(local_settings.USER_PATH + usertask +
                    '/output/result', exist_ok=False)
        os.makedirs(local_settings.USER_PATH + usertask +
                    '/output/log', exist_ok=False)
        os.makedirs(local_settings.USER_PATH + usertask +
                    '/output/intermediate', exist_ok=False) # intermediate files
        os.makedirs(local_settings.USER_PATH + usertask +
                    '/output/intermediate/blastdb', exist_ok=False)
        os.makedirs(local_settings.USER_PATH + usertask +
                    '/output/intermediate/temp', exist_ok=False)

        if inputtype == 'upload':
            submitfile = request.FILES['submitfile']
            # path = local_settings.USER_PATH + usertask + '/input/' + submitfile.name
            _path = default_storage.save(path, ContentFile(submitfile.read()))
            with open(path, 'r') as fin:
                print(fin.readlines())
        elif inputtype == 'paste':
            with open(path, 'w') as file:
                file.write(request.data['file'])
        elif inputtype == 'rundemo':
            shutil.copy(local_settings.DEMO_ANALYSIS + 'demouser_sequencealignment/input/sequence.fasta', path)

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
                    # output_intermediate_path=local_settings.USER_PATH + usertask + '/output/intermediate/',
                    analysis_type=analysistype,
                    parameters={
                        'window_size': window_size,
                        'step_size': step_size,
                        'evalue': evalue,
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
                    'output_result_path': newtask.output_result_path,
                    'output_log_path': newtask.output_log_path,
                    'output_intermediate_path': local_settings.USER_PATH + usertask + '/output/intermediate/',
                    'parameters': {
                        'window_size': newtask.parameters['window_size'],
                        'step_size': newtask.parameters['step_size'],
                        'evalue': newtask.parameters['evalue'],
                    },}
                try:
                    taskdetail_dict = task.run_sequence_align(sbatch_dict)
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
                print('================== failed')
                res = {
                    'status': 'Failed',
                    'message': 'Pipline create failed: The file you uploaded is not a fasta file',
                }
        return Response(res)
    
@api_view(['GET'])
def viewtask(request):
    userid = request.query_params.dict()['userid']
    taskslist = mrna_task.objects.filter(user_id=userid).order_by('-id')
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
    if task_obj.analysis_type in ['Linear Design', 'Prediction', 'Safety', 'Sequence Align']:
        task_log = task.get_job_output(task_obj.analysis_type, task_obj.output_log_path)
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