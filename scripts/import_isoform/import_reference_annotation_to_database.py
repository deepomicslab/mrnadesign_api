import django
import os,json
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mrnadesign_api.settings")

django.setup()

from isoform_sequences.models import isoform, gene
from isoform_sequences.serializers import IsoformSerializer, GeneSerializer

import argparse
import requests
import logging
import pandas as pd
from datetime import datetime

# 设置日志
logging.basicConfig(filename="gtf_input.log", level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

def parse_gtf(file_path):
    """解析GTF文件, 提取转录本和外显子信息"""
    logging.info(f"开始读取GTF文件: {file_path}")
    df = pd.read_csv(file_path, sep='\t', comment='#', header=None, 
                     names=['seqname', 'source', 'feature', 'start', 'end', 'score', 'strand', 'frame', 'attributes'])
    logging.info("GTF文件读取完成, 开始解析属性信息。")
    
    # Apply parse_attributes to each row in the attributes column
    df['attributes_dict'] = df['attributes'].apply(parse_attributes)

    # Extract needed information from the attributes dictionary
    df['gene_id'] = df['attributes_dict'].apply(lambda x: x.get('gene_id'))
    df['gene_name'] = df['attributes_dict'].apply(lambda x: x.get('gene_name', x.get('gene')))
    df['transcript_id'] = df['attributes_dict'].apply(lambda x: x.get('transcript_id', ''))
    df['transcript_type'] = df['attributes_dict'].apply(lambda x: x.get('transcript_type', x.get('transcript_biotype')))

    # 提取gene记录
    genes = df[df['feature'] == 'gene']
    # 提取transcripts和exons
    transcripts = df[df['feature'] == 'transcript']
    exons = df[df['feature'] == 'exon']
    
    # 计算外显子数和接头位置
    exon_counts = exons.groupby('transcript_id').size().rename('exon_count')
    junction_positions = exons.groupby('transcript_id').apply(
        lambda x: ','.join(f"{row['start']}-{row['end']}" for index, row in x.iterrows())
    ).rename('junction_position')

    # 合并转录本信息与外显子统计
    transcripts = transcripts.set_index('transcript_id')
    transcripts = transcripts.join(exon_counts).join(junction_positions)

    logging.info("属性解析完成，转录本和外显子信息已合并。")
    
    return transcripts.reset_index(), genes.reset_index()

def post_gene(request_data):
    gene_id = request_data['gene_id']
    if gene.objects.filter(gene_id=gene_id).exists():
        logging.info(f"Gene {gene_id} already exists.")
        return
    serializer = GeneSerializer(data=request_data)
    if serializer.is_valid():
        serializer.save()
        return 
    logging.error(f"Failed to insert gene {gene_id}")

def post_isoform(request_data):
    isoform_id = request_data['isoform_id']
    if isoform.objects.filter(isoform_id=isoform_id).exists():
        logging.info(f"Isoform {isoform_id} already exists.")
        return
    gene_id = request_data.get('gene_id')
    gene_name = request_data.get('gene_name')
    if gene.objects.filter(gene_id=gene_id).exists():
        request_data['gene_related'] = True
    elif gene.objects.filter(gene_name=gene_name).exists():
        request_data['gene_related'] = True
        gene_id = gene.objects.get(gene_name=gene_name).gene_id
        request_data['gene_id'] = gene_id
    serializer = IsoformSerializer(data=request_data)
    if serializer.is_valid():
        serializer.save()
        return 
    logging.error(f"Failed to insert isoform {isoform_id}")

def add_data():

    gtf_file = '/home/platform/project/mrnadesign_platform/mrnadesign_api/workspace/isoform_ys/projects_data/reference/annotated_transcripts/merged/hg38.gencode.RefSeq.gtf'

    transcripts, genes = parse_gtf(gtf_file)

    # Post genes
    for _, gene in genes.iterrows():
        gene_data = {
            'gene_id': gene['gene_id'],
            'gene_name': gene['gene_name'],
            'chromosome': gene['seqname'],
            'start_pos': gene['start'],
            'end_pos': gene['end'],
            'strand': gene['strand'],
            'gene_type': gene['attributes_dict'].get('gene_type', gene['attributes_dict'].get('gene_biotype'))
        }
        post_gene(gene_data)
    logging.info(f"posting gene data finished, total count = {len(genes)}")

    # Post transcripts
    for _, transcript in transcripts.iterrows():
        transcript_data = {
            'isoform_id': transcript['transcript_id'],
            'gene_id': transcript['gene_id'],
            'gene_name': transcript['gene_name'],
            'chromosome': transcript['seqname'],
            'start_pos': transcript['start'],
            'end_pos': transcript['end'],
            'junction_position': transcript['junction_position'],
            'strand': transcript['strand'],
            'isoform_type': transcript['transcript_type'],
            'exon_count': transcript['exon_count'],
            'create_time': datetime.now().isoformat(),
            'update_time': datetime.now().isoformat()
        }
        post_isoform(transcript_data)
    logging.info(f"posting transcript data finished, total count = {len(transcripts)}")
