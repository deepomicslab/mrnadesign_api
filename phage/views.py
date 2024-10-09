from io import BytesIO
from rest_framework import viewsets
from rest_framework.views import APIView
from phage.models import phage
from phage.serializers import phageSerializer
from phage_clusters.models import phage_clusters
from phage_subcluster.models import phage_subcluster
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from phage_hosts.models import phage_hosts
from phage_lifestyle.models import phage_lifestyle
import json
from django.db.models import Q
from Phage_api import settings_local as local_settings
from django.http import FileResponse
from rest_framework.decorators import api_view
from phage_protein.serializers import phage_crispr_Serializer
from phage_protein.models import phage_crispr
import pandas as pd
import random
from datasets.models import datasets
class LargeResultsSetPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'pagesize'
    max_page_size = 10000


class phageViewSet(viewsets.ModelViewSet):

    queryset = phage.objects.order_by('display_id')
    serializer_class = phageSerializer
    pagination_class = LargeResultsSetPagination

    def get(self, request):
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(self.queryset, request)
        serializer = phageSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class phage_crisprViewSet(viewsets.ModelViewSet):
    queryset = phage_crispr.objects.order_by('id')
    serializer_class = phage_crispr_Serializer
    pagination_class = LargeResultsSetPagination

# ['Genbank', 'RefSeq', 'DDBJ', 'EMBL', 'tpg', 'PhagesDB', 'GPD', 'GVD', 'MGV', 'TemPhD','CHVD','IGVD','IMG VR','GOV2','STV',]


class phage_NCBIViewSet(viewsets.ModelViewSet):
    queryset = phage.objects.filter(Data_Sets__id__in=[1, 2, 3, 4, 5])
    serializer_class = phageSerializer
    pagination_class = LargeResultsSetPagination


class phage_GenbankViewSet(viewsets.ModelViewSet):
    queryset = phage.objects.filter(Data_Sets__id=1)
    serializer_class = phageSerializer
    pagination_class = LargeResultsSetPagination


class phage_RefSeqViewSet(viewsets.ModelViewSet):
    queryset = phage.objects.filter(Data_Sets__id=2)
    serializer_class = phageSerializer
    pagination_class = LargeResultsSetPagination


class phage_DDBJViewSet(viewsets.ModelViewSet):
    queryset = phage.objects.filter(Data_Sets__id=3)
    serializer_class = phageSerializer
    pagination_class = LargeResultsSetPagination


class phage_EMBLViewSet(viewsets.ModelViewSet):
    queryset = phage.objects.filter(Data_Sets__id=4)
    serializer_class = phageSerializer
    pagination_class = LargeResultsSetPagination


class phage_PhagesDBViewSet(viewsets.ModelViewSet):
    queryset = phage.objects.filter(Data_Sets__id=6)
    serializer_class = phageSerializer
    pagination_class = LargeResultsSetPagination


class phage_GPDViewSet(viewsets.ModelViewSet):
    queryset = phage.objects.filter(Data_Sets__id=7)
    serializer_class = phageSerializer
    pagination_class = LargeResultsSetPagination


class phage_GVDViewSet(viewsets.ModelViewSet):
    queryset = phage.objects.filter(Data_Sets__id=8)
    serializer_class = phageSerializer
    pagination_class = LargeResultsSetPagination


class phage_MGVViewSet(viewsets.ModelViewSet):
    queryset = phage.objects.filter(Data_Sets__id=9)
    serializer_class = phageSerializer
    pagination_class = LargeResultsSetPagination


class phage_TemPhDViewSet(viewsets.ModelViewSet):
    queryset = phage.objects.filter(Data_Sets__id=10)
    serializer_class = phageSerializer
    pagination_class = LargeResultsSetPagination

class phage_CHVDViewSet(viewsets.ModelViewSet):
    queryset = phage.objects.filter(Data_Sets__id=11)
    serializer_class = phageSerializer
    pagination_class = LargeResultsSetPagination

class phage_IGVDViewSet(viewsets.ModelViewSet):
    queryset = phage.objects.filter(Data_Sets__id=12)
    serializer_class = phageSerializer
    pagination_class = LargeResultsSetPagination

