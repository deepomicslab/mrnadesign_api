from utils import task, slurm_api
from mrna_task.models import mrna_task
from taskresult.models import lineardesign_taskresult
import datetime
from mrnadesign_api import settings_local as local_settings
import os,json
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mrnadesign_api.settings")
import django
django.setup()

def create_task(L, task_obj):
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

    if len(seq_name) != len(sequence) or len(seq_name) != len(structure) \
        or len(seq_name) != len(folding_free_energy) or len(seq_name) != len(cai):
        task_obj.status = 'Failed'

    task_obj.status = 'Success'
    for i in range(len(seq_name)):
        tr_obj = lineardesign_taskresult.objects.create(
            mrna_task_analysis_type = task_obj.analysis_type,
            task_id = task_obj.id,
            seq_name = seq_name[i],
            sequence = sequence[i],
            structure = structure[i],
            folding_free_energy = float(folding_free_energy[i]),
            cai = float(cai[i]),
        )
        task_obj.task_results.append(tr_obj.id)

# To manually run: python manage.py crontab run <tash_hash_id>
def task_status_updata():
    current_time = datetime.datetime.now()
    f = open(local_settings.TASKLOG + 'my_cronjob.log', 'a')
    f.write('exec update start  '+str(current_time)+"\n")
    tasklist = mrna_task.objects.filter(status='Running')

    for task_obj in tasklist:
        status = slurm_api.get_job_status(task_obj.job_id)
        if status == 'FAILED':
            task_obj.status = 'Failed'
        elif status == 'COMPLETED':
            if task_obj.analysis_type == 'Linear Design' \
                    and task.check_lineardesign_result(task_obj.output_result_path):
                with open(task_obj.output_result_path + 'result.txt', 'r') as fout:
                    L = fout.readlines()
                create_task(L, task_obj)
        task_obj.save()

    f.write('exec update end  '+str(current_time)+"\n")
    f.close()