from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from phage_clusters.models import phage_clusters
from phage_clusters.serializers import phage_clustersSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.views import APIView
from Phage_api import settings_local as local_settings
import os
from phage.models import phage
from phage.serializers import phageSerializer
import pandas as pd
from rest_framework.decorators import api_view
from phage_protein.models import phage_protein_NCBI, phage_protein_PhagesDB, phage_protein_GPD, phage_protein_MGV, phage_protein_TemPhD, phage_protein_GVD
from phage_protein.serializers import phage_protein_GPD_Serializer, phage_protein_GVD_Serializer, phage_protein_MGV_Serializer, phage_protein_NCBI_Serializer, phage_protein_PhagesDB_Serializer, phage_protein_TemPhD_Serializer
from django.http import FileResponse
from io import BytesIO
from utils import query

class phage_clustersViewSet(viewsets.ModelViewSet):
    queryset = phage_clusters.objects.order_by('-member')
    serializer_class = phage_clustersSerializer
    filter_backends = [filters.SearchFilter,
                       filters.OrderingFilter, DjangoFilterBackend]


class clusterView(APIView):
    def get(self, request, *args, **kwargs):

        query_dict = request.query_params.dict()
        if 'id' in query_dict:
            id = query_dict['id']
            cluster = phage_clusters.objects.filter(id=id)
        else:
            clusterid = query_dict['clusterid']
            cluster = phage_clusters.objects.filter(cluster=clusterid)

        serializer = phage_clustersSerializer(cluster, many=True)
        return Response(serializer.data[0])


class cluster_treeView(APIView):
    def get(self, request, *args, **kwargs):
        query_dict = request.query_params.dict()
        id = int(query_dict['id'])
        cluster = phage_clusters.objects.get(id=id)
        path = local_settings.CLUSTERTREEPATH + \
            cluster.cluster.replace('Cluster', 'group')+'/sequence.phy'

        if os.path.exists(path):
            file = open(path, 'r')
            data = file.read()
        else:
            data = ''
        return Response(data)

import random
class cluster_heatmapView(APIView):
    def get(self, request, *args, **kwargs):
        clusterid = request.query_params.dict()['clusterid']
        phage_clusters_queryset = phage_clusters.objects.get(id=clusterid)
        phages = phage.objects.filter(cluster=phage_clusters_queryset.cluster)
        countlist=[]
        for p in phages:
            coutdict={}
            coutdict['phage_id']=p.Acession_ID
            #countlist=[{'phage_id':'TemPhD_cluster_55397','hypothetical':0,'infection':3,'assembly':0,'replication':0,'packaging':0,'lysis':0,'regulation':0,'immune':0,'integration':0,'tRNA':0}]
            coutdict['lysis']=random.randint(0, 10)
            coutdict['integration']=random.randint(0, 10)
            coutdict['replication']=random.randint(0, 10)
            coutdict['tRNARelated']=random.randint(0, 10)
            coutdict['regulation']=random.randint(0, 10)
            coutdict['packaging']=random.randint(0, 10)
            coutdict['assembly']=random.randint(0, 10)
            coutdict['infection']=random.randint(0, 10)
            coutdict['immune']=random.randint(0, 10)
            coutdict['hypothetical']=random.randint(0, 10)
            countlist.append(coutdict)
        #    protein=getphageprotein(p)
        #    proteinlist.append(protein)

        return Response(countlist)


@api_view(['GET'])
def getfasta(request):

    querydict = request.query_params.dict()
    if 'clusterid' in querydict:
        clusterid = querydict['clusterid']
        phage_clusters_queryset = phage_clusters.objects.get(id=clusterid)
        clustername = str(phage_clusters_queryset.cluster)
        pathlist = [local_settings.CLUSTERSEQUENCEPATH+clustername.replace('Cluster','group')+'.fasta']
        filename=clustername+'.fasta'
    elif 'clusterids' in querydict:
        clusterids = querydict['clusterids']
        clusterids = clusterids.split(',')
        phage_clusters_objs = phage_clusters.objects.filter(id__in=clusterids)
        pathlist = []
        for phage_clusters_obj in phage_clusters_objs:
            clustername = str(phage_clusters_obj.cluster)
            pathlist.append(local_settings.CLUSTERSEQUENCEPATH+clustername.replace('Cluster','group')+'.fasta')
        filename='cluster.fasta'
    else:
        pathlist = [
            '/home/platform/phage_db/phage_api/workspace/rawd_data/phage/all_sequence_v1.fasta']
        filename='cluster.fasta'

    content = ''
    for path in pathlist:
        with open(path, 'r') as file:
            content = content+file.read()

    content_bytes = content.encode('utf-8')
    buffer = BytesIO(content_bytes)

    response = response = FileResponse(buffer)
    response['Content-Disposition'] = 'attachment; filename='+filename
    response['Content-Type'] = 'text/plain'
    return response
@api_view(['GET'])
def cluster_alignmentView(request):
    querydict = request.query_params.dict()
    if 'phageids' in request.query_params.dict() :
        phageids=request.query_params.dict()['phageids'].split(', ')
    else:
        phageids=None
    clusterid = querydict['id']
    cluster = phage_clusters.objects.get(id=clusterid)
    basepath = local_settings.CLUSTERALIGNMENTPATH + '/cluster/' +\
        cluster.cluster.replace('Cluster', 'cluster')
    sortlistpath=basepath+'/phage_list_sort.txt'
    aligncirclepath=basepath+'/comparison_link_circle.csv'
    sortedlist=[]
    order=1
    with open(sortlistpath, 'r') as f:
        sortedlistlines = f.readlines()
        for line in sortedlistlines:
            sortedlist.append({'order':order,'phage_id':line.strip()})
            order+=1

    circlealignments=pd.read_csv(aligncirclepath, sep=',', index_col=False,names=['id','Source_Phage_ID','Target_Phage_ID',
                                                                            'Source_start_point','Source_end_point','Source_strand',
                                                                            'Source_protein_id','Target_start_point','Target_end_point',
                                                                            'Target_strand','Target_protein_id','Identity','Coverage'                                                     
                                                                            ]).astype(str)
    #print(circlealignments)
    if phageids != None:
        circlealignments=circlealignments[circlealignments['Source_Phage_ID'].isin(phageids)]
        circlealignments=circlealignments[circlealignments['Target_Phage_ID'].isin(phageids)]
    else:
        sortedpid = [sorteddict['phage_id'] for sorteddict in sortedlist]
        phageids=sortedpid[:3]
        circlealignments=circlealignments[circlealignments['Source_Phage_ID'].isin(phageids)]
        circlealignments=circlealignments[circlealignments['Target_Phage_ID'].isin(phageids)]
    proteins=[]  
    for phageid in phageids:
        proteins=proteins+query.findphageprotein(phageAccId=phageid)
    result ={
            'sortedlist':sortedlist,
            'circlealignment':circlealignments.to_dict(orient='records'),
            'proteins':proteins
            }
    return Response({'results': result})