class phage_IMG_VRViewSet(viewsets.ModelViewSet):
    queryset = phage.objects.filter(Data_Sets__id=13)
    serializer_class = phageSerializer
    pagination_class = LargeResultsSetPagination

class phage_GOV2ViewSet(viewsets.ModelViewSet):
    queryset = phage.objects.filter(Data_Sets__id=14)
    serializer_class = phageSerializer
    pagination_class = LargeResultsSetPagination

class phage_STVViewSet(viewsets.ModelViewSet):
    queryset = phage.objects.filter(Data_Sets__id=15)
    serializer_class = phageSerializer
    pagination_class = LargeResultsSetPagination
    

class phageView(APIView):
    def get(self, request, *args, **kwargs):
        querydict = request.query_params.dict()
        if 'id' in querydict:
            id = request.query_params.dict()['id']
            queryset = phage.objects.get(id=id)
        elif 'accid' in querydict:
            accid = request.query_params.dict()['accid']
            queryset = phage.objects.get(Acession_ID=accid)
        serializer = phageSerializer(queryset)
        return Response(serializer.data)


class phage_clusterView(APIView):
    def get(self, request, *args, **kwargs):
        clusterid = request.query_params.dict()['clusterid']
        phage_clusters_queryset = phage_clusters.objects.get(id=clusterid)
        phages = phage.objects.filter(cluster=phage_clusters_queryset.cluster)
        serializer = phageSerializer(phages, many=True)
        return Response(serializer.data)


class phage_subclusterView(APIView):
    def get(self, request, *args, **kwargs):
        subclusterid = request.query_params.dict()['subclusterid']
        phage_subcluster_queryset = phage_subcluster.objects.get(
            id=subclusterid)
        phages = phage.objects.filter(
            subcluster=phage_subcluster_queryset.subcluster)
        serializer = phageSerializer(phages, many=True)
        return Response(serializer.data)


class phage_filterView(APIView):
    def post(self, request, *args, **kwargs):
        filterdatajson = json.loads(request.data['filterdata'])
        q_expression = Q()
        if filterdatajson['HostType'] != '':
            host = filterdatajson['HostType']
            qs = phage_hosts.objects.filter(Phylum=host)
            q_expression &= Q(phage_hosts__in=qs)
        if filterdatajson['cluster'] != '':
            cluster = filterdatajson['cluster']
            q_expression &= Q(cluster=cluster)
        if filterdatajson['subcluster'] != '':
            subcluster = filterdatajson['subcluster']
            q_expression &= Q(subcluster=subcluster)
        if filterdatajson['quality'] != '':
            quality = filterdatajson['quality']
            q_expression &= Q(completeness__exact=quality)
        if filterdatajson['datasets'] != []:
            datasetslist = filterdatajson['datasets']
            sets = []
            for dataset in datasetslist:
                ds = datasets.objects.get(name=dataset)
                sets.append(ds.id)
            q_expression &= Q(Data_Sets__in=sets)
        if filterdatajson['lifestyle'] != '' and filterdatajson['lifestyle'] != 'all':
            lifestyle = filterdatajson['lifestyle']
            qs = phage_lifestyle.objects.filter(lifestyle=lifestyle)
            q_expression &= Q(phage_lifestyle__in=qs)
        if filterdatajson['Taxonomy'] != '':
            taxonomy = filterdatajson['Taxonomy']
            q_expression &= Q(taxonomy=taxonomy)
        total_queryset = phage.objects.filter(q_expression)
        paginator = LargeResultsSetPagination()
        paginated_phages = paginator.paginate_queryset(
            total_queryset, request, view=self)
        serializer = phageSerializer(paginated_phages, many=True)
        return paginator.get_paginated_response(serializer.data)





