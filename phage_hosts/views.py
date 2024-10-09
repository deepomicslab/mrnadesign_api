from rest_framework import viewsets
from phage_hosts.models import phage_hosts
from phage_hosts.models import phage_hostnode
from phage_hosts.serializers import phage_hostsSerializer
from phage_hosts.serializers import phage_hostnodeSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
import json


class MyPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'pagesize'


class phage_hostsViewSet(viewsets.ModelViewSet):
    queryset = phage_hosts.objects.all()
    serializer_class = phage_hostsSerializer


class phage_hostnodeViewSet(viewsets.ModelViewSet):
    queryset = phage_hostnode.objects.all()
    serializer_class = phage_hostnodeSerializer


class phage_hosts_nodeView(APIView):

    def get(self, request, *args, **kwargs):
        querydict = request.query_params.dict()

        if querydict.get('rank') is not None:
            rank = querydict['rank']
            tree = []
            if querydict.get('node') is not None:
                node = querydict['node']
                queryset = phage_hostnode.objects.filter(
                    rank=rank, parent=node)
            else:
                queryset = phage_hostnode.objects.filter(rank=rank)
            serializer = phage_hostnodeSerializer(queryset, many=True)
            for i in serializer.data:
                treenode = {}
                # treenode['label'] = i['node']+'('+str(i['phagecount'])+')'
                treenode['label'] = i['node']
                treenode['count'] = i['phagecount']
                treenode['rank'] = i['rank']
                tree.append(treenode)
        return Response(tree)


class phage_hostsView(APIView):
    def get(self, request, *args, **kwargs):
        hosts = request.query_params.dict()['host']
        if hosts == 'Others':
            excluded_values = ['Synergistota', 'Cyanobacteriota', 'Fusobacteriota','Verrucomicrobiota','Pseudomonadota','Bacillota','Campylobacterota']
            phages = phage_hosts.objects.exclude(Phylum=excluded_values)
        else:
            rank = request.query_params.dict()['rank']
            if rank == 'Phylum':
                phages = phage_hosts.objects.filter(Phylum=hosts)
            elif rank == 'Class':
                phages = phage_hosts.objects.filter(Class=hosts)
            elif rank == 'Order':
                phages = phage_hosts.objects.filter(Order=hosts)
            elif rank == 'Family':
                phages = phage_hosts.objects.filter(Family=hosts)
            elif rank == 'Genus':
                phages = phage_hosts.objects.filter(Genus=hosts)
            elif rank == 'Species':
                phages = phage_hosts.objects.filter(Species=hosts)
            else:
                phages = phage_hosts.objects.filter(host=hosts)
        paginator = MyPagination()
        paginated_phages = paginator.paginate_queryset(
                phages, request, view=self)
        serializer = phage_hostsSerializer(paginated_phages, many=True)
        return paginator.get_paginated_response(serializer.data)


class phage_hostsfilterView(APIView):
    def post(self, request, *args, **kwargs):
        hostjson = json.loads(request.data['hosts'])
        total_qs = phage_hosts.objects.none()
        for checkednode in hostjson:
            hosts = checkednode['label']
            rank = checkednode['rank']
            if rank == 'Phylum':
                qs = phage_hosts.objects.filter(Phylum=hosts)
            elif rank == 'Class':
                qs = phage_hosts.objects.filter(Class=hosts)
            elif rank == 'Order':
                qs = phage_hosts.objects.filter(Order=hosts)
            elif rank == 'Family':
                qs = phage_hosts.objects.filter(Family=hosts)
            elif rank == 'Genus':
                qs = phage_hosts.objects.filter(Genus=hosts)
            elif rank == 'Species':
                qs = phage_hosts.objects.filter(Species=hosts)
            total_qs = qs | total_qs

        paginator = MyPagination()
        paginated_phages = paginator.paginate_queryset(
            total_qs, request, view=self)
        serializer = phage_hostsSerializer(paginated_phages, many=True)
        return paginator.get_paginated_response(serializer.data)
