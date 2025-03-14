import csv
import logging
import os

from Bio import SeqIO
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from isoform_expression.models import ExpressionRecord
from isoform_expression.serializers import ExpressionRecordSerializer
from isoform_sequences.models import isoform, gene
from isoform_samples.models import Samples

try:
    from mrnadesign_api import settings_local as local_settings
except ImportError:
    local_settings = None


# transcript seq visualization demo
class TranscriptViewer(APIView):
    FASTA_FILE = ('/mnt/d/projects_data/isoform/test_data/output/TCGA_BRCA/f48956a3-c821-429f-b1ad'
                  '-a27133d739bd/f48956a3-c821-429f-b1ad-a27133d739bd_stringTie.fasta')
    GFF3_FILE = ('/mnt/d/projects_data/isoform/test_data/output/TCGA_BRCA/f48956a3-c821-429f-b1ad'
                 '-a27133d739bd/f48956a3-c821-429f-b1ad-a27133d739bd_stringTie.fasta.transdecoder.gff3')

    def parse_gff3(self, transcript_id):
        features = {
            'five_prime_UTR': [],
            'CDS': [],
            'three_prime_UTR': []
        }
        with open(self.GFF3_FILE, 'r') as file:
            for line in file:
                if line.startswith('#'):
                    continue
                parts = line.strip().split('\t')
                if len(parts) < 9:
                    continue
                trans_id_str = parts[0]
                info = parts[8]
                if transcript_id == trans_id_str or transcript_id in trans_id_str:
                    feature_type = parts[2]
                    if feature_type in ['five_prime_UTR', 'CDS', 'three_prime_UTR']:
                        start = int(parts[3])
                        end = int(parts[4])
                        features[feature_type].append({'start': start, 'end': end})
        return features

    def get(self, request, *args, **kwargs):
        transcript_id = request.GET.get('transcript_id')
        if not transcript_id:
            return Response({'error': 'Missing transcript ID'}, status=400)

        sequence = ''
        for record in SeqIO.parse(self.FASTA_FILE, "fasta"):
            if record.id == transcript_id:
                sequence = str(record.seq)
                break

        if not sequence:
            return Response({'error': 'Transcript not found'}, status=404)

        features = self.parse_gff3(transcript_id)

        return Response({
            'sequence': sequence,
            'features': features
        })


class TranscriptViewerV2(APIView):
    FASTA_FILE = ('/mnt/d/projects_data/isoform/test_data/output/TCGA_BRCA/f48956a3-c821-429f-b1ad'
                  '-a27133d739bd/f48956a3-c821-429f-b1ad-a27133d739bd_stringTie.fasta')
    GFF3_FILE = ('/mnt/d/projects_data/isoform/test_data/output/TCGA_BRCA/f48956a3-c821-429f-b1ad'
                 '-a27133d739bd/f48956a3-c821-429f-b1ad-a27133d739bd_stringTie.fasta.transdecoder.gff3')

    def parse_gff3(self, transcript_id):
        featuresList = []
        current_features = None

        with open(self.GFF3_FILE, 'r') as file:
            for line in file:
                if line.startswith('#'):
                    continue
                parts = line.strip().split('\t')
                if len(parts) < 9:
                    continue
                trans_id_str = parts[0]
                info = parts[8]
                if transcript_id == trans_id_str or transcript_id in trans_id_str:
                    feature_type = parts[2]
                    if feature_type == 'mRNA':
                        if current_features:
                            featuresList.append(current_features)
                        current_features = {'info': info, 'mRNA': [], 'five_prime_UTR': [], 'CDS': [],
                                            'three_prime_UTR': []}
                    elif feature_type in ['five_prime_UTR', 'CDS', 'three_prime_UTR'] and current_features:
                        start = int(parts[3])
                        end = int(parts[4])
                        current_features[feature_type].append({'start': start, 'end': end})

        if current_features:
            featuresList.append(current_features)

        return featuresList

    def get(self, request, *args, **kwargs):
        transcript_id = request.GET.get('transcript_id')
        if not transcript_id:
            return Response({'error': 'Missing transcript ID'}, status=400)

        sequence = ''
        for record in SeqIO.parse(self.FASTA_FILE, "fasta"):
            if record.id == transcript_id:
                sequence = str(record.seq)
                break

        if not sequence:
            return Response({'error': 'Transcript not found'}, status=404)

        featuresList = self.parse_gff3(transcript_id)

        return Response({
            'sequence': sequence,
            'featuresList': featuresList
        })

