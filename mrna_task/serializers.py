from rest_framework import serializers
from mrna_task.models import mrna_task


class mrna_taskSerializer(serializers.ModelSerializer):
    class Meta:
        model = mrna_task
        fields = ['id', 'job_id', 'user_id', 'user_input_path', 'is_demo_input', 'output_result_path', 'output_log_path', 'analysis_type', 'parameters', 'status', 'created_at']
