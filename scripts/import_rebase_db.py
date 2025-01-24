import django
import os
import json
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mrnadesign_api.settings")

django.setup()

def add_data():
    from rebase_db.models import rebase_data, rebase_enzyme_link
    from mrnadesign_api import settings_local as local_settings
    import pandas as pd
    import numpy as np
    
    # ================================
    # ======= rebase_data ============
    # ================================

    rebase_data_df = pd.read_csv(
        local_settings.MRNADESIGN_DATABASE + 'rebase/processed/rebase_restriction_site_information.tsv', sep='\t').to_numpy()
    
    for l in rebase_data_df:
        
        rebase_data.objects.create(
            accession_number = l[0],
            recognition_seq_w_cleavage_site = l[1],
            recognition_site = l[2],
            enzyme_name_list = [i.strip() for i in l[3].split(',')],
            enzyme_type = l[4],
            suppliers = l[5],
            prototype = l[6],
        )

    # =================================
    # ======= rebase_enzyme_link ======
    # =================================

    rebase_enzyme_link_df = pd.read_csv(
        local_settings.MRNADESIGN_DATABASE + 'rebase/processed/rebase_enzyme_pages.tsv', sep='\t').to_numpy()
    
    for l in rebase_enzyme_link_df:
        rebase_enzyme_link.objects.create(
            enzyme_name = l[0],
            enzyme_page = l[1],
        )
