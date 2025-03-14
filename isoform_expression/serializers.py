from rest_framework import serializers

from isoform_expression.models import ExpressionRecord


class ExpressionRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpressionRecord
        fields = '__all__'
