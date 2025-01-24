import django
import os
import json
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mrnadesign_api.settings")

django.setup()

def add_data():
    from tsnadb.models import tsnadb_validated, tsnadb_neoantigen
    from mrnadesign_api import settings_local as local_settings
    import pandas as pd
    import numpy as np

    # ================================
    # ======= tsnadb_validated =======
    # ================================

    tsnadb_validated_df = pd.read_csv(
        local_settings.MRNADESIGN_DATABASE + 'tsnadb2/validated_tsnadb2.tsv', sep='\t').to_numpy()
    
    def na_check(x):
        if isinstance(x, str) and x == 'NA':
            return True
        if (isinstance(x, float)) and np.isnan(x):
            return True
        return False

    for l in tsnadb_validated_df:
        
        tsnadb_validated.objects.create(
            level = l[0],
            patient_id = l[1],
            tumor_type = l[2],
            tumor_type_detaile = l[3],
            mutation_type = l[4],
            gene = l[5],
            mutation = l[6],
            position = str(l[7]),
            mutant_peptide = l[8],
            hla = l[9],
            pubmed_id = l[10],
            reference_name = l[11],
            journal = l[12],
            year = int(l[13]) if not na_check(l[13]) else None,
            doi = l[14],
        )

    # =================================
    # ======= tsnadb_neoantigen =======
    # =================================

    for tool in ['Fusion', 'INDEL', 'SNV']:

        tsnadb_neoantigen_df = pd.read_csv(
            local_settings.MRNADESIGN_DATABASE + 'tsnadb2/' + tool + '-derived.tsv', sep='\t').to_numpy()
        
        for l in tsnadb_neoantigen_df:
            tsnadb_neoantigen.objects.create(
                type = l[0],
                tissue = l[1],
                mutation = l[2],
                hla = l[3],
                peptide = l[4],
                deep_bind = float(l[5]) if not na_check(l[5]) else None,
                deep_imm = float(l[6]) if not na_check(l[6]) else None,
                nhcf_rank_percent = float(l[7]) if not na_check(l[7]) else None,
                net4_aff_nm = float(l[8]) if not na_check(l[8]) else None,
                net4_aff_percent = float(l[9]) if not na_check(l[9]) else None,
                tpm = float(l[10]) if not na_check(l[10]) else None,
                frequency_in_the_tissue = l[11],
                frequency_in_all_samples = l[12],
            )
    