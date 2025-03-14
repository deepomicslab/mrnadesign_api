import django
import os,json
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mrnadesign_api.settings")

django.setup()

from isoform_datasets.models import Datasets
from isoform_samples.models import Samples
from isoform_datasets.serializers import DatasetsSerializer
from isoform_samples.serializers import SamplesSerializer

import pandas as pd
import numpy as np
import psycopg2
from psycopg2 import sql
import argparse
import os
import logging
from datetime import date
import requests

# Configure logging
logging.basicConfig(filename="load_meta.log", level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to read a tab-separated file into a DataFrame
def read_tab_separated_file(file_path):
    try:
        logging.info(f"Reading file: {file_path}")
        return pd.read_csv(file_path, sep='\t', header=0, encoding='utf-8')
    except Exception as e:
        logging.error(f"Error reading file {file_path}: {e}")
        raise

# Function to extract specific columns of interest from the DataFrame
def extract_columns_of_interest(df):
    columns_of_interest = [
        'SAMPID', 'SMTS', 'SMTSD', 'SMNABTCH', 
        'SMNABTCHT', 'SMNABTCHD', 'SMGEBTCHT', 'SMAFRZE'
    ]
    logging.info("Extracting columns of interest")
    return df[columns_of_interest]

# Function to filter the DataFrame by 'SMAFRZE' column with value 'RNASEQ'
def filter_by_smafrze(new_df):
    logging.info("Filtering DataFrame by SMAFRZE == 'RNASEQ'")
    return new_df[new_df['SMAFRZE'] == 'RNASEQ']

# Function to merge filtered DataFrame with annotation DataFrame
def merge_filtered_and_annotation(filtered_df, annotation_df):
    logging.info("Merging filtered DataFrame with annotations")
    merged_data = []

    # Iterate over annotation DataFrame rows
    for _, annotation_row in annotation_df.iterrows():
        subj_id = annotation_row['SUBJID']
        # Find matching rows in filtered DataFrame
        matching_rows = filtered_df[filtered_df['SAMPID'].str.contains(subj_id)]

        # Combine data from matching rows
        for _, filtered_row in matching_rows.iterrows():
            combined_row = filtered_row.to_dict()
            combined_row.update({
                'SUBJID': annotation_row['SUBJID'],
                'SEX': annotation_row['SEX'],
                'AGE': annotation_row['AGE'],
                'DTHHRDY': annotation_row['DTHHRDY']
            })
            merged_data.append(combined_row)

    return pd.DataFrame(merged_data)

def post_dataset(requests):
    name = requests['name'] # dataset name
    if Datasets.objects.filter(name=name).exists():
        queryset = Datasets.objects.get(name=name)
        serializer = DatasetsSerializer(queryset)
        return serializer.data['id']
    serializer = DatasetsSerializer(data=requests)
    if serializer.is_valid():
        serializer.save()
        return serializer.data['id']
    logging.error(f"Failed to insert dataset {name}")
    return None

def post_sample(requests):
    name = requests['name'] 
    if Samples.objects.filter(name=name).exists():
        queryset = Samples.objects.get(name=name)
        serializer = SamplesSerializer(queryset)
        return serializer.data['id']
    dataset_id = requests['dataset_id']
    dataset_name = requests['dataset_name']
    if not Datasets.objects.filter(id=dataset_id).exists():
        print(f'Dataset {dataset_name} not found, can not load related sample')
        return None
    serializer = SamplesSerializer(data=requests)
    if serializer.is_valid():
        serializer.save()
        return serializer.data['id']
    logging.error(f"Failed to insert sample {name}")
    return None

def import_to_api(merged_df, platform):
    # Get current date
    current_date = date.today().isoformat()

    # Iterate over rows in merged DataFrame
    for _, row in merged_df.iterrows():
        age_range = row['AGE'].split("-")
        dataset_name = f'{platform}_{row["SMTS"]}'

        # Prepare dataset payload
        dataset_data = {
            'name': dataset_name,
            'database': platform,
            'data_type': row['SMAFRZE'],
            'submission_date': current_date,
            'last_update_date': current_date
        }

        # Post dataset data
        dataset_id = post_dataset(requests=dataset_data)

        # Prepare sample payload
        sample_data = {
            'name': row['SAMPID'],
            'tissue_type': row['SMTS'],
            'tissue_type_detail': row['SMTSD'],
            'subject_id': row['SUBJID'],
            'gender': row['SEX'],
            'min_age': int(age_range[0]),
            'max_age': int(age_range[1]),
            'death_circumstances': (None if (np.isnan(row['DTHHRDY']) or np.isinf(row['DTHHRDY'])) else row['DTHHRDY']),
            'dataset_id': dataset_id,
            'dataset_name': dataset_name,
        }

        # Post sample data
        sample_id = post_sample(requests=sample_data)


def add_data():
    file1_path = '/home/platform/project/mrnadesign_platform/mrnadesign_api/workspace/mrnadesign_database/isoform_db/raw/gtex/GTEx_Analysis_v8_Annotations_SampleAttributesDS.txt'
    file2_path = '/home/platform/project/mrnadesign_platform/mrnadesign_api/workspace/mrnadesign_database/isoform_db/raw/gtex/GTEx_Analysis_v8_Annotations_SubjectPhenotypesDS.txt'
    platform = 'gtex'

    # Read and process the first file
    df1 = read_tab_separated_file(file1_path)
    new_df = extract_columns_of_interest(df1)
    filtered_df = filter_by_smafrze(new_df)

    # Read the second file
    annotation_df = read_tab_separated_file(file2_path)

    # Merge DataFrames
    merged_df = merge_filtered_and_annotation(filtered_df, annotation_df)
    logging.info("Merged DataFrame created")
    logging.info(merged_df)

    # Import merged data into PostgreSQL
    import_to_api(merged_df, platform)