class phage_searchView(APIView):
    def get(self, request, *args, **kwargs):
        searchstr = request.query_params.dict()['search']
        q_expression = Q()
        q_expression |= Q(Acession_ID__icontains=searchstr)
        q_expression |= Q(taxonomy__icontains=searchstr)
        q_expression |= Q(host__icontains=searchstr)
        q_expression |= Q(completeness__icontains=searchstr)
        q_expression |= Q(cluster__icontains=searchstr)
        q_expression |= Q(subcluster__icontains=searchstr)
        qs = phage_lifestyle.objects.filter(lifestyle__icontains=searchstr)
        q_expression |= Q(phage_lifestyle__in=qs)
        total_queryset = phage.objects.filter(q_expression)
        paginator = LargeResultsSetPagination()
        paginated_phages = paginator.paginate_queryset(
            total_queryset, request, view=self)
        serializer = phageSerializer(paginated_phages, many=True)
        return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
def getfasta(request):
    querydict = request.query_params.dict()
    if 'phageid' in querydict:
        phageid = querydict['phageid']
        phage_obj = phage.objects.get(id=phageid)
        phagedata = phageSerializer(phage_obj).data
        pathlist = [phagedata['fastapath']]
    elif 'phageids' in querydict:
        phageids = querydict['phageids']
        phageids = phageids.split(',')
        phage_obj = phage.objects.filter(id__in=phageids)
        phagedatas = phageSerializer(phage_obj, many=True).data
        pathlist = []
        for phagedata in phagedatas:
            pathlist.append(phagedata['fastapath'])
    else:
        pathlist = [
            '/home/platform/phage_db/phage_api/workspace/rawd_data/phage/all_sequence_v1.fasta']
        file = open('/home/platform/phage_db/phage_data/data/phage_sequence/phage_fasta/All_fasta.tar.gz', 'rb')
        response = FileResponse(file)
        filename = file.name.split('/')[-1]
        response['Content-Disposition'] = "attachment; filename="+filename
        response['Content-Type'] = 'application/x-gzip'
        return response
        

    content = ''
    for path in pathlist:
        with open(path, 'r') as file:
            content = content+file.read()
    content_bytes = content.encode('utf-8')
    buffer = BytesIO(content_bytes)
    response = response = FileResponse(buffer)
    response['Content-Disposition'] = 'attachment; filename="sequence.fasta"'
    response['Content-Type'] = 'text/plain'
    return response






@api_view(['GET'])
def getgbk(request):
    querydict = request.query_params.dict()
    if 'phageid' in querydict:
        phageid = querydict['phageid']
        phage_obj = phage.objects.get(id=phageid)
        phagedata = phageSerializer(phage_obj).data
        pathlist = [phagedata['gbkpath']]
    elif 'phageids' in querydict:
        phageids = querydict['phageids']
        phageids = phageids.split(',')
        phage_obj = phage.objects.filter(id__in=phageids)
        phagedatas = phageSerializer(phage_obj, many=True).data
        pathlist = []
        for phagedata in phagedatas:
            pathlist.append(phagedata['gbkpath'])
    else:
        pathlist = [
            '/home/platform/phage_db/phage_data/data/phage_sequence/phage_gbk/All.gbk']
        file = open('/home/platform/phage_db/phage_data/data/phage_sequence/phage_gbk/All.gbk', 'rb')
        response = FileResponse(file)
        filename = file.name.split('/')[-1]
        response['Content-Disposition'] = "attachment; filename="+filename
        response['Content-Type'] = 'text/plain'
        return response
    content = ''
    for path in pathlist:
        with open(path, 'r') as file:
            content = content+file.read()
    content_bytes = content.encode('utf-8')
    buffer = BytesIO(content_bytes)
    response = response = FileResponse(buffer)
    response['Content-Disposition'] = 'attachment; filename="sequence.gbk"'
    response['Content-Type'] = 'text/plain'
    return response


