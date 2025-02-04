from mrnadesign_api import settings_local as local_settings
from mrna_task.models import mrna_task
import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Phage_api.settings")

django.setup()


demo_user_map = {
    # ============================== two demo cases of linear design =============================
    'Demo User Linear Design - CDS plus 35utr': {
        'task_id': -99,
        'job_id': '1443108',
        'user_input_path': {
            'fasta': local_settings.DEMO_ANALYSIS + 'demouser_lineardesign_cds_plus_35utr/input/sequence.fasta',
            'utr3_path': local_settings.DEMO_ANALYSIS + 'demouser_lineardesign_cds_plus_35utr/input/utr3.fasta', 
            'utr5_path': local_settings.DEMO_ANALYSIS + 'demouser_lineardesign_cds_plus_35utr/input/utr5.fasta',
        },
        'is_demo_input': True,
        'output_result_path': local_settings.DEMO_ANALYSIS + 'demouser_lineardesign_cds_plus_35utr/output/result/',
        'output_log_path': local_settings.DEMO_ANALYSIS + 'demouser_lineardesign_cds_plus_35utr/output/log/',
        'analysis_type': 'Linear Design',
        'parameters': {
            "lambda": "0", 
            "codonusage": "human",
            "lineardesignanalysistype": "cds_plus_35utr",
        },
        'status': 'Success',
        'created_at': 'N/A',
        'task_results': [],
    },
    'Demo User Linear Design - CDS only': {
        'task_id': -98,
        'job_id': '1443109',
        'user_input_path': {
            'fasta': local_settings.DEMO_ANALYSIS + 'demouser_lineardesign_cds_only/input/sequence.fasta',
        },
        'is_demo_input': True,
        'output_result_path': local_settings.DEMO_ANALYSIS + 'demouser_lineardesign_cds_only/output/result/',
        'output_log_path': local_settings.DEMO_ANALYSIS + 'demouser_lineardesign_cds_only/output/log/',
        'analysis_type': 'Linear Design',
        'parameters': {
            "lambda": "0", 
            "codonusage": "human",
            "lineardesignanalysistype": "cds_only",
        },
        'status': 'Success',
        'created_at': 'N/A',
        'task_results': [],
    },

    # ============================== three demo cases of prediction ============================== 
    'Demo User Prediction Task0001': {
        'task_id': -95,
        'job_id': '1446907',
        'user_input_path': {
            'config': local_settings.DEMO_ANALYSIS + 'demouser_prediction_task0001/task_prediction_config.ini',
            'sequence': local_settings.DEMO_ANALYSIS + 'demouser_prediction_task0001/sequences/input_seq.tsv',
        },
        'is_demo_input': True,
        'output_result_path': local_settings.DEMO_ANALYSIS + 'demouser_prediction_task0001/prediction_results/',
        'output_log_path': local_settings.DEMO_ANALYSIS + 'demouser_prediction_task0001/log/',
        'analysis_type': 'Prediction',
        'parameters': {}, # in the config file
        'status': 'Success',
        'created_at': 'N/A',
        'task_results': [-995, -996],
    },
    'Demo User Prediction Task0002': {
        'task_id': -94,
        'job_id': '1446906',
        'user_input_path': {
            'config': local_settings.DEMO_ANALYSIS + 'demouser_prediction_task0002/task_prediction_config.ini',
            'sequence': local_settings.DEMO_ANALYSIS + 'demouser_prediction_task0002/sequences/input_seq.tsv',
        },
        'is_demo_input': True,
        'output_result_path': local_settings.DEMO_ANALYSIS + 'demouser_prediction_task0002/prediction_results/',
        'output_log_path': local_settings.DEMO_ANALYSIS + 'demouser_prediction_task0002/log/',
        'analysis_type': 'Prediction',
        'parameters': {}, # in the config file
        'status': 'Success',
        'created_at': 'N/A',
        'task_results': [-997, -998],
    },
    'Demo User Prediction Task0003': {
        'task_id': -93,
        'job_id': '1446905',
        'user_input_path': {
            'config': local_settings.DEMO_ANALYSIS + 'demouser_prediction_task0003/task_prediction_config.ini',
            'sequence': local_settings.DEMO_ANALYSIS + 'demouser_prediction_task0003/sequences/input_seq.tsv',
        },
        'is_demo_input': True,
        'output_result_path': local_settings.DEMO_ANALYSIS + 'demouser_prediction_task0003/prediction_results/',
        'output_log_path': local_settings.DEMO_ANALYSIS + 'demouser_prediction_task0003/log/',
        'analysis_type': 'Prediction',
        'parameters': {}, # in the config file
        'status': 'Success',
        'created_at': 'N/A',
        'task_results': [-999],
    },

    # ============================== one demo case of safety ============================== 
    'Demo User Safety': {
        'task_id': -80,
        'job_id': '1447000',
        'user_input_path': {
            'fasta': local_settings.DEMO_ANALYSIS + 'demouser_safety/input/sequence.fasta',
        },
        'is_demo_input': True,
        'output_result_path': local_settings.DEMO_ANALYSIS + 'demouser_safety/output/result/',
        'output_log_path': local_settings.DEMO_ANALYSIS + 'demouser_safety/output/log/',
        'analysis_type': 'Safety',
        'parameters': {
            "toxicity_model": "1", 
            "toxicity_threshold": "0.38", 
            "allergencity_model": "1", 
            "allergencity_threshold": "0.3",
        }, 
        'status': 'Success',
        'created_at': 'N/A',
        'task_results': [],
    },

    # ============================== one demo case of sequence alignment ============================== 
    'Demo User Sequence Alignment': {
        'task_id': -70,
        'job_id': '1227000',
        'user_input_path': {
            'fasta': local_settings.DEMO_ANALYSIS + 'demouser_sequencealignment/input/sequence.fasta',
        },
        'is_demo_input': True,
        'output_result_path': local_settings.DEMO_ANALYSIS + 'demouser_sequencealignment/output/result/',
        'output_log_path': local_settings.DEMO_ANALYSIS + 'demouser_sequencealignment/output/log/',
        'analysis_type': 'Sequence Align',
        'parameters': {
            "window_size": "11",
            "step_size": "5",
            'evalue': '10' 
        }, 
        'status': 'Success',
        'created_at': 'N/A',
        'task_results': [],
    },
}

