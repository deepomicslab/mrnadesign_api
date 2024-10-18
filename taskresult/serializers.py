from rest_framework import serializers
from taskresult.models import lineardesign_taskresult


class lineardesign_taskresultSerializer(serializers.ModelSerializer):
    class Meta:
        model = lineardesign_taskresult
        fields = '__all__'