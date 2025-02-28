from django.shortcuts import render
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db.models import F, Value, TextField, CharField
from django.db.models.functions import Replace
from django.contrib.postgres.search import TrigramSimilarity

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view

from mrnadesign_api import settings_local as local_settings
from utils import tools, task
from mrna_task.models import mrna_task
from mrna_task.serializers import mrna_taskSerializer
from antigen.models import antigen
from tantigen.models import tantigen
from three_utr.models import three_utr
from tsnadb.models import tsnadb_neoantigen, tsnadb_validated
from mirtarbase_db.models import mirtarbase_db
from rebase_db.models import rebase_data, rebase_enzyme_link
from protein_score.models import protein_score
from utils import tools, task, slurm_api

import time
import os
import shutil
import random
import json
import traceback
import string
import pandas as pd
import numpy as np
import time

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
            subtasks=[],
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

            'task_id': newtask.id,
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
    
class antigenscreeningView(APIView):
    def post(self, request, *args, **kwargs):
        is_demo_input = (request.data['rundemo'] == 'true')
        analysistype = request.data['analysistype']
        user_id = request.data['userid']
        inputtype = request.data['inputtype']
        peptide_len_range = [int(i) for i in request.data['peptide_len_range'].split(',')]
        
        usertask = str(int(time.time())) + '_' + generate_id()
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
                    analysis_type=analysistype,
                    parameters={
                        'peptide_len_min': peptide_len_range[0],
                        'peptide_len_max': peptide_len_range[1],
                    },
                    status='Created',
                    subtasks=[],
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
                    'parameters': {
                        'peptide_len_min': peptide_len_range[0],
                        'peptide_len_max': peptide_len_range[1],
                    },}
                try:
                    taskdetail_dict = task.run_antigen_screening(sbatch_dict)
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
    
def apply_similarity(table_dict, to_compare):
    all_objects = []

    for table in table_dict.keys():
        try:
            model_class = globals()[table]
        except KeyError:
            print(f"Model {table} not found in globals()")
            continue

        for field in table_dict[table]:
            qs = model_class.objects.values('id', field).annotate(
                seq=Replace(F(field), Value('\n'), Value(''), output_field=TextField()),
                src_id=F('id'),
                src_table=Value(table, output_field=CharField()),
                src_field=Value(field, output_field=CharField()),
                similarity=TrigramSimilarity('seq', to_compare)
            ).values('src_id', 'src_table', 'src_field', 'seq', 'similarity').order_by('-similarity').iterator(chunk_size=1000)

            all_objects.extend({
                'src_id': obj['src_id'],
                'src_table': obj['src_table'],
                'src_field': obj['src_field'],
                'seq': obj['seq'],
                'similarity': obj['similarity'],
            } for idx, obj in enumerate(qs) if idx < 100)

    # sorted_objects = sorted(all_objects, key=lambda obj: obj['similarity'], reverse=True)[:10]
    sorted_objects = all_objects[:10]

    import random
    L = list(range(len(sorted_objects)))
    random.shuffle(L)
    for i in L:
        temp_obj = protein_score.objects.get(id = i + 1)
        sorted_objects[i]['overall_gc'] = temp_obj.overall_gc
        sorted_objects[i]['codon_usage_efficiency_index'] = temp_obj.codon_usage_efficiency_index
        sorted_objects[i]['tis'] = temp_obj.tis
        sorted_objects[i]['rna_interference'] = temp_obj.rna_interference
        sorted_objects[i]['rna_structure'] = temp_obj.rna_structure
        sorted_objects[i]['ires_number'] = temp_obj.ires_number
        sorted_objects[i]['degscore'] = temp_obj.degscore
    return sorted_objects  

@api_view(['GET'])
def strSimilarityView(request):   
    querydict = request.query_params.dict()
    subtask_name = querydict['score_subtask_name']
    taskid = querydict['taskid']
    task_obj = mrna_task.objects.filter(id = taskid)[0]
    fpath = task_obj.output_result_path + subtask_name + '/cds_protein.fasta'
    with open(fpath, 'r') as f: _this_protein = f.readlines()[1:]
    this_protein = ''
    for i in _this_protein: this_protein += i.replace('\n', '')

    protein_table_dict = {
        'antigen': ['sequence'],
        'tantigen': ['antigen_sequence'],
        'tsnadb_neoantigen': ['peptide'],
        'tsnadb_validated': ['mutant_peptide'],
    }
    # rna_table_dict = {
    #     'tantigen': ['seq_5', 'cds', 'seq_3'],
    #     'three_utr': ['pattern'],
    #     'mirtarbase_db': ['target_site'],
    #     'rebase_data': ['recognition_site'],
    # }    

    results = apply_similarity(protein_table_dict, this_protein)
    
    merged_df = pd.DataFrame(results)
    merged_df.to_csv(task_obj.output_result_path + subtask_name + '/recommendation.csv')

    return Response({'results': merged_df.to_dict(orient='records')})

@api_view(['GET'])
def getStrSimilarityView(request):   
    querydict = request.query_params.dict()
    subtask_name = querydict['score_subtask_name']
    taskid = querydict['taskid']
    task_obj = mrna_task.objects.filter(id = taskid)[0]
    fpath = task_obj.output_result_path + subtask_name + '/recommendation.csv'
    merged_df = pd.read_csv(fpath)

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

    return Response({'results': merged_df.to_dict(orient='records')})

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
    if task_obj.analysis_type in ['Linear Design', 'Prediction', 'Safety', 'Sequence Align', 'Antigen Screening']:
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