from mrnadesign_api import settings_local as local_settings
from utils import slurm_api
import json
import subprocess
import re
import glob
import os
import pandas as pd

def check_lineardesign_result_v1(output_result_path):
    with open(output_result_path+'result.txt') as f: 
        L = f.read()
    if 'mRNA sequence' not in L: 
        print('Linear Design Failed')
        return False
    with open(output_result_path+'3utr_rnafold.output') as f: 
        L = f.read()
    if len(L) == 0: 
        print('Linear Design Failed')
        return False
    with open(output_result_path+'5utr_rnafold.output') as f: 
        L = f.read()
    if len(L) == 0: 
        print('Linear Design Failed')
        return False
    return True

def check_lineardesign_result_v2(output_result_path):
    with open(output_result_path+'result.txt') as f: 
        L = f.read()
    if 'mRNA sequence' not in L: 
        print('Linear Design Failed')
        return False
    return True

def check_prediction_result(output_result_path):
    if os.path.exists(output_result_path):
        return True
    return False

def check_safety_result(output_result_path):
    if not os.path.exists(output_result_path + 'merged_file.csv'):
        return False
    if pd.read_csv(output_result_path + 'merged_file.csv').shape[0] <= 0:
        return False
    return True

def check_sequencealign_result(output_result_path):
    if not os.path.exists(output_result_path + 'result.json'):
        return False
    return True

def check_antigenscreening_result(output_result_path):
    if not os.path.exists(output_result_path + 'result.csv'): 
        return False
    return True

def check_tsa_result(output_log_path):
    if not os.path.exists(output_log_path + 'sbatch.out'): 
        return False
    with open(output_log_path + 'sbatch.out') as f:
        L = f.read()
    if 'All done.' in L: 
        return True
    return False

def check_tcranno_result(output_result_path):
    if not os.path.exists(output_result_path + 'result.txt'): 
        return False
    with open(output_result_path + 'result.txt') as f:
        L = f.read()
    if 'All done.' in L: 
        return True
    return False

def get_job_output(analysis_type, output_log_path):
    if analysis_type == 'Linear Design':
        path = output_log_path + 'lineardesign.log'
        try:
            with open(path, 'r') as f:
                output = f.read()
                if output == '':
                    output = 'no linear design log'
                return output
        except:
            return 'no linear design log'
    elif analysis_type == 'Prediction':
        path = output_log_path + 'prediction.log'
        try:
            with open(path, 'r') as f:
                output = f.read()
                if output == '':
                    output = 'no prediction log'
                return output
        except:
            return 'no prediction log'
    elif analysis_type == 'Safety':
        path = output_log_path + 'safety.log'
        try:
            with open(path, 'r') as f:
                output = f.read()
                if output == '':
                    output = 'no safety log'
                return output
        except:
            return 'no safety log'
    elif analysis_type == 'Sequence Align':
        path = output_log_path + 'sequencealign.log'
        try:
            with open(path, 'r') as f:
                output = f.read()
                if output == '':
                    output = 'no sequence align log'
                return output
        except:
            return 'no sequence align log'
    elif analysis_type == 'Antigen Screening':
        path = output_log_path + 'antigenscreening.log'
        try:            
            with open(path, 'r') as f:
                output = f.read()
                if output == '':
                    output = 'no antigen screening log'
                return output
        except:
            return 'no antigen screening log'
    elif analysis_type == 'TSA':
        path = output_log_path + 'tsa.log'
        try:            
            with open(path, 'r') as f:
                output = f.read()
                if output == '':
                    output = 'no tsa log'
                return output
        except:
            return 'no tsa log'
    elif analysis_type == 'TCRanno':
        path = output_log_path + 'tcranno.log'
        try:
            with open(path, 'r') as f:
                output = f.read()
                if output == '':
                    output = 'no tcranno log'
                return output
        except:
            return 'no tcranno log'
    
