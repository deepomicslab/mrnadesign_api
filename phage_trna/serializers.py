from rest_framework import serializers
from phage_trna.models import phage_trna
# from phage.models import phage
from phage.serializers import phageSerializer


class phage_trnaSerializer(serializers.ModelSerializer):
    # phage = phageSerializer(many=True,read_only=True)

    class Meta:
        model = phage_trna
        fields = '__all__'