class GenomeDataView(APIView):
    def get(self, request):
        gene_id_param = request.query_params.get('gene_id')
        if not gene_id_param:
            return Response({"error": "gene_id parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        file_path = '/mnt/d/projects_data/isoform/test_data/output/TCGA_BRCA/f48956a3-c821-429f-b1ad-a27133d739bd/f48956a3-c821-429f-b1ad-a27133d739bd_stringTie_EE.gtf'
        express_path = '/mnt/d/projects_data/isoform/test_data/output/TCGA_BRCA/f48956a3-c821-429f-b1ad-a27133d739bd/transcript_count_matrix.csv'  # 新增的表达量文件路径

        if not os.path.exists(file_path):
            return Response({"error": "File not found."}, status=status.HTTP_404_NOT_FOUND)

        # 读取表达量文件并创建一个字典来映射 transcript_id 到 expression_count
        expression_data = {}
        if os.path.exists(express_path):
            with open(express_path, 'r') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # 跳过首行列名
                for row in reader:
                    if len(row) >= 2:
                        expression_data[row[0]] = row[1]

        genome_data_list = []
        with open(file_path, 'r') as file:
            for line in file:
                if line.startswith('#'):
                    continue
                parts = line.strip().split('\t')
                if len(parts) < 9:
                    continue

                chrom, feature_type, start, end, strand, attributes = parts[0], parts[2], int(parts[3]), int(parts[4]), \
                    parts[6], parts[8]
                attr_dict = {}
                for attr in attributes.split(';'):
                    attr = attr.strip()
                    if attr:
                        key_value = attr.split(' ')
                        if len(key_value) == 2:
                            key, value = key_value[0], key_value[1].strip('"')
                            attr_dict[key] = value

                if attr_dict.get('cov') == "0.0":
                    continue
                if attr_dict.get('gene_id') == gene_id_param or attr_dict.get('ref_gene_id') == gene_id_param:
                    genome_data = {
                        "chrom": chrom,
                        "start": start,
                        "end": end,
                        "type": feature_type,
                        "gene_id": attr_dict.get('gene_id', ''),
                        "trans_id": attr_dict.get('transcript_id', ''),
                        "exon_num": attr_dict.get('exon_number', '') if feature_type == 'exon' else None,
                        "expression_count": None,
                        "strand": strand
                    }
                    if feature_type == 'transcript' and genome_data["trans_id"] in expression_data:
                        genome_data["expression_count"] = expression_data[genome_data["trans_id"]]
                    genome_data_list.append(genome_data)

        return Response(genome_data_list, status=status.HTTP_200_OK)


class isoformdbExpressionSearchViewSet(APIView):
    def get(self, request):
        query_dict = request.query_params.dict()
        gene_id = query_dict.get('gene_id')
        transcript_id = query_dict.get('transcript_id')
        sample_id = query_dict.get('sample_id')
        if gene_id:
            expression_records = ExpressionRecord.objects.filter(gene_id=gene_id)
        elif transcript_id:
            expression_records = ExpressionRecord.objects.filter(transcript_id=transcript_id)
        elif sample_id:
            expression_records = ExpressionRecord.objects.filter(sample_id=sample_id)
        else:
            return Response("Related expression records not found!", status=404)
        serializer = ExpressionRecordSerializer(expression_records, many=True)
        return Response(serializer.data)


class ExpressionRecordCreateView(APIView):
    def post(self, request):
        data = request.data
        gene_id_str = data.get('gene_id')
        transcript_id_str = data.get('transcript_id')
        sample_id_str = data.get('sample_id')
        if not isoform.objects.filter(isoform_id=transcript_id_str).exists():
            return Response({'error': f'Transcript {transcript_id_str} not found.'}, status=404)
        if not Samples.objects.filter(name=sample_id_str).exists():
            return Response({'error': f'Sample {sample_id_str} not found.'}, status=404)
        transcript_rec = isoform.objects.get(isoform_id=transcript_id_str)
        gene_rec = gene.objects.get(gene_id=transcript_rec.gene_id)
        sample_rec = Samples.objects.get(name=sample_id_str)
        if ExpressionRecord.objects.filter(transcript_id=transcript_rec.id, sample_id=sample_rec.id).exists():
            return Response({
                'conflict': f'Expression record already exists. Sample id = {sample_rec.name}, transcript id = {transcript_rec.isoform_id}'},
                status=409)
        data['gene_id'] = gene_rec.id
        data['gene_id_str'] = gene_rec.gene_id
        data['transcript_id'] = transcript_rec.id
        data['transcript_id_str'] = transcript_rec.isoform_id
        data['sample_id'] = sample_rec.id
        data['sample_id_str'] = sample_rec.name
        serializer = ExpressionRecordSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class ExpressionRecordBulkCreateView(APIView):
    def post(self, request):
        data = request.data.get('data', [])  # 获取批量数据，假设请求体包含一个 'data' 列表字段
        if not isinstance(data, list) or not data:
            return Response({'error': 'Invalid or empty data. Expected a list of records.'}, status=400)

        # 批量校验和处理数据
        validated_records = []
        errors = []
        warns = []

        for idx, record in enumerate(data):
            gene_id_str = record.get('gene_id')
            transcript_id_str = record.get('transcript_id')
            sample_id_str = record.get('sample_id')

            # 校验 transcript 是否存在
            transcript_rec = isoform.objects.filter(isoform_id=transcript_id_str).first()
            if not transcript_rec:
                logging.warning(f"Transcript {transcript_id_str} not found.")
                continue

            # 校验 sample 是否存在
            sample_rec = Samples.objects.filter(name=sample_id_str).first()
            if not sample_rec:
                logging.error(f"Sample {sample_id_str} not found.")
                errors.append({'index': idx, 'error': f'Sample {sample_id_str} not found.'})
                continue

            # 获取 gene 信息（从 transcript 关联的 gene_id 获取）
            gene_rec = gene.objects.filter(gene_id=transcript_rec.gene_id).first()
            if not gene_rec:
                logging.warning(f"gene record {gene_id_str} not found for transcript {transcript_id_str}.")
                continue

            # 检查是否已存在相同的记录
            if ExpressionRecord.objects.filter(transcript_id=transcript_rec.id, sample_id=sample_rec.id).exists():
                logging.warning(
                    f"index = {idx}, conflict: Expression record already exists. Sample id = {sample_rec.name}, transcript id = {transcript_rec.isoform_id}")
                continue

            # 构造 validated record
            validated_records.append(ExpressionRecord(
                gene_id=gene_rec.id,
                transcript_id=transcript_rec.id,
                sample_id=sample_rec.id,
                gene_id_str=gene_rec.gene_id,
                transcript_id_str=transcript_rec.isoform_id,
                sample_id_str=sample_rec.name,
                cov=record.get('cov', 0),
                fpkm=record.get('fpkm', 0),
                tpm=record.get('tpm', 0)
            ))

        # 如果存在任何错误，返回错误信息
        if errors:
            return Response({'errors': errors, 'valid_count': len(validated_records)}, status=400)

        # 批量插入 validated_records
        try:
            ExpressionRecord.objects.bulk_create(validated_records)
            return Response({'message': f'Successfully inserted {len(validated_records)} records.'}, status=201)
        except Exception as e:
            logging.error(f'Failed to bulk insert records: {str(e)}')
            return Response({'error': f'Failed to bulk insert records: {str(e)}'}, status=500)


# todo: here is a test demo view, remember to remove it
class GeneExpressionCsvView(APIView):
    """
    A Django view to read gene expression data from a server-side CSV file
    and return it as JSON.
    """

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests to fetch gene expression data from the CSV file.
        """
        try:
            # 打开 CSV 文件
            with open(local_settings.EXPRESSIONCSV, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)

                # 获取表头的样本 ID（除 gene_id）
                if 'gene_id' not in csv_reader.fieldnames:
                    return Response({'error': 'Missing "gene_id" column in the CSV file'}, status=400)

                sample_ids = [col for col in csv_reader.fieldnames if col != 'gene_id']

                # 解析数据
                data = []
                for row in csv_reader:
                    gene_id = row['gene_id']
                    sample_expression_map = {sample_id: float(row[sample_id]) for sample_id in sample_ids}
                    data.append({'gene_id': gene_id, 'skin_part1': sample_expression_map, 'skin_part2': sample_expression_map})

                # 返回数据
                return Response(data[0], status=200)

        except FileNotFoundError:
            # 文件不存在错误
            return Response({'error': f'CSV file not found at {local_settings.EXPRESSIONCSV}'}, status=404)

        except Exception as e:
            # 捕获其他异常
            return Response({'error': 'Failed to process the CSV file', 'details': str(e)}, status=500)

class HeatmapDataView(APIView):
    """
    A Django class-based view to read a CSV file containing transcript expression data
    and return JSON for use in a heatmap visualization in Vue + D3.js.
    """

    def get(self, request, *args, **kwargs):
        # Define the path to the CSV file (adjust the path as necessary)
        csv_file_path = os.path.join(local_settings.CSVDIR, "mock_trans_skin_1_10_samples.csv")

        # Check if the file exists
        if not os.path.exists(csv_file_path):
            return Response({"error": "CSV file not found"}, status=404)

        # Initialize storage for the heatmap data
        heatmap_data = []

        try:
            # Open and read the CSV file
            with open(csv_file_path, mode="r", encoding="utf-8") as csv_file:
                reader = csv.DictReader(csv_file)  # Use DictReader to handle headers automatically

                # Extract rows and prepare data
                for row in reader:
                    # Each row should contain a transcript_id and sample values
                    transcript_id = row.get("transcript_id")
                    for sample_id, expression_value in row.items():
                        if sample_id != "transcript_id":  # Skip the 'transcript_id' column
                            heatmap_data.append({
                                "transcript_id": transcript_id,
                                "sample_id": sample_id,
                                "expression_value": float(expression_value) if expression_value else 0.0,
                            })

            # Return the data as JSON
            return Response({"data": heatmap_data}, status=200)

        except Exception as e:
            # Handle any errors that occur during file reading or parsing
            return Response({"error": str(e)}, status=500)