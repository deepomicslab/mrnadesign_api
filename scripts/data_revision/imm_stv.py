import django
import os
import pandas as pd
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Phage_api.settings")

django.setup()

#['Phage_ID','Protein_ID','Length','PredictedTMHsNumber','ExpnumberofAAsinTMHs','Expnumberfirst60AAs','TotalprobofNin','POSSIBLENterm','Insidesource','Insidestart','Insidesource',
# 'TMhelixsource','TMhelixstart','TMhelixend','Outsidesource','Outsidestart','Outsideend']
def add_data():
    from phage_protein.models import phage_protein_tmhmm_IMG_VR,phage_protein_tmhmm_CHVD,phage_protein_tmhmm_IGVD,phage_protein_tmhmm_GOV2,phage_protein_tmhmm_STV
    path='/home/platform/phage_db/phage_data/data/csv_data/Download/Transmembrane_protein_meta_data/stv_phage_transmembrane_protein_meta_data.tsv'
    phage_protein_tmm = pd.read_csv(path, sep=',')
    print('load data')
    for row in phage_protein_tmm.itertuples():
        phage_protein_tmhmm_STV.objects.create(Phage_Acession_ID=row.Phage_ID, Length=row.Length, predictedTMHsNumber=row.PredictedTMHsNumber, ExpnumberofAAsinTMHs=row.ExpnumberofAAsinTMHs, 
                Expnumberfirst60AAs=row.ExpnumberofAAsinTMHs, TotalprobofNin=row.TotalprobofNin, POSSIBLENterm=row.POSSIBLENterm, insidesource=row.Insidesource, insidestart=row.Insidestart, insideend=row.Insideend, 
                TMhelixsource=row.TMhelixsource, TMhelixstart=row.TMhelixstart, TMhelixend=row.TMhelixend, outsidesource=row.Outsidesource, outsidestart=row.Outsidestart, outsideend=row.Outsideend, 
                Protein_id=row.Protein_ID)

add_data()
