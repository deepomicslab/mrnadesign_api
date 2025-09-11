from mrnadesign_api import settings_local as local_settings
from mrna_task.models import mrna_task
import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mrnadesign_api.settings")

django.setup()


demo_user_map = {
    # # ============================== two demo cases of linear design =============================
    # 'Demo User Linear Design - CDS plus 35utr': {
    #     'task_id': -99,
    #     'job_id': '1443108',
    #     'user_input_path': {
    #         'fasta': local_settings.DEMO_ANALYSIS + 'demouser_lineardesign_cds_plus_35utr/input/sequence.fasta',
    #         'utr3_path': local_settings.DEMO_ANALYSIS + 'demouser_lineardesign_cds_plus_35utr/input/utr3.fasta', 
    #         'utr5_path': local_settings.DEMO_ANALYSIS + 'demouser_lineardesign_cds_plus_35utr/input/utr5.fasta',
    #     },
    #     'is_demo_input': True,
    #     'output_result_path': local_settings.DEMO_ANALYSIS + 'demouser_lineardesign_cds_plus_35utr/output/result/',
    #     'output_log_path': local_settings.DEMO_ANALYSIS + 'demouser_lineardesign_cds_plus_35utr/output/log/',
    #     'analysis_type': 'Linear Design',
    #     'parameters': {
    #         "lambda": "0", 
    #         "codonusage": "human",
    #         "lineardesignanalysistype": "cds_plus_35utr",
    #     },
    #     'status': 'Success',
    #     'created_at': 'N/A',
    # },
    # 'Demo User Linear Design - CDS only': {
    #     'task_id': -98,
    #     'job_id': '1443109',
    #     'user_input_path': {
    #         'fasta': local_settings.DEMO_ANALYSIS + 'demouser_lineardesign_cds_only/input/sequence.fasta',
    #     },
    #     'is_demo_input': True,
    #     'output_result_path': local_settings.DEMO_ANALYSIS + 'demouser_lineardesign_cds_only/output/result/',
    #     'output_log_path': local_settings.DEMO_ANALYSIS + 'demouser_lineardesign_cds_only/output/log/',
    #     'analysis_type': 'Linear Design',
    #     'parameters': {
    #         "lambda": "0", 
    #         "codonusage": "human",
    #         "lineardesignanalysistype": "cds_only",
    #     },
    #     'status': 'Success',
    #     'created_at': 'N/A',
    # },

    # # ============================== three demo cases of prediction ============================== 
    # 'Demo User Prediction Task0001': {
    #     'task_id': -95,
    #     'job_id': '1446907',
    #     'user_input_path': {
    #         'config': local_settings.DEMO_ANALYSIS + 'demouser_prediction_task0001/task_prediction_config.ini',
    #         'sequence': local_settings.DEMO_ANALYSIS + 'demouser_prediction_task0001/sequences/input_seq.tsv',
    #     },
    #     'is_demo_input': True,
    #     'output_result_path': local_settings.DEMO_ANALYSIS + 'demouser_prediction_task0001/prediction_results/',
    #     'output_log_path': local_settings.DEMO_ANALYSIS + 'demouser_prediction_task0001/log/',
    #     'analysis_type': 'Prediction',
    #     'parameters': {}, # in the config file
    #     'status': 'Success',
    #     'created_at': 'N/A',
    # },
    # 'Demo User Prediction Task0002': {
    #     'task_id': -94,
    #     'job_id': '1446906',
    #     'user_input_path': {
    #         'config': local_settings.DEMO_ANALYSIS + 'demouser_prediction_task0002/task_prediction_config.ini',
    #         'sequence': local_settings.DEMO_ANALYSIS + 'demouser_prediction_task0002/sequences/input_seq.tsv',
    #     },
    #     'is_demo_input': True,
    #     'output_result_path': local_settings.DEMO_ANALYSIS + 'demouser_prediction_task0002/prediction_results/',
    #     'output_log_path': local_settings.DEMO_ANALYSIS + 'demouser_prediction_task0002/log/',
    #     'analysis_type': 'Prediction',
    #     'parameters': {}, # in the config file
    #     'status': 'Success',
    #     'created_at': 'N/A',
    # },
    # 'Demo User Prediction Task0003': {
    #     'task_id': -93,
    #     'job_id': '1446905',
    #     'user_input_path': {
    #         'config': local_settings.DEMO_ANALYSIS + 'demouser_prediction_task0003/task_prediction_config.ini',
    #         'sequence': local_settings.DEMO_ANALYSIS + 'demouser_prediction_task0003/sequences/input_seq.tsv',
    #     },
    #     'is_demo_input': True,
    #     'output_result_path': local_settings.DEMO_ANALYSIS + 'demouser_prediction_task0003/prediction_results/',
    #     'output_log_path': local_settings.DEMO_ANALYSIS + 'demouser_prediction_task0003/log/',
    #     'analysis_type': 'Prediction',
    #     'parameters': {}, # in the config file
    #     'status': 'Success',
    #     'created_at': 'N/A',
    # },

    # # ============================== one demo case of safety ============================== 
    # 'Demo User Safety': {
    #     'task_id': -80,
    #     'job_id': '1447000',
    #     'user_input_path': {
    #         'fasta': local_settings.DEMO_ANALYSIS + 'demouser_safety/input/sequence.fasta',
    #     },
    #     'is_demo_input': True,
    #     'output_result_path': local_settings.DEMO_ANALYSIS + 'demouser_safety/output/result/',
    #     'output_log_path': local_settings.DEMO_ANALYSIS + 'demouser_safety/output/log/',
    #     'analysis_type': 'Safety',
    #     'parameters': {
    #         "toxicity_model": "1", 
    #         "toxicity_threshold": "0.38", 
    #         "allergencity_model": "1", 
    #         "allergencity_threshold": "0.3",
    #     }, 
    #     'status': 'Success',
    #     'created_at': 'N/A',
    # },

    # # ============================== one demo case of sequence alignment ============================== 
    # 'Demo User Sequence Alignment': {
    #     'task_id': -70,
    #     'job_id': '1227000',
    #     'user_input_path': {
    #         'fasta': local_settings.DEMO_ANALYSIS + 'demouser_sequencealignment/input/sequence.fasta',
    #     },
    #     'is_demo_input': True,
    #     'output_result_path': local_settings.DEMO_ANALYSIS + 'demouser_sequencealignment/output/result/',
    #     'output_log_path': local_settings.DEMO_ANALYSIS + 'demouser_sequencealignment/output/log/',
    #     'analysis_type': 'Sequence Align',
    #     'parameters': {
    #         "window_size": "11",
    #         "step_size": "5",
    #         'evalue': '10' 
    #     }, 
    #     'status': 'Success',
    #     'created_at': 'N/A',
    # },

    # # ============================== one demo case of antigen screening ============================== 
    # 'Demo User Antigen Screening': {
    #     'task_id': -60,
    #     'job_id': '1327000',
    #     'user_input_path': {
    #         'fasta': local_settings.DEMO_ANALYSIS + 'demouser_antigenscreening/input/sequence.fasta',
    #     },
    #     'is_demo_input': True,
    #     'output_result_path': local_settings.DEMO_ANALYSIS + 'demouser_antigenscreening/output/result/',
    #     'output_log_path': local_settings.DEMO_ANALYSIS + 'demouser_antigenscreening/output/log/',
    #     'analysis_type': 'Antigen Screening',
    #     'parameters': {
    #         "peptide_len_min": "8",
    #         "peptide_len_max": "14",
    #     }, 
    #     'status': 'Success',
    #     'created_at': 'N/A',
    # },

    # # ============================== one demo case of tsa ============================================ 
    # 'Demo User TSA': {
    #     'task_id': -50,
    #     'job_id': '1227001',
    #     'user_input_path': {
    #         "hlaI": "/home/platform/project/mrnadesign_platform/mrnadesign_api/workspace/analysis_script/user/1744705311_XFZC/input/hlaI.txt"
    #     },
    #     'is_demo_input': True,
    #     'output_result_path': local_settings.DEMO_ANALYSIS + 'demouser_tsa_HGSC3/output/result/',
    #     'output_log_path': local_settings.DEMO_ANALYSIS + 'demouser_tsa_HGSC3/output/log/',
    #     'analysis_type': 'TSA',
    #     'parameters': {
    #         "sample": "HGSC3", 
    #         "spe_lcount": "6", 
    #         "mutation_type": "0123456", 
    #         "rmats_as_type": "A3S"
    #     }, 
    #     'status': 'Success',
    #     'created_at': 'N/A',
    # },

    # ============================== one demo case of tcranno ============================================ 
    'Demo User TCRanno': {
        'task_id': -40,
        'job_id': '1427000',
        'user_input_path': {
            'repertoire_path': local_settings.DEMO_ANALYSIS / 'demouser_tcranno/input/input_repertoire.tsv',
        },
        'is_demo_input': True,
        'output_result_path': local_settings.DEMO_ANALYSIS / 'demouser_tcranno/output/result/',
        'output_log_path': local_settings.DEMO_ANALYSIS / 'demouser_tcranno/output/log/',
        'analysis_type': 'TCRanno',
        'parameters': {
            "k": "10",
            "ref_db": "IEDB",
            "anno_type": "all",
            "frequency_col": "frequency",
            "tcrannoanalysistype": "qual_quant",
        },
        'status': 'Success',
        'created_at': 'N/A',
    }
}

def add_data():
    for userid in list(demo_user_map.keys()):
        if len(mrna_task.objects.filter(id=demo_user_map[userid]['task_id'])) > 0:
            continue

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
        )
    
if __name__ == "__main__":
    add_data()
