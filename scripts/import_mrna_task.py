from mrnadesign_api import settings_local as local_settings
import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Phage_api.settings")

django.setup()


demo_user_map = {
    'Demo User Linear Design': {
        'task_id': -99,
        'job_id': '1443108',
        'user_input_path': {
            'fasta': local_settings.DEMO_ANALYSIS + 'demouser_lineardesign/input/sequence.fasta',
        },
        'is_demo_input': True,
        'output_result_path': local_settings.DEMO_ANALYSIS + 'demouser_lineardesign/output/result/',
        'output_log_path': local_settings.DEMO_ANALYSIS + 'demouser_lineardesign/output/log/',
        'analysis_type': 'Linear Design',
        'parameters': {
            "lambda": "0", 
            "codonusage": "human",
        },
        'status': 'Success',
        'created_at': 'N/A',
        'task_results': [-990, -991],
    },
}

demo_user_task_map = {
    -990: {
        'mrna_task_analysis_type': 'Linear Design',
        'task_id': -99,
        'seq_name': '>seq1',
        'sequence': 'AUGCCAAACACUUUGGCAUGCCCG',
        'structure': '((((((((...)))))))).....',
        'folding_free_energy': -7.4,
        'cai': 0.653,
    },
    -991: {
        'mrna_task_analysis_type': 'Linear Design',
        'task_id': -99,
        'seq_name': '>seq2',
        'sequence': 'AUGCUGGAUCAGGUCAACAAGCUGAAGUACCCUGAGGUUUCGUUGACCUGA',
        'structure': '........(((((((((((((((..((....))..))))).))))))))))',
        'folding_free_energy': -20.7,
        'cai': 0.768,
    },
}


def add_data():
    from mrna_task.models import mrna_task
    from taskresult.models import lineardesign_taskresult

    for userid in list(demo_user_map.keys()):
        if len(mrna_task.objects.filter(id=demo_user_map[userid]['task_id'])) > 0:
            continue

        for task_result_id in demo_user_map[userid]['task_results']:
            if len(lineardesign_taskresult.objects.filter(id=task_result_id)) > 0:
                continue
            lineardesign_taskresult.objects.create(
                id=task_result_id,
                mrna_task_analysis_type=demo_user_task_map[task_result_id]['mrna_task_analysis_type'],
                task_id=demo_user_task_map[task_result_id]['task_id'],
                seq_name=demo_user_task_map[task_result_id]['seq_name'],
                sequence=demo_user_task_map[task_result_id]['sequence'],
                structure=demo_user_task_map[task_result_id]['structure'],
                folding_free_energy=demo_user_task_map[task_result_id]['folding_free_energy'],
                cai=demo_user_task_map[task_result_id]['cai'],
            )

        mrna_task.objects.create(
            id=demo_user_map[userid]['task_id'],
            job_id=demo_user_map[userid]['job_id'],
            user_id=userid,
            user_input_path=demo_user_map[userid]['user_input_path'],
            is_demo_input=demo_user_map[userid]['is_demo_input'],
            output_result_path=demo_user_map[userid]['output_result_path'],
            output_log_path=demo_user_map[userid]['output_log_path'],
            analysis_type=demo_user_map[userid]['analysis_type'],
            parameters=demo_user_map[userid]['parameters'],
            status=demo_user_map[userid]['status'],
            created_at = demo_user_map[userid]['created_at'],
            task_results = demo_user_map[userid]['task_results'],
        )


if __name__ == "__main__":
    add_data()
