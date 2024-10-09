from rest_framework import serializers
from phage.models import phage
try:
    from Phage_api import settings_local as local_settings
except ImportError:
    local_settings = None


class phageSerializer(serializers.ModelSerializer):

    lifestyle = serializers.SerializerMethodField()

    fastapath = serializers.SerializerMethodField()
    gbkpath = serializers.SerializerMethodField()
    gffpath = serializers.SerializerMethodField()
    
    class Meta:
        model = phage
        exclude = ['display_id']

    def get_lifestyle(self, obj):
        from phage_lifestyle.models import phage_lifestyle
        lifestyle = phage_lifestyle.objects.filter(phage_id=obj.id)
        return lifestyle[0].lifestyle

    def get_fastapath(self, obj):
        return local_settings.PHAGEFASTA+str(obj.Data_Sets.name)+'/'+obj.Acession_ID+'.fasta'

    def get_gbkpath(self, obj):
        return local_settings.PHAGEGBK+str(obj.Data_Sets.name)+'/'+obj.Acession_ID+'.gbk'
    
    def get_gffpath(self, obj):
        return local_settings.PHAGEGFF+str(obj.Data_Sets.name)+'/'+obj.Acession_ID+'.gff3'