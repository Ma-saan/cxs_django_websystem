from django.shortcuts import render
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from datetime import datetime, timedelta
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import WorkCenter, ProductSchedule, ScheduleAttribute
from .serializers import (
    WorkCenterSerializer, ProductScheduleSerializer, ScheduleUpdateSerializer
)

@method_decorator(ensure_csrf_cookie, name='dispatch')
class ScheduleManagerView(APIView):
    """メインの管理ビュー - カレンダーアプリを表示"""
    def get(self, request):
        return render(request, 'schedule_manager/index.html')

class WorkCenterViewSet(viewsets.ReadOnlyModelViewSet):
    """ワークセンター情報を提供するViewSet"""
    queryset = WorkCenter.objects.all().order_by('order')
    serializer_class = WorkCenterSerializer

class ProductScheduleViewSet(viewsets.ModelViewSet):
    """生産予定のCRUD操作を提供するViewSet"""
    queryset = ProductSchedule.objects.all()
    serializer_class = ProductScheduleSerializer
    
    def get_queryset(self):
        queryset = ProductSchedule.objects.all()
        
        # 日付フィルター
        date_str = self.request.query_params.get('date')
        if date_str:
            print(f"日付フィルター: {date_str}")
            try:
                # YYYYMMDD形式の場合
                if len(date_str) == 8 and date_str.isdigit():
                    year = int(date_str[0:4])
                    month = int(date_str[4:6])
                    day = int(date_str[6:8])
                    target_date = datetime(year, month, day).date()
                    print(f"解析された日付: {target_date}")
                    queryset = queryset.filter(production_date=target_date)
                # YY/MM/DD形式の場合
                elif '/' in date_str:
                    date = datetime.strptime(date_str, '%y/%m/%d').date()
                    queryset = queryset.filter(production_date=date)
                # YYYY-MM-DD形式の場合
                elif '-' in date_str:
                    date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    queryset = queryset.filter(production_date=date)
                else:
                    print(f"不明な日付形式: {date_str}")
            except ValueError as e:
                print(f"日付パースエラー: {e}")
                pass
                
        # 日付範囲フィルター
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date and end_date:
            try:
                # YYYYMMDD形式をサポート
                start = datetime.strptime(start_date, '%Y%m%d').date()
                end = datetime.strptime(end_date, '%Y%m%d').date()
                queryset = queryset.filter(production_date__gte=start, production_date__lte=end)
            except ValueError:
                pass
        
        # ワークセンターフィルター
        work_center = self.request.query_params.get('work_center')
        if work_center:
            queryset = queryset.filter(work_center__name=work_center)
            
        return queryset.select_related('work_center').prefetch_related('attributes')
    
    @action(detail=False, methods=['post'])
    def update_position(self, request):
        """位置情報を更新するエンドポイント"""
        serializer = ScheduleUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                schedule = ProductSchedule.objects.get(id=serializer.validated_data['id'])
                
                # 位置情報の更新
                if 'grid_row' in serializer.validated_data:
                    schedule.grid_row = serializer.validated_data['grid_row']
                if 'grid_column' in serializer.validated_data:
                    schedule.grid_column = serializer.validated_data['grid_column']
                if 'display_color' in serializer.validated_data:
                    schedule.display_color = serializer.validated_data['display_color']
                if 'notes' in serializer.validated_data:
                    schedule.notes = serializer.validated_data['notes']
                    
                schedule.save()
                
                # WebSocketで更新を通知
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    "schedule_updates",
                    {
                        "type": "schedule_update",
                        "message": {
                            "action": "update",
                            "schedule": ProductScheduleSerializer(schedule).data
                        }
                    }
                )
                
                return Response(ProductScheduleSerializer(schedule).data)
            
            except ProductSchedule.DoesNotExist:
                return Response(
                    {"error": "指定されたスケジュールが見つかりません"},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        """作成時の処理"""
        instance = serializer.save()
        
        # WebSocketで更新を通知
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "schedule_updates",
            {
                "type": "schedule_update",
                "message": {
                    "action": "create",
                    "schedule": ProductScheduleSerializer(instance).data
                }
            }
        )
        
    def perform_update(self, serializer):
        """更新時の処理"""
        instance = serializer.save()
        
        # WebSocketで更新を通知
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "schedule_updates",
            {
                "type": "schedule_update",
                "message": {
                    "action": "update",
                    "schedule": ProductScheduleSerializer(instance).data
                }
            }
        )
        
    def perform_destroy(self, instance):
        """削除時の処理"""
        schedule_id = instance.id
        schedule_data = ProductScheduleSerializer(instance).data
        instance.delete()
        
        # WebSocketで更新を通知
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "schedule_updates",
            {
                "type": "schedule_update",
                "message": {
                    "action": "delete",
                    "schedule_id": schedule_id,
                    "schedule_data": schedule_data
                }
            }
        )