from utils import task, slurm_api
from mrna_task.models import mrna_task
import datetime
from mrnadesign_api import settings_local as local_settings


# To manually run: python manage.py crontab run <tash_hash_id>
def task_status_updata():
    current_time = datetime.datetime.now()
    f = open(local_settings.TASKLOG + 'my_cronjob.log', 'a')
    f.write('exec update start  '+str(current_time)+"\n")
    tasklist = mrna_task.objects.filter(status='Running')

    for task_obj in tasklist:
        job_id = task_obj.job_id
        status = slurm_api.get_job_status(job_id)
        if status == 'FAILED':
            task_obj.status = 'Failed'
        elif status == 'COMPLETED':
            if task_obj.analysis_type == 'Linear Design' \
                    and task.check_lineardesign_result(task_obj.output_result_path):
                task_obj.status = 'Success'
            else:
                task_obj.status = 'Failed'
        task_obj.save()

    f.write('exec update end  '+str(current_time)+"\n")
    f.close()
