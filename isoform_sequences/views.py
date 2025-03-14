import os
import re
import json

from django.http import HttpResponse, FileResponse, StreamingHttpResponse
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from mrnadesign_api import settings_local as local_settings

from isoform_sequences.models import isoform, gene
from isoform_sequences.serializers import IsoformSerializer, GeneSerializer


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'pagesize'
    max_page_size = 10000

class isoformdbGenesViewSet(APIView):
    queryset = gene.objects.order_by('id')
    serializer_class = GeneSerializer
    pagination_class = LargeResultsSetPagination

    def get(self, request):
        querydict = request.query_params.dict()
        
        queryset = self.queryset
        
        if 'sorter' in querydict and querydict['sorter'] != '':
            sorterjson = json.loads(querydict['sorter'])
            order = sorterjson['order']
            columnKey = sorterjson['columnKey']
            if order == False:
                queryset = queryset.order_by('id')
            elif order == 'ascend':
                queryset = queryset.order_by(columnKey)
            else:  # 'descend
                queryset = queryset.order_by('-'+columnKey)

        if 'filter' in querydict and querydict['filter'] != '':
            filter = json.loads(querydict['filter'])
            q_expression = Q()
            for k, v in filter.items():
                if v:
                    q_expression &= Q(**{k + '__in': v})
            queryset = queryset.filter(q_expression)

        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = GeneSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

class isoformdbIsoformsViewSet(APIView):
    queryset = isoform.objects.order_by('id')
    serializer_class = IsoformSerializer
    pagination_class = LargeResultsSetPagination

    def get(self, request):
        querydict = request.query_params.dict()
        
        queryset = self.queryset
        
        if 'sorter' in querydict and querydict['sorter'] != '':
            sorterjson = json.loads(querydict['sorter'])
            order = sorterjson['order']
            columnKey = sorterjson['columnKey']
            if order == False:
                queryset = queryset.order_by('id')
            elif order == 'ascend':
                queryset = queryset.order_by(columnKey)
            else:  # 'descend
                queryset = queryset.order_by('-'+columnKey)

        if 'filter' in querydict and querydict['filter'] != '':
            filter = json.loads(querydict['filter'])
            q_expression = Q()
            for k, v in filter.items():
                if v:
                    q_expression &= Q(**{k + '__in': v})
            queryset = queryset.filter(q_expression)

        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = IsoformSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class isoformdbIsoformsDetailViewSet(APIView):
    def get(self, request, *args, **kwargs):
        querydict = request.query_params.dict()
        if 'id' in querydict:
            id = querydict['id']
            queryset = isoform.objects.get(id=id)
        serializer = IsoformSerializer(queryset)
        return Response(serializer.data)


class isoformdbIsoformsSequencesViewSet(APIView):
    def get(self, request, *args, **kwargs):
        querydict = request.query_params.dict()
        if 'id' in querydict:
            id = request.query_params.dict()['id']
            queryset = isoform.objects.get(id=id)
        else:
            return HttpResponse("Error: None id is not acceptable.", status=404)
        serializer = IsoformSerializer(queryset)
        try:
            with open(serializer.get_fasta_path(queryset), 'r') as file:
                data = file.read()
            return HttpResponse(data, content_type='text/plain')
        except IOError:
            print(f"Error: File not found. id = {id}")
            return HttpResponse("Error: File not found.", status=404)
        