@api_view(['GET'])
def getgff(request):
    querydict = request.query_params.dict()
    if 'phageid' in querydict:
        phageid = querydict['phageid']
        phage_obj = phage.objects.get(id=phageid)
        phagedata = phageSerializer(phage_obj).data
        pathlist = [phagedata['gffpath']]
    elif 'phageids' in querydict:
        phageids = querydict['phageids']
        phageids = phageids.split(',')
        phage_obj = phage.objects.filter(id__in=phageids)
        phagedatas = phageSerializer(phage_obj, many=True).data
        pathlist = []
        for phagedata in phagedatas:
            pathlist.append(phagedata['gffpath'])
    else:
        pathlist = [
            '/home/platform/phage_db/phage_data/data/phage_sequence/phage_gff3/All.gff3']
        file = open('/home/platform/phage_db/phage_data/data/phage_sequence/phage_gff3/All.gff3', 'rb')
        response = FileResponse(file)
        filename = file.name.split('/')[-1]
        response['Content-Disposition'] = "attachment; filename="+filename
        response['Content-Type'] = 'text/plain'
        return response
    content = ''
    for path in pathlist:
        with open(path, 'r') as file:
            content = content+file.read()
    content_bytes = content.encode('utf-8')
    buffer = BytesIO(content_bytes)
    response = response = FileResponse(buffer)
    response['Content-Disposition'] = 'attachment; filename="sequence.gff3"'
    response['Content-Type'] = 'text/plain'
    return response   

@api_view(['GET'])
def getphagemeta(request):
    querydict = request.query_params.dict()
    if 'phageid' in querydict:
        phageid = querydict['phageid']
        phage_obj = phage.objects.get(id=phageid)
        phagedata = [phageSerializer(phage_obj).data]
    elif 'phageids' in querydict:
        phageids = querydict['phageids']
        phageids = phageids.split(',')
        phage_obj = phage.objects.filter(id__in=phageids)
        phagedata = phageSerializer(phage_obj, many=True).data
    else:
        file = open('/home/platform/phage_db/phage_api/workspace/csv_data/Download/Phage_meta_data/all_phage_meta_data.tsv', 'rb')
        response = FileResponse(file)
        filename = file.name.split('/')[-1]
        response['Content-Disposition'] = "attachment; filename="+filename
        response['Content-Type'] = 'text/plain'
        return response
    proteinmetadata = pd.DataFrame(phagedata)
    tmppath = local_settings.TEMPPATH + \
        str(random.randint(1000, 9999))+"_phagemetadata.tsv"
    proteinmetadata.to_csv(tmppath, sep="\t", index=False)
    file = open(tmppath, 'rb')
    response = FileResponse(file)
    response['Content-Disposition'] = 'attachment; filename="metadata.tsv"'
    response['Content-Type'] = 'text/plain'
    return response

@api_view(['GET'])
def downloadphagetmeta(request):
    querydict = request.query_params.dict()
    if 'source' in querydict:
        source = querydict['source']
        file = open(local_settings.METADATA+'phage.tsv', 'rb')
    else:
        file = open(local_settings.METADATA+'phage.tsv', 'rb')
    response = FileResponse(file)
    response['Content-Disposition'] = 'attachment; filename="phage.tsv"'
    response['Content-Type'] = 'text/plain'
    return response


@api_view(['GET'])
def download_phage_fasta(request):
    querydict = request.query_params.dict()
    if 'datasource' in querydict:
        source = querydict['datasource']
        file = open(local_settings.PHAGEFASTA+''+source+'.tar.gz', 'rb')
    else:
        file = open(local_settings.PHAGEFASTA+'Genbank.tar.gz', 'rb')
    response = FileResponse(file)
    filename = file.name.split('/')[-1]
    response['Content-Disposition'] = "attachment; filename="+filename
    response['Content-Type'] = 'application/x-gzip'
    return response


@api_view(['GET'])
def downloadbypaath(request, path):

    file_path = local_settings.METADATA + path
    file = open(file_path, 'rb')
    response = FileResponse(file)
    filename = file.name.split('/')[-1]
    response['Content-Disposition'] = "attachment; filename="+filename
    response['Content-Type'] = 'text/plain'
    return response


@api_view(['GET'])
def downloadbypaatfasta(request, path):
    file_path = local_settings.FASTAPATH + path
    file = open(file_path, 'rb')
    response = FileResponse(file)
    filename = file.name.split('/')[-1]
    response['Content-Disposition'] = "attachment; filename="+filename
    response['Content-Type'] = 'text/plain'
    return response