def run_lineardesign(sbatch_dict):
    user_input_path = sbatch_dict['user_input_path']
    parameters = sbatch_dict['parameters']
    output_result_path = sbatch_dict['output_result_path']
    output_log_path = sbatch_dict['output_log_path']

    if parameters['lineardesignanalysistype'] == 'cds_plus_35utr':
        sbatch_command = (
            'sbatch' +
            ' --output=' + output_log_path + 'sbatch.out' +
            ' --error=' + output_log_path + 'sbatch.err' +
            ' ' + local_settings.SCRIPTS + 'run_lineardesign_cds_plus_35utr.sh' +
            ' -a ' + user_input_path['fasta'] +
            ' -b ' + str(parameters['lambda']) + 
            ' -c ' + parameters['codonusage'] + 
            ' -d ' + output_result_path +
            ' -e ' + output_log_path + 'lineardesign.log' +
            ' -f ' + user_input_path['utr3_path'] + 
            ' -g ' + user_input_path['utr5_path'] 
        )
    elif parameters['lineardesignanalysistype'] == 'cds_only':
        sbatch_command = (
            'sbatch' +
            ' --output=' + output_log_path + 'sbatch.out' +
            ' --error=' + output_log_path + 'sbatch.err' +
            ' ' + local_settings.SCRIPTS + 'run_lineardesign_cds_only.sh' +
            ' -a ' + user_input_path['fasta'] +
            ' -b ' + str(parameters['lambda']) + 
            ' -c ' + parameters['codonusage'] + 
            ' -d ' + output_result_path +
            ' -e ' + output_log_path + 'lineardesign.log'
        )
    print('sbatch_command', sbatch_command)
    sbatch_output = subprocess.check_output(sbatch_command, shell=True).decode("utf-8")  # Submitted batch job 1410435
    job_id = re.search(r"Submitted batch job (\d+)", sbatch_output).group(1)  # 1410435
    status = slurm_api.get_job_status(job_id)  # PENDING
    taskdetail_dict = {
        'job_id': job_id,
        'status': status,
    }
    return taskdetail_dict

def run_prediction(sbatch_dict):
    task_dir = sbatch_dict['task_dir']
    user_input_path = sbatch_dict['user_input_path']
    output_log_path = sbatch_dict['output_log_path']
    task_id = sbatch_dict['task_id']

    subtask_names = list(pd.read_csv(user_input_path['sequence'], '\t')['seq_acc'])

    sbatch_command = (
        'sbatch' +
        ' --output=' + output_log_path + 'sbatch.out' +
        ' --error=' + output_log_path + 'sbatch.err' +
        ' ' + local_settings.SCRIPTS + 'run_prediction.sh' +
        ' -a ' + task_dir +
        ' -b ' + user_input_path['config'] + 
        ' -c ' + output_log_path + 'prediction.log' + 

        ' -d ' + str(task_id) + 
        ' -e ' + '\"' + '|'.join(subtask_names) + '\"'
    )
    print('sbatch_command', sbatch_command)
    sbatch_output = subprocess.check_output(sbatch_command, shell=True).decode("utf-8")  # Submitted batch job 1410435
    job_id = re.search(r"Submitted batch job (\d+)", sbatch_output).group(1)  # 1410435
    status = slurm_api.get_job_status(job_id)  # PENDING
    taskdetail_dict = {
        'job_id': job_id,
        'status': status,
    }
    return taskdetail_dict

