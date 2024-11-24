from mrnadesign_api import settings_local as local_settings
from utils import slurm_api
import json
import subprocess
import re
import glob
import os

def run_lineardesign(sbatch_dict):
    user_input_path = sbatch_dict['user_input_path']
    parameters = sbatch_dict['parameters']
    output_result_path = sbatch_dict['output_result_path']
    output_log_path = sbatch_dict['output_log_path']

    sbatch_command = (
        'sbatch' +
        ' --output=' + output_log_path + 'sbatch.out' +
        ' --error=' + output_log_path + 'sbatch.err' +
        ' ' + local_settings.SCRIPTS + 'run_lineardesign.sh' +
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

def check_lineardesign_result(output_result_path):
    with open(output_result_path+'result.txt') as f:
        L = f.read()
    if 'mRNA sequence' in L: 
        return True
    print('Linear Design Failed')
    return False

def check_prediction_result(output_result_path):
    if os.path.exists(output_result_path):
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
    
def run_prediction(sbatch_dict):
    task_dir = sbatch_dict['task_dir']
    user_input_path = sbatch_dict['user_input_path']
    output_log_path = sbatch_dict['output_log_path']

    sbatch_command = (
        'sbatch' +
        ' --output=' + output_log_path + 'sbatch.out' +
        ' --error=' + output_log_path + 'sbatch.err' +
        ' ' + local_settings.SCRIPTS + 'run_prediction.sh' +
        ' -a ' + task_dir +
        ' -b ' + user_input_path['config'] + 
        ' -c ' + output_log_path + 'prediction.log'
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

# #    infodict = {'taskid': newtask.id, 'userpath': usertask, 'modulelist': modulelist,
# #                 'analysis_type': request.data['analysistype'], 'userid': request.data['userid']}

# ##### run analysis script#####


# def init_taskdetail_dict(info_dict):
#     new_dict = {}
#     new_dict["taskid"] = info_dict["taskid"]
#     new_dict["userpath"] = info_dict["userpath"]
#     new_dict["task_status"] = "create"
#     module_list = info_dict["modulelist"]
#     new_dict["modulelist"] = module_list
#     new_dict["analysis_type"] = info_dict["analysis_type"]
#     new_dict["userid"] = info_dict["userid"]

#     task_que = []
#     if 'transmembrane' in module_list and 'annotation' not in module_list:
#         new_dict["log"] = "Transmembrane Protein Annotation must need ORF prediction & Protein classification"
#         new_dict["status"] = "error"

#     if 'terminator' in module_list and 'annotation' not in module_list:
#         new_dict["log"] = "Transcription Terminator Annotation must need ORF prediction & Protein classification"
#         new_dict["status"] = "error"

#     if 'anticrispr' in module_list and 'annotation' not in module_list:
#         new_dict["log"] = "Anti-CRISPR Protein Annotation must need ORF prediction & Protein classification"
#         new_dict["status"] = "error"
    
#     # annotation must be the first module
#     if 'annotation' in module_list:
#         task_dict = {'module': 'annotation',
#                      'module_satus': 'waiting', 'job_id': '', 'module_log': {'output': '', 'error': ''}}
#         task_que.append(task_dict)
#     for module in module_list:
#         if module == 'annotation':
#             continue
#         task_dict = {'module': module,
#                      'module_satus': 'waiting', 'job_id': '', 'module_log': {'output': '', 'error': ''}}
#         task_que.append(task_dict)
#     new_dict["task_que"] = task_que
#     return new_dict

# first run task and update task status
def update_task_que(taskdetail_dict, module, status, job_id):
    for task in taskdetail_dict["task_que"]:
        if task["module"] == module:
            task["module_satus"] = status
            task["job_id"] = job_id
    return taskdetail_dict


# def run_annotation(taskdetail_dict):
#     # sbatch /home/platform/phage_db/phage_api/workspace/analysis_script/annotation/run.sh /home/platform/phage_db/phage_api/workspace/user_task/sequence.fasta /home/platform/phage_db/phage_api/workspace/user_task/output
#     userpath = taskdetail_dict["userpath"]
#     inputpath = userpath + "/upload/sequence.fasta"
#     outputpath = userpath + "/output/rawdata/annotation"
#     shell_script = local_settings.ANALYSIS + "annotation_v2/run.sh"
#     script_arguments = [inputpath, outputpath]
#     #shell_script = "/home/platform/phage_db/phage_api/workspace/analysis_script/annotation/run.sh"
#     job_id = slurm_api.submit_job(
#         shell_script, script_arguments=script_arguments)
#     status = slurm_api.get_job_status(job_id)
#     taskdetail_dict = update_task_que(
#         taskdetail_dict, "annotation", status, job_id)
#     return taskdetail_dict


# def run_quality(taskdetail_dict):
#     # sbatch /home/platform/phage_db/phage_api/workspace/analysis_script/quality/run.sh /home/platform/phage_db/phage_api/workspace/user_task/sequence.fasta /home/platform/phage_db/phage_api/workspace/user_task/output
#     userpath = taskdetail_dict["userpath"]
#     inputpath = userpath + "/upload/sequence.fasta"
#     outputpath = userpath + "/output/rawdata/quality"
#     shell_script = local_settings.ANALYSIS + "quality/run.sh"
#     script_arguments = [inputpath, outputpath]
#     shell_script = "/home/platform/phage_db/phage_api/workspace/analysis_script/quality/run.sh"
#     job_id = slurm_api.submit_job(
#         shell_script, script_arguments=script_arguments)
#     status = slurm_api.get_job_status(job_id)
#     taskdetail_dict = update_task_que(
#         taskdetail_dict, "quality", status, job_id)
#     return taskdetail_dict


# def run_host(taskdetail_dict):
#     # sbatch /home/platform/phage_db/phage_api/workspace/analysis_script/host/run.sh /home/platform/phage_db/phage_api/workspace/user_task/sequence.fasta /home/platform/phage_db/phage_api/workspace/user_task/output
#     userpath = taskdetail_dict["userpath"]
#     inputpath = userpath + "/upload/sequence.fasta"
#     outputpath = userpath + "/output/rawdata/host"
#     shell_script = local_settings.ANALYSIS + "host/run.sh"
#     script_arguments = [inputpath, outputpath]
#     shell_script = "/home/platform/phage_db/phage_api/workspace/analysis_script/host/run.sh"
#     job_id = slurm_api.submit_job(
#         shell_script, script_arguments=script_arguments)
#     status = slurm_api.get_job_status(job_id)
#     taskdetail_dict = update_task_que(
#         taskdetail_dict, "host", status, job_id)
#     return taskdetail_dict


# def run_lifestyle(taskdetail_dict):
#     # sbatch /home/platform/phage_db/phage_api/workspace/analysis_script/lifestyle/run.sh /home/platform/phage_db/phage_api/workspace/user_task/sequence.fasta /home/platform/phage_db/phage_api/workspace/user_task/output
#     userpath = taskdetail_dict["userpath"]
#     inputpath = userpath + "/upload/sequence.fasta"
#     outputpath = userpath + "/output/rawdata/lifestyle/result.txt"
#     outputpathdir = userpath + "/output/rawdata/lifestyle"
#     shell_script = local_settings.ANALYSIS + "lifestyle/run.sh"
#     script_arguments = [inputpath, outputpath, outputpathdir]
#     shell_script = "/home/platform/phage_db/phage_api/workspace/analysis_script/lifestyle/run.sh"
#     job_id = slurm_api.submit_job(
#         shell_script, script_arguments=script_arguments)
#     status = slurm_api.get_job_status(job_id)
#     taskdetail_dict = update_task_que(
#         taskdetail_dict, "lifestyle", status, job_id)
#     return taskdetail_dict


# def run_transmembrane(taskdetail_dict):
#     userpath = taskdetail_dict["userpath"]
#     inputpath = userpath + "/output/rawdata/annotation/gene.faa"
#     outputpath = userpath + "/output/rawdata/transmembrane/result.txt"
#     outputpathdir = userpath + "/output/rawdata/transmembrane"
#     shell_script = local_settings.ANALYSIS + "transmembrane/run.sh"
#     script_arguments = [inputpath, outputpath, outputpathdir]
#     annotation_job_id = -1
#     for task in taskdetail_dict["task_que"]:
#         if task["module"] == 'annotation':
#             annotation_job_id = int(task["job_id"])

#     if annotation_job_id != -1:
#         job_id = slurm_api.submit_job(
#             shell_script, script_arguments=script_arguments, dependency_job_ids=[annotation_job_id])
#         status = slurm_api.get_job_status(job_id)
#         taskdetail_dict = update_task_que(
#             taskdetail_dict, "transmembrane", status, job_id)
#     else:
#         taskdetail_dict["task_status"] = "error"
#     return taskdetail_dict


# def run_arvf(taskdetail_dict):
#     userpath = taskdetail_dict["userpath"]
#     inputpath = userpath + "/output/rawdata/annotation/gene.faa"
#     outputpath = userpath + "/output/rawdata/arvf"
#     shell_script = local_settings.ANALYSIS + "arvf/run.sh"
#     script_arguments = [inputpath, outputpath]
#     annotation_job_id = -1
#     for task in taskdetail_dict["task_que"]:
#         if task["module"] == 'annotation':
#             annotation_job_id = int(task["job_id"])

#     if annotation_job_id != -1:
#         job_id = slurm_api.submit_job(
#             shell_script, script_arguments=script_arguments, dependency_job_ids=[annotation_job_id])
#         status = slurm_api.get_job_status(job_id)
#         taskdetail_dict = update_task_que(
#             taskdetail_dict, "arvf", status, job_id)
#     else:
#         taskdetail_dict["task_status"] = "error"
#     return taskdetail_dict

# def run_trna(taskdetail_dict):
#     userpath = taskdetail_dict["userpath"]
#     inputpath = userpath + "/upload/sequence.fasta"
#     outputpath = userpath + "/output/rawdata/trna"
#     # shell_script = local_settings.ANALYSIS + "tRNA2/run.sh"
#     script_arguments = [inputpath, outputpath]
#     shell_script = "/home/platform/phage_db/phage_api/workspace/analysis_script/tRNA2/run.sh"
#     job_id = slurm_api.submit_job(
#         shell_script, script_arguments=script_arguments)
#     status = slurm_api.get_job_status(job_id)
#     taskdetail_dict = update_task_que(
#         taskdetail_dict, "trna", status, job_id)
#     return taskdetail_dict



# # /home/platform/phage_db/phage_api/workspace/analysis_script/sequencecomparison/run.sh
# # /home/platform/phage_db/phage_api/workspace/analysis_script/sequencecomparison/test/gene.faa
# # None
# # /home/platform/phage_db/phage_api/workspace/analysis_script/sequencecomparison/test/sequence.gff3
# # /home/platform/phage_db/phage_api/workspace/user_task/comparison
# # 1
# def run_alignment(taskdetail_dict):
#     userpath = taskdetail_dict["userpath"]
#     inputfaapath = userpath + "/output/rawdata/annotation/gene.faa"
#     inputgffpath = userpath + "/output/rawdata/annotation/sequence.gff3"
#     outputpathdir = userpath + "/output/rawdata/alignment"
#     shell_script = local_settings.ANALYSIS + "alignment/run.sh"
#     script_arguments = [inputfaapath, 'None',inputgffpath, outputpathdir, '1']
#     annotation_job_id = -1
#     for task in taskdetail_dict["task_que"]:
#         if task["module"] == 'annotation':
#             annotation_job_id = int(task["job_id"])

#     if annotation_job_id != -1:
#         job_id = slurm_api.submit_job(
#             shell_script, script_arguments=script_arguments, dependency_job_ids=[annotation_job_id])
#         status = slurm_api.get_job_status(job_id)
#         taskdetail_dict = update_task_que(
#             taskdetail_dict, "alignment", status, job_id)
#     else:
#         taskdetail_dict["task_status"] = "error"
#     return taskdetail_dict


# # /home/platform/phage_db/phage_api/workspace/analysis_script/terminator/run.sh

# # /home/platform/phage_db/phage_api/workspace/user_task/1690265364_4345/output/rawdata/annotation/acc_list.txt

# # /home/platform/phage_db/phage_api/workspace/user_task/1690265364_4345/upload/sequence.fasta

# # /home/platform/phage_db/phage_api/workspace/user_task/terminator
# def run_terminator(taskdetail_dict):
#     userpath = taskdetail_dict["userpath"]
#     inputacclistpath = userpath + "/output/rawdata/annotation/acc_list.txt"
#     inputpath = userpath + "/upload/sequence.fasta"
#     outputpathdir = userpath + "/output/rawdata/terminator"
#     shell_script = local_settings.ANALYSIS + "terminator/run.sh"
#     script_arguments = [inputacclistpath, inputpath, outputpathdir]
#     annotation_job_id = -1
#     for task in taskdetail_dict["task_que"]:
#         if task["module"] == 'annotation':
#             annotation_job_id = int(task["job_id"])

#     if annotation_job_id != -1:
#         job_id = slurm_api.submit_job(
#             shell_script, script_arguments=script_arguments, dependency_job_ids=[annotation_job_id])
#         status = slurm_api.get_job_status(job_id)
#         taskdetail_dict = update_task_que(
#             taskdetail_dict, "terminator", status, job_id)
#     else:
#         taskdetail_dict["task_status"] = "error"
#     return taskdetail_dict



# def run_anticrispr(taskdetail_dict):
#     userpath = taskdetail_dict["userpath"]

#     inputpath = userpath + "/output/rawdata/annotation/gene.faa"
#     outputpathdir = userpath + "/output/rawdata/anticrispr"
#     shell_script = local_settings.ANALYSIS + "anticrispr2/run.sh"
#     script_arguments = [inputpath, outputpathdir]
#     # job_id = slurm_api.submit_job(
#     #     shell_script, script_arguments=script_arguments)
#     # status = slurm_api.get_job_status(job_id)
#     # taskdetail_dict = update_task_que(
#     #     taskdetail_dict, "anticrispr", status, job_id)
    
#     annotation_job_id = -1
#     for task in taskdetail_dict["task_que"]:
#         if task["module"] == 'annotation':
#             annotation_job_id = int(task["job_id"])

#     if annotation_job_id != -1:
#         job_id = slurm_api.submit_job(
#             shell_script, script_arguments=script_arguments, dependency_job_ids=[annotation_job_id])
#         status = slurm_api.get_job_status(job_id)
#         taskdetail_dict = update_task_que(
#             taskdetail_dict, "anticrispr", status, job_id)
#     else:
#         taskdetail_dict["task_status"] = "error"
#     return taskdetail_dict

# def run_crispr(taskdetail_dict):
#     userpath = taskdetail_dict["userpath"]

#     inputpath = userpath + "/upload/sequence.fasta"
#     outputpathdir = userpath + "/output/rawdata/crispr"
#     shell_script = local_settings.ANALYSIS + "crispr/run.sh"
#     script_arguments = [inputpath, outputpathdir]
#     job_id = slurm_api.submit_job(
#         shell_script, script_arguments=script_arguments)
#     status = slurm_api.get_job_status(job_id)
#     taskdetail_dict = update_task_que(
#         taskdetail_dict, "crispr", status, job_id)
#     return taskdetail_dict


# def run_taxonomic(taskdetail_dict):
#     userpath = taskdetail_dict["userpath"]
#     inputfaapath = userpath + "/output/rawdata/annotation/gene.faa"
#     inputgffpath = userpath + "/output/rawdata/annotation/sequence.gff3"
#     outputpathdir = userpath + "/output/rawdata/taxonomic"
#     shell_script = local_settings.ANALYSIS + "taxonomic/run.sh"
#     script_arguments = [inputfaapath,inputgffpath, outputpathdir]
#     annotation_job_id = -1
#     for task in taskdetail_dict["task_que"]:
#         if task["module"] == 'annotation':
#             annotation_job_id = int(task["job_id"])

#     if annotation_job_id != -1:
#         job_id = slurm_api.submit_job(
#             shell_script, script_arguments=script_arguments, dependency_job_ids=[annotation_job_id])
#         status = slurm_api.get_job_status(job_id)
#         taskdetail_dict = update_task_que(
#             taskdetail_dict, "taxonomic", status, job_id)
#     else:
#         taskdetail_dict["task_status"] = "error"
#     return taskdetail_dict


# def run_annotation_pipline(taskdetail_dict):
#     module_list = taskdetail_dict["modulelist"]
#     for module in module_list:
#         if module == "annotation":
#             taskdetail_dict = run_annotation(taskdetail_dict)
#         elif module == "quality":
#             taskdetail_dict = run_quality(taskdetail_dict)
#         elif module == "host":
#             taskdetail_dict = run_host(taskdetail_dict)
#         elif module == "lifestyle":
#             taskdetail_dict = run_lifestyle(taskdetail_dict)
#         elif module == "trna":
#             taskdetail_dict = run_trna(taskdetail_dict)
#         elif module == "transmembrane":
#             taskdetail_dict = run_transmembrane(taskdetail_dict)
#         elif module == "alignment":
#             taskdetail_dict = run_alignment(taskdetail_dict)
#         elif module == "terminator":
#             taskdetail_dict = run_terminator(taskdetail_dict)
#         elif module == "crispr":
#             taskdetail_dict = run_crispr(taskdetail_dict)
#         elif module == "anticrispr":
#             taskdetail_dict = run_anticrispr(taskdetail_dict)
#         elif module == "arvf":
#             taskdetail_dict = run_arvf(taskdetail_dict)
#         elif module == "taxonomic":
#             taskdetail_dict = run_taxonomic(taskdetail_dict)
#     return taskdetail_dict










# def run_cluster(taskdetail_dict):
#     userpath = taskdetail_dict["userpath"]
#     inputpath = userpath + "/upload/sequence.fasta"
#     outputpath = userpath + "/output/rawdata/cluster"
#     outputpath_tree= userpath + "/output/rawdata/tree"
#     outputpath_annotation= userpath + "/output/rawdata/annotation"
#     outputpath_alignment= userpath + "/output/rawdata/alignment"
#     script_arguments = [inputpath, outputpath,outputpath_tree,outputpath_annotation,outputpath_alignment]
    
#     shell_script = "/home/platform/phage_db/phage_api/workspace/analysis_script/clustering/run.sh"

#     annotation_job_id = -1
#     for task in taskdetail_dict["task_que"]:
#         if task["module"] == 'annotation':
#             annotation_job_id = int(task["job_id"])

#     if annotation_job_id != -1:
#         job_id = slurm_api.submit_job(
#             shell_script, script_arguments=script_arguments, dependency_job_ids=[annotation_job_id])
#         status = slurm_api.get_job_status(job_id)
#         taskdetail_dict = update_task_que(
#             taskdetail_dict, "cluster", status, job_id)
#     else:
#         taskdetail_dict["task_status"] = "error"
#     return taskdetail_dict



# def run_tree(taskdetail_dict):
#     userpath = taskdetail_dict["userpath"]
#     inputpath = userpath + "/upload/sequence.fasta"
#     outputpath_tree= userpath + "/output/rawdata/tree"
#     script_arguments = [inputpath,outputpath_tree]

#     shell_script = "/home/platform/phage_db/phage_api/workspace/analysis_script/phylogenetictree/run.sh"
#     job_id = slurm_api.submit_job(
#         shell_script, script_arguments=script_arguments)
#     status = slurm_api.get_job_status(job_id)
#     taskdetail_dict = update_task_que(
#         taskdetail_dict, "tree", status, job_id)
#     return taskdetail_dict


# def run_comparedatabse(taskdetail_dict):
#     '''
#     #1 input fasta 
#     #2 output directory
#     #3 database fasta
#     #4 tree output directory
#     '''

#     #cluster
#     userpath = taskdetail_dict["userpath"]
#     inputpath = userpath + "/upload/sequence.fasta"
#     outputpath_compare= userpath + "/output/rawdata/comparedatabse"
#     outputpath_tree= userpath + "/output/rawdata/tree"
#     #databasejson= userpath + "/upload/database.json"
#     databsefile='/home/platform/phage_db/phage_api/workspace/analysis_script/comparedatabse/group_rep.fasta'

#     script_arguments = [inputpath,outputpath_compare,databsefile,outputpath_tree]

#     shell_script = "/home/platform/phage_db/phage_api/workspace/analysis_script/comparedatabse/run.sh"
#     job_id = slurm_api.submit_job(
#         shell_script, script_arguments=script_arguments)
#     status = slurm_api.get_job_status(job_id)
#     taskdetail_dict = update_task_que(
#         taskdetail_dict, "comparedatabse", status, job_id)
#     taskdetail_dict = update_task_que(
#         taskdetail_dict, "tree", status, job_id)
#     taskdetail_dict = update_task_que(
#         taskdetail_dict, "cluster", status, job_id)
#     outputpath = userpath + "/output/rawdata/annotation"
#     shell_script = local_settings.ANALYSIS + "annotation_v2/run.sh"
#     script_arguments = [inputpath, outputpath]
#     job_id = slurm_api.submit_job(
#         shell_script, script_arguments=script_arguments, dependency_job_ids=[job_id])
#     status = slurm_api.get_job_status(job_id)
#     taskdetail_dict = update_task_que(
#         taskdetail_dict, "annotation", status, job_id)
#     taskdetail_dict=run_alignment(taskdetail_dict)

#     return taskdetail_dict

# def run_cluster_pipline(taskdetail_dict):
#     module_list = taskdetail_dict["modulelist"]
#     if 'comparedatabse' in module_list:
#         taskdetail_dict = run_comparedatabse(taskdetail_dict)
#     else:
#         for module in module_list:
#             if module == "annotation":
#                 taskdetail_dict = run_annotation(taskdetail_dict)
#             elif module == "cluster":
#                 taskdetail_dict = run_cluster(taskdetail_dict)
#             elif module == "tree":
#                 taskdetail_dict = run_tree(taskdetail_dict)
#             elif module == "alignment":
#                 taskdetail_dict = run_alignment(taskdetail_dict)
#     return taskdetail_dict


