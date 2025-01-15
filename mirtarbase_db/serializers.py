from rest_framework import serializers
from mirtarbase_db.models import mirtarbase_db


class mirtarbase_db_Serializer(serializers.ModelSerializer):
    class Meta:
        model = mirtarbase_db
        fields = '__all__'