def run_safety(sbatch_dict):
    user_input_path = sbatch_dict['user_input_path']
    output_result_path = sbatch_dict['output_result_path']
    output_log_path = sbatch_dict['output_log_path']
    output_intermediate_path = sbatch_dict['output_intermediate_path']
    parameters = sbatch_dict['parameters']

    sbatch_command = (
        'sbatch' +
        ' --output=' + output_log_path + 'sbatch.out' +
        ' --error=' + output_log_path + 'sbatch.err' +
        ' ' + local_settings.SCRIPTS + 'run_safety.sh' +
        ' -a ' + user_input_path['fasta'] + 
        ' -b ' + output_result_path + 
        ' -c ' + output_log_path + 'safety.log' + 
        ' -d ' + output_intermediate_path + 
        ' -e ' + str(parameters['toxicity_threshold']) +
        ' -f ' + parameters['toxicity_model'] +
        ' -g ' + str(parameters['allergencity_threshold']) +
        ' -h ' + parameters['allergencity_model']
    )
    print('sbatch_command', sbatch_command)
    sbatch_output = subprocess.check_output(sbatch_command, shell=True).decode("utf-8")  # Submitted batch job 1410435
    job_id = re.search(r"Submitted batch job (\d+)", sbatch_output).group(1)  # 1410435
    status = slurm_api.get_job_status(job_id)  # PENDING
    taskdetail_dict = {
        'job_id': job_id,
        'status': status,
    }
    return taskdetail_dict

def run_sequence_align(sbatch_dict):
    user_input_path = sbatch_dict['user_input_path']
    output_result_path = sbatch_dict['output_result_path']
    output_log_path = sbatch_dict['output_log_path']
    output_intermediate_path = sbatch_dict['output_intermediate_path']
    parameters = sbatch_dict['parameters']

    sbatch_command = (
        'sbatch' +
        ' --output=' + output_log_path + 'sbatch.out' +
        ' --error=' + output_log_path + 'sbatch.err' +
        ' ' + local_settings.SCRIPTS + 'run_seq_align.sh' +
        ' -a ' + user_input_path['fasta'] + 
        ' -b ' + output_result_path + 
        ' -c ' + output_log_path + 'sequencealign.log' + 
        ' -d ' + output_intermediate_path + 
        ' -e ' + str(parameters['window_size']) +
        ' -f ' + parameters['step_size'] +
        ' -g ' + str(parameters['evalue'])
    )
    print('sbatch_command', sbatch_command)
    sbatch_output = subprocess.check_output(sbatch_command, shell=True).decode("utf-8")  # Submitted batch job 1410435
    job_id = re.search(r"Submitted batch job (\d+)", sbatch_output).group(1)  # 1410435
    status = slurm_api.get_job_status(job_id)  # PENDING
    taskdetail_dict = {
        'job_id': job_id,
        'status': status,
    }
    return taskdetail_dict

def run_antigen_screening(sbatch_dict):
    user_input_path = sbatch_dict['user_input_path']
    output_result_path = sbatch_dict['output_result_path']
    output_log_path = sbatch_dict['output_log_path']
    parameters = sbatch_dict['parameters']

    sbatch_command = (
        'sbatch' +
        ' --output=' + output_log_path + 'sbatch.out' +
        ' --error=' + output_log_path + 'sbatch.err' +
        ' ' + local_settings.SCRIPTS + 'run_antigen_screening.sh' +
        ' -a ' + user_input_path['fasta'] + 
        ' -b ' + output_result_path + 
        ' -c ' + output_log_path + 'antigenscreening.log' + 
        ' -d ' + str(parameters['peptide_len_min']) +
        ' -e ' + str(parameters['peptide_len_max'])
    )
    print('sbatch_command', sbatch_command)
    sbatch_output = subprocess.check_output(sbatch_command, shell=True).decode("utf-8")  # Submitted batch job 1410435
    job_id = re.search(r"Submitted batch job (\d+)", sbatch_output).group(1)  # 1410435
    status = slurm_api.get_job_status(job_id)  # PENDING
    taskdetail_dict = {
        'job_id': job_id,
        'status': status,
    }
    return taskdetail_dict