demo_user_task_map = {
    # ============================== prediction ============================== 
    -995: {
        'mrna_task_analysis_type': 'Prediction',
        'task_id': -95,
        'task_name': 'SEQ000000',
    },
    -996: {
        'mrna_task_analysis_type': 'Prediction',
        'task_id': -95,
        'task_name': 'SEQ000001',
    },
    -997: {
        'mrna_task_analysis_type': 'Prediction',
        'task_id': -94,
        'task_name': 'SEQ000000',
    },
    -998: {
        'mrna_task_analysis_type': 'Prediction',
        'task_id': -94,
        'task_name': 'SEQ000001',
    },
    -999: {
        'mrna_task_analysis_type': 'Prediction',
        'task_id': -93,
        'task_name': 'SEQ000000',
    },

    # ============================== linear design ============================== 
    # skip
    # ============================== safety ============================== 
    # skip
    # ============================== sequence alignment ============================== 
    # skip
}


def add_data():
    for userid in list(demo_user_map.keys()):
        if len(mrna_task.objects.filter(id=demo_user_map[userid]['task_id'])) > 0:
            continue

        for task_result_id in demo_user_map[userid]['task_results']:
            if demo_user_task_map[task_result_id]['mrna_task_analysis_type'] == 'Prediction':
                from taskresult.models import prediction_taskresult
                if len(prediction_taskresult.objects.filter(id=task_result_id)) > 0:
                    continue
                prediction_taskresult.objects.create(
                    id=task_result_id,
                    mrna_task_analysis_type=demo_user_task_map[task_result_id]['mrna_task_analysis_type'],
                    task_id=demo_user_task_map[task_result_id]['task_id'],
                    task_name=demo_user_task_map[task_result_id]['task_name'],
                )
            # elif demo_user_task_map[task_result_id]['mrna_task_analysis_type'] == 'Linear Design':
                # pass
            # elif demo_user_task_map[task_result_id]['mrna_task_analysis_type'] == 'Safety':
                # pass
            # elif demo_user_task_map[task_result_id]['mrna_task_analysis_type'] == 'Sequence Align':
                # pass

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
