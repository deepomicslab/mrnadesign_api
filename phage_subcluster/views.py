from django.shortcuts import render
from rest_framework import viewsets
from phage_subcluster.models import phage_subcluster
from phage_subcluster.serializers import phage_subclusterSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.views import APIView
from rest_framework.response import Response


class phage_subclusterViewSet(viewsets.ModelViewSet):
    queryset = phage_subcluster.objects.all()
    serializer_class = phage_subclusterSerializer
    filter_backends = [filters.SearchFilter,
                       filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['cluster__id']
    ordering_fields = ['cluster', 'subcluster', 'id']

# class phage_subclusterListView(generics.ListAPIView):
#     queryset = phage_subcluster.objects.all()
#     serializer_class = phage_subclusterSerializer
#     filter_backends = [django_filters.rest_framework.DjangoFilterBackend]


class subclustersView(APIView):
    def get(self, request, *args, **kwargs):
        query_dict = request.query_params.dict()
        clusterid = query_dict['clusterid']
        subcluster = phage_subcluster.objects.filter(cluster_id=clusterid)
        serializer = phage_subclusterSerializer(subcluster, many=True)
        return Response(serializer.data)


class subcluster_detialView(APIView):
    def get(self, request, *args, **kwargs):
        query_dict = request.query_params.dict()
        subclusterid = query_dict['subclusterid']
        subcluster = phage_subcluster.objects.filter(id=subclusterid)
        serializer = phage_subclusterSerializer(subcluster, many=True)
        return Response(serializer.data)