def run_tsa(sbatch_dict):
    is_demo_input = sbatch_dict['is_demo_input']
    user_input_path = sbatch_dict['user_input_path']
    output_result_path = sbatch_dict['output_result_path']
    output_log_path = sbatch_dict['output_log_path']
    parameters = sbatch_dict['parameters']

    if is_demo_input:
        sbatch_command = (
            'sbatch' +
            ' --output=' + output_log_path + 'sbatch.out' +
            ' --error=' + output_log_path + 'sbatch.err' +
            ' ' + local_settings.SCRIPTS + 'run_tsa_demo.sh' +
            # ' -a ' + user_input_path[''] +
            ' -b ' + output_result_path +
            ' -c ' + output_log_path + 'tsa.log' +
            ' -d ' + str(parameters['sample']) +
            ' -e ' + str(parameters['mutation_type']) +
            ' -f ' + user_input_path['hlaI'] +
            ' -g ' + str(parameters['rmats_as_type']) +
            ' -h ' + str(parameters['spe_lcount']) 
        )
    else:
        sbatch_command = (
            'sbatch' + 
            ' --output=' + output_log_path + 'sbatch.out' +
            ' --error=' + output_log_path + 'sbatch.err' +
            ' ' + local_settings.SCRIPTS + 'run_tsa_user.sh' +
            ' -a ' + user_input_path['folder'] +
            ' -b ' + output_result_path +
            ' -c ' + output_log_path + 'tsa.log' +
            ' -d ' + str(parameters['sample']) +
            ' -e ' + str(parameters['mutation_type']) +
            ' -f ' + user_input_path['hlaI'] +
            ' -g ' + str(parameters['rmats_as_type']) +
            ' -h ' + str(parameters['spe_lcount']) 
        )

    print('sbatch_command', sbatch_command)
    sbatch_output = subprocess.check_output(sbatch_command, shell=True).decode("utf-8")  # Submitted batch job 1410435
    job_id = re.search(r"Submitted batch job (\d+)", sbatch_output).group(1)  # 1410435
    status = slurm_api.get_job_status(job_id)  # PENDING
    taskdetail_dict = {
        'job_id': job_id,
        'status': status,
    }
    return taskdetail_dict

def run_tcranno(sbatch_dict):
    user_input_path = sbatch_dict['user_input_path']['repertoire_path']
    output_result_path = sbatch_dict['output_result_path']
    output_log_path = sbatch_dict['output_log_path']
    parameters = sbatch_dict['parameters']

    sbatch_command = (
        'sbatch' +
        ' --output=' + output_log_path + '/sbatch.out' +
        ' --error=' + output_log_path + '/sbatch.err' +
        ' ' + str(local_settings.SCRIPTS / 'run_tcranno.sh') +
        ' -a ' + user_input_path +
        ' -b ' + output_result_path + '/' +
        ' -c ' + output_log_path + '/tcranno.log' + 
        ' -d ' + str(parameters['tcrannoanalysistype']) +
        ' -e ' + str(parameters['k']) + 
        ' -f ' + str(parameters['frequency_col']) + 
        ' -g ' + str(parameters['ref_db']) +
        ' -h ' + str(parameters['anno_type']) 
    )
    print('sbatch_command', sbatch_command)
    sbatch_output = subprocess.check_output(sbatch_command, shell=True).decode("utf-8")  # Submitted batch job 1410435
    job_id = re.search(r"Submitted batch job (\d+)", sbatch_output).group(1)  # 1410435
    status = slurm_api.get_job_status(job_id)  # PENDING
    taskdetail_dict = {
        'job_id': job_id,
        'status': status,
    }
    return taskdetail_dict


# 'parameters': {'sample': 'HGSC3', 'mutation_type': ['control', 'rna_edit', 'indel', 'snp', 'fusion', 'rmats', 'spe'], 'rmats_as_type': 'A3S', 'spe_lcount': '6'}}
# first run task and update task status
def update_task_que(taskdetail_dict, module, status, job_id):
    for task in taskdetail_dict["task_que"]:
        if task["module"] == module:
            task["module_satus"] = status
            task["job_id"] = job_id
    return taskdetail_dict

