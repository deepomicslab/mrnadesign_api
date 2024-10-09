from rest_framework import serializers
from phage_subcluster.models import phage_subcluster


class phage_subclusterSerializer(serializers.ModelSerializer):
    # trna = serializers.SerializerMethodField()

    class Meta:
        model = phage_subcluster
        fields = '__all__'

    # def get_trna(self, obj):
    #     trnacount = 0
    #     from phage_trna.models import phage_trna
    #     from phage.models import phage
    #     phages = phage.objects.filter(subcluster=obj.subcluster)
    #     for phage in phages:
    #         trnas = phage_trna.objects.filter(phage_id=phage.id)
    #         trnacount += len(trnas)
    #     return trnacount