class FileTrackView(APIView):
    def get(self, request, file_path, *args, **kwargs):
        # 规范化文件路径
        file_path = os.path.normpath(file_path)
        full_file_path = os.path.join(local_settings.JBROWSERDATADIR,
                                      file_path)
        if not os.path.exists(full_file_path):
            return HttpResponse("Error: File not found.", status=404)
        # 获取文件大小
        file_size = os.path.getsize(full_file_path)
        range_header = request.headers.get('Range', '').strip()
        range_match = re.match(r'bytes=(\d+)-(\d+)?', range_header)
        if range_match:
            # 处理 Range 请求
            first_byte, last_byte = range_match.groups()
            first_byte = int(first_byte)
            last_byte = int(last_byte) if last_byte else file_size - 1
            last_byte = min(last_byte, file_size - 1)
            length = last_byte - first_byte + 1
            with open(full_file_path, 'rb') as f:
                f.seek(first_byte)
                data = f.read(length)
            response = HttpResponse(data, status=206, content_type='application/octet-stream')
            response['Content-Range'] = f'bytes {first_byte}-{last_byte}/{file_size}'
        else:
            # 返回整个文件
            with open(full_file_path, 'rb') as f:
                data = f.read()
            response = HttpResponse(data, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename={os.path.basename(full_file_path)}'
        response['Accept-Ranges'] = 'bytes'
        response['Access-Control-Allow-Origin'] = '*' # Add CORS header
        response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
        response["Access-Control-Allow-Methods"] = "GET, HEAD"
        response["Access-Control-Max-Age"] = "3000"

        return response

# class FileTrackView(APIView):
#     def get(self, request, file_path, *args, **kwargs):
#         # 规范化文件路径
#         file_path = os.path.normpath(file_path)
#         full_file_path = os.path.join(local_settings.JBROWSERDATADIR, file_path)
#         if not os.path.exists(full_file_path):
#             return HttpResponse("Error: File not found.", status=404)
#         else:
#             # 获取文件大小
#             file_size = os.path.getsize(full_file_path)
#             range_header = request.headers.get('Range', '').strip()
#             range_match = re.match(r'bytes=(\d+)-(\d+)?', range_header)
#             if range_match:
#                 # 处理 Range 请求
#                 first_byte, last_byte = range_match.groups()
#                 first_byte = int(first_byte)
#                 last_byte = int(last_byte) if last_byte else file_size - 1
#                 last_byte = min(last_byte, file_size - 1)
#                 length = last_byte - first_byte + 1
#                 with open(full_file_path, 'rb') as f:
#                     f.seek(first_byte)
#                     data = f.read(length)
#                 response = HttpResponse(data, status=206, content_type='application/octet-stream')
#                 response['Content-Range'] = f'bytes {first_byte}-{last_byte}/{file_size}'
#             else:
#                 # 返回整个文件
#                 with open(full_file_path, 'rb') as f:
#                     data = f.read()
#                 response = HttpResponse(data, content_type='application/octet-stream')
        
#         response['Content-Disposition'] = f'attachment; filename={os.path.basename(full_file_path)}'
#         response['Access-Control-Allow-Origin'] = '*' # Add CORS header
#         response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"

#         response['Accept-Ranges'] = 'bytes'
#         response["Access-Control-Allow-Methods"] = "GET, HEAD"
#         response["Access-Control-Max-Age"] = "3000"

#         return response


# class IsoformCreateView(APIView):
#     def post(self, request, *args, **kwargs):
#         isoform_id = request.data.get('isoform_id')
#         if isoform.objects.filter(isoform_id=isoform_id).exists():
#             return Response({'error': 'Isoform already exists.'}, status=409)
#         gene_id = request.data.get('gene_id')
#         gene_name = request.data.get('gene_name')
#         if gene.objects.filter(gene_id=gene_id).exists():
#             request.data['gene_related'] = True
#         elif gene.objects.filter(gene_name=gene_name).exists():
#             request.data['gene_related'] = True
#             gene_id = gene.objects.get(gene_name=gene_name).gene_id
#             request.data['gene_id'] = gene_id
#         serializer = IsoformSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=201)
#         return Response(serializer.errors, status=400)


# class GeneCreateView(APIView):
#     def post(self, request, *args, **kwargs):
#         gene_id = request.data.get('gene_id')
#         if gene.objects.filter(gene_id=gene_id).exists():
#             return Response({'error': f'Gene {gene_id} already exists.'}, status=409)
#         serializer = GeneSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=201)
#         return Response(serializer.errors, status=400)
