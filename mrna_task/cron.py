from utils import task, slurm_api
from mrna_task.models import mrna_task
import datetime
from mrnadesign_api import settings_local as local_settings
import os,json
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mrnadesign_api.settings")
import django
django.setup()

# To manually run: python manage.py crontab run <hash_id>
# crontab -l: to check hash_id
def task_status_updata():
    current_time = datetime.datetime.now()
    f = open(local_settings.TASKLOG / 'my_cronjob.log', 'a')
    f.write('exec update start '+str(current_time)+"\n")
    tasklist = mrna_task.objects.filter(status='Running')

    for task_obj in tasklist:
        status = slurm_api.get_job_status(task_obj.job_id)
        if status == 'FAILED':
            task_obj.status = 'Failed'
        elif status == 'COMPLETED':
            if task_obj.analysis_type == 'Linear Design':
                if task_obj.parameters['lineardesignanalysistype'] == 'cds_plus_35utr' \
                        and task.check_lineardesign_result_v1(task_obj.output_result_path) \
                        or task_obj.parameters['lineardesignanalysistype'] == 'cds_only' \
                        and task.check_lineardesign_result_v2(task_obj.output_result_path):
                    task_obj.status = 'Success'
            elif task_obj.analysis_type == 'Prediction' \
                    and task.check_prediction_result(task_obj.output_result_path):
                task_obj.status = 'Success'
            elif task_obj.analysis_type == 'Safety' \
                    and task.check_safety_result(task_obj.output_result_path):
                task_obj.status = 'Success'
            elif task_obj.analysis_type == 'Sequence Align' \
                    and task.check_sequencealign_result(task_obj.output_result_path):
                task_obj.status = 'Success'
            elif task_obj.analysis_type == 'Antigen Screening' \
                    and task.check_antigenscreening_result(task_obj.output_result_path):
                task_obj.status = 'Success'
            elif task_obj.analysis_type == 'TSA' \
                    and task.check_tsa_result(task_obj.output_log_path):
                task_obj.status = 'Success'
            elif task_obj.analysis_type == 'TCRanno' \
                    and task.check_tcranno_result(task_obj.output_result_path):
                task_obj.status = 'Success'
            elif task_obj.analysis_type == 'TCR Alpha-Beta Chain Pairing' \
                    and task.check_tcrabpairing_result(task_obj.output_log_path):
                task_obj.status = 'Success'
        task_obj.save()

    f.write('exec update end '+str(current_time)+"\n")
    f.close()
