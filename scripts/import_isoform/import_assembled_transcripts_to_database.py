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
    """解析GTF文件，提取转录本和外显子信息"""
    logging.info(f"开始读取GTF文件: {file_path}")
    df = pd.read_csv(file_path, sep='\t', comment='#', header=None, 
                     names=['seqname', 'source', 'feature', 'start', 'end', 'score', 'strand', 'frame', 'attributes'])
    logging.info("GTF文件读取完成，开始解析属性信息。")
    
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

def post_data(api_url, data):
    """发送数据到指定API端点"""
    try:
        response = requests.post(api_url, json=data)
        if response.status_code == 201:
            pass
            # logging.info("Data posted successfully!")
        else:
            logging.error(f"Failed to post data: {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error posting data: {e}")

def main():
    """主函数，处理命令行参数并调用API"""
    parser = argparse.ArgumentParser(description='Process GTF file and post data to Django API.')
    parser.add_argument('gtf_file', type=str, help='Path to the GTF file.')

    args = parser.parse_args()
    gene_api_url = 'http://localhost:8066/isoform/create_gene/'
    isoform_api_url = 'http://localhost:8066/isoform/create_isoform/'

    transcripts, genes = parse_gtf(args.gtf_file)

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
        # logging.info(f"Posting transcript data: {transcript_data}")
        post_data(isoform_api_url, transcript_data)
    logging.info(f"posting transcript data finished, total count = {len(transcripts)}")

if __name__ == '__main__':
    main()