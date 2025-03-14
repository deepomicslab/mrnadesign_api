from rest_framework import serializers
from isoform_sequences.models import isoform, gene

try:
    from mrnadesign_api import settings_local as local_settings
except ImportError:
    local_settings = None


class IsoformSerializer(serializers.ModelSerializer):
    fasta_path = serializers.SerializerMethodField()
    gtf_path = serializers.SerializerMethodField()
    gff_path = serializers.SerializerMethodField()

    class Meta:
        model = isoform
        fields = '__all__'

    def get_fasta_path(self, obj):
        return "{}/{}.fasta".format(local_settings.ISOFORMFASTA, obj.isoform_id)

    def get_gtf_path(self, obj):
        return "{}/{}.gtf".format(local_settings.ISOFORMGTF, obj.isoform_id)

    def get_gff_path(self, obj):
        return "{}/{}.gff3".format(local_settings.ISOFORMGFF, obj.isoform_id)


class GeneSerializer(serializers.ModelSerializer):
    class Meta:
        model = gene
        fields = '__all__'
