import argparse
import requests
import logging

def setup_logging():
    logging.basicConfig(filename="bulk_load_sample_transcript_map.log", level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_arguments():
    parser = argparse.ArgumentParser(description='Process GTF files and store transcript data via Django API.')
    parser.add_argument('--file', type=str, help='Input txt file containing sample names and GTF file paths.')
    return parser.parse_args()

def parse_attributes(attributes):
    """Parse the attributes field from a GTF file into a dictionary."""
    attr_dict = {}
    attributes = attributes.strip(';').split(';')
    for attr in attributes:
        attr = attr.strip()
        if attr:
            first_space_index = attr.find(' ')
            key = attr[:first_space_index]
            value = attr[first_space_index:].strip().strip('"')
            if value:
                attr_dict[key] = value
    return attr_dict

def process_gtf_file(gtf_file_path):
    transcripts = []
    with open(gtf_file_path, 'r') as file:
        for line in file:
            if line.startswith('#'):
                continue
            fields = line.strip().split('\t')
            if fields[2] == 'transcript':
                attributes = parse_attributes(fields[8])
                transcript_id = attributes.get('reference_id', attributes.get('transcript_id'))
                gene_id = attributes.get('ref_gene_id', attributes.get('gene_id'))
                cov = attributes.get('cov')
                fpkm = attributes.get('FPKM')
                tpm = attributes.get('TPM')
                if transcript_id and gene_id:
                    transcripts.append((transcript_id, gene_id, cov, fpkm, tpm))
    logging.info(f'Processed {len(transcripts)} transcripts from {gtf_file_path}.')
    return transcripts

def store_transcripts_to_django_api(sample_name, transcripts):
    url = "http://localhost:8066/isoform/expression/create/"  # Replace with your Django API URL
    for transcript_id, gene_id in transcripts:
        data = {
            'sample_id': sample_name,
            'transcript_id': transcript_id,
            'gene_id': gene_id
        }
        response = requests.post(url, json=data)
        if response.status_code == 201:
            logging.info(f'Successfully stored {transcript_id} for {sample_name}.')
        else:
            logging.error(f'Failed to store {transcript_id} for {sample_name}. Request data is {data}, status code: {response.status_code}, response dataL {response.text}')

def bulk_store_transcripts_to_django_api(sample_name, transcripts):
    """Store transcript-gene pairs to the Django API in bulk."""
    url = "http://localhost:8066/isoform/expression/bulk_create/"  # Replace with your Django API bulk endpoint
    data = [
        {'sample_id': sample_name, 'transcript_id': transcript_id, 'gene_id': gene_id, 'cov': cov, 'fpkm': fpkm, 'tpm': tpm}
        for transcript_id, gene_id, cov, fpkm, tpm in transcripts
    ]
    response = requests.post(url, json={'data': data})  # Assuming the bulk endpoint accepts a key `data`
    if response.status_code == 201:
        logging.info(f'Successfully bulk stored {len(transcripts)} transcripts for {sample_name}.')
    else:
        logging.error(
            f'Failed to bulk store transcripts for {sample_name}. '
            f'Status code: {response.status_code}, response: {response.text}'
        )

def main():
    setup_logging()
    logging.info('Starting transcript processing.')
    args = parse_arguments()
    with open(args.file, 'r') as input_file:
        for line in input_file:
            sample_name, gtf_file_path = line.strip().split('\t')
            logging.info(f'Processing sample: {sample_name} with GTF file: {gtf_file_path}')
            transcripts = process_gtf_file(gtf_file_path)
            # store_transcripts_to_django_api(sample_name, transcripts)
            bulk_store_transcripts_to_django_api(sample_name, transcripts)
    logging.info('Finished processing all samples.')

if __name__ == '__main__':
    main()