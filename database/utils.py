import os
import requests

def esm_fold_cif_api(sequence):
    api_url = 'https://api.esmatlas.com/foldSequence/v1/cif/'
    x = requests.post(api_url, data = sequence[:399], verify=False)
    
    return x.text