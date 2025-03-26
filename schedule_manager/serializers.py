from rest_framework import serializers
from .models import WorkCenter, ProductSchedule, ScheduleAttribute

class WorkCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkCenter
        fields = ['id', 'name', 'display_name', 'color', 'order']

class ScheduleAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleAttribute
        fields = ['id', 'attribute_type', 'value']

class ProductScheduleSerializer(serializers.ModelSerializer):
    work_center_details = WorkCenterSerializer(source='work_center', read_only=True)
    attributes = ScheduleAttributeSerializer(many=True, read_only=True)
    
    class Meta:
        model = ProductSchedule
        fields = [
            'id', 'production_date', 'work_center', 'work_center_details',
            'product_number', 'product_name', 'production_quantity', 
            'grid_row', 'grid_column', 'display_color', 'notes',
            'last_updated', 'attributes'
        ]

class ScheduleUpdateSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    grid_row = serializers.IntegerField(required=False, allow_null=True)
    grid_column = serializers.IntegerField(required=False, allow_null=True)
    display_color = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=20)
    notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)