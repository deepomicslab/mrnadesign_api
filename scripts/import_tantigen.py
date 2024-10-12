import django
import os,json
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mrnsdesign_api.settings")

django.setup()

def add_data():
    from tantigen.models import tantigen
    from mrnadesign_api import settings_local as local_settings
    import pandas as pd

    tantigendb_se_df = pd.read_csv(local_settings.MRNADESIGN_DATABASE + 'TAntigendb_se.csv')
    tantigen_rna_seq_df = pd.read_csv(local_settings.MRNADESIGN_DATABASE + 'Tantigen_rna_seq.csv')

    merged_df = pd.merge(tantigendb_se_df, tantigen_rna_seq_df, how='outer', on=['AgACC'])
    merged_df['Antigen Name_x'] = merged_df['Antigen Name_x'].combine_first(merged_df['Antigen Name_y'])
    merged_df = merged_df.drop(columns=['Antigen Name_y'])
    merged_df.rename(columns={'Antigen Name_x': 'Antigen Name'}, inplace=True)
    merged_df = merged_df.to_numpy()

    for l in merged_df:
        tantigen.objects.create(
            agacc=l[0],
            antigen_name=l[1],
            full_name=l[2],
            synonym=l[3],
            uniprot_id=l[4],
            href1=l[5],
            ncbi_gene_id=l[6],
            href2=l[7],
            gene_card_id=l[8],
            href3=l[9],
            rna_or_protein_expression_profile=l[10],
            href4=l[11],
            antigen_sequence=l[12],
            seq_5=l[13],
            cds=l[14],
            seq_3=l[15],
        )

if __name__ == "__main__":
    add_data()