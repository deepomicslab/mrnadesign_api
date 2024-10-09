from rest_framework import viewsets
from analysis.models import analysis
from analysis.serializers import analysisSerializer
from rest_framework.views import APIView
from Phage_api import settings_local as local_settings
from rest_framework.response import Response
from phage.models import phage

    
class analysisViewSet(viewsets.ModelViewSet):
    queryset = analysis.objects.all()
    serializer_class = analysisSerializer


class inputcheck(APIView):
    def post(self, request, *args, **kwargs):
        res = {}
        
        split_phageids = request.data['phageids'].split(';')
        print(split_phageids)
        search_pids=[]
        phages = phage.objects.filter(Acession_ID__in=split_phageids)
        for ph in phages:
            search_pids.append(ph.Acession_ID)
        #       idlist.value = res.idlist
        # inputfeedback.value = res.message
        # validationstatus.value = res.status

        res['idlist']=search_pids
        res['message']='Your selected phage ids are valid: '+', '.join(search_pids)
        res['status']='success'
        return Response(res)