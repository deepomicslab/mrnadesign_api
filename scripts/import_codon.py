import django
import os,json
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mrnadesign_api.settings")

django.setup()

from mrnadesign_api import settings_local as local_settings
import logging
logging.basicConfig(filename=local_settings.TASKLOG / "additional_scripts/02_import_data.log", level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def util(calculation_type):
    
    from codon.models import CodonPair
    from codon.serializers import CodonPairSerializer
    
    import pandas as pd
    import numpy as np

    dir = local_settings.MRNADESIGN_DATABASE + 'codon_pair/'
    df = pd.read_csv(dir + 'bicodon_' + calculation_type + '.csv', index_col=0)
    df.columns = [i.lower().replace(' - ', '_').replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_') for i in df.columns]
    dict = df.T.to_dict()
    
    for pair, tissuedata in dict.items():
        tissuedata['Dinucleotide'] = pair
        tissuedata['calculation_type'] = calculation_type
        if CodonPair.objects.filter(Dinucleotide = pair, calculation_type = calculation_type).exists():
            logging.info(f"CodonPair {pair}_{calculation_type} already exists")
            continue
        serializer = CodonPairSerializer(data = tissuedata)
        if serializer.is_valid():
            serializer.save()
            continue
        logging.error(f"Failed to insert CodonPair {pair}_{calculation_type}")
        logging.error(serializer.errors)

def add_data():
    for i in ['fraction', 'frequency', 'counts']:
        util(i)
    


if __name__ == "__main__":
    try:
        add_data()
    except Exception as e:
        logging.error(f"An error occurred: {e}")