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
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
import json
from channels.db import database_sync_to_async
from .models import WorkCenter, ProductSchedule, ScheduleAttribute
from .serializers import WorkCenterSerializer, ProductScheduleSerializer, ScheduleUpdateSerializer


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

@method_decorator(csrf_exempt, name='dispatch')
class SchedulePositionUpdateView(APIView):
    """
    生産予定の位置情報を更新するAPI
    フロントエンドからのドラッグ＆ドロップ操作を処理します
    """
    def post(self, request):
        try:
            # リクエストデータのバリデーション
            card_id = request.data.get('id')
            position_data = request.data.get('position', {})
            
            if not card_id:
                return Response({'error': 'カードIDが必要です'}, status=status.HTTP_400_BAD_REQUEST)
                
            # 対象のスケジュールを取得
            try:
                schedule = ProductSchedule.objects.get(id=card_id)
            except ProductSchedule.DoesNotExist:
                return Response({'error': '指定されたスケジュールが見つかりません'}, status=status.HTTP_404_NOT_FOUND)
                
            # フロントエンドから送られた位置情報
            side = position_data.get('side')  # 'left' or 'right'
            line_id = position_data.get('lineId')  # ワークセンターID
            position = position_data.get('position', 0)  # 表示順
            
            # ワークセンターの確認と更新
            if line_id and line_id != str(schedule.work_center.id):
                try:
                    new_work_center = WorkCenter.objects.get(name=line_id)
                    schedule.work_center = new_work_center
                except WorkCenter.DoesNotExist:
                    return Response(
                        {'error': '指定されたワークセンターが見つかりません'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # 日付の更新（別の日に移動した場合）
            if side:
                date_str = request.data.get('date') or datetime.now().strftime('%Y%m%d')
                try:
                    # APIから来る日付形式に応じて処理（YYYYMMDDを想定）
                    year = int(date_str[:4])
                    month = int(date_str[4:6])
                    day = int(date_str[6:8])
                    new_date = datetime(year, month, day).date()
                    schedule.production_date = new_date
                except (ValueError, IndexError):
                    pass  # 日付形式が不正な場合は無視
            
            # 位置情報の更新
            schedule.grid_row = position
            
            # 保存
            schedule.save(update_fields=['work_center', 'production_date', 'grid_row', 'last_updated'])
            
            # WebSocketで他のクライアントに通知
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "schedule_updates",
                {
                    "type": "schedule_update",
                    "message": {
                        "action": "position_update",
                        "schedule": ProductScheduleSerializer(schedule).data
                    }
                }
            )
            
            return Response({
                'status': 'success',
                'message': '位置情報を更新しました',
                'schedule': ProductScheduleSerializer(schedule).data
            })
            
        except Exception as e:
            return Response(
                {'error': f'処理中にエラーが発生しました: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# schedule_manager/urls.py に追加
from django.urls import path
from . import views

urlpatterns = [
    # 既存のURLパターン
    # ...
    
    # 位置更新用のエンドポイント
    path('api/schedules/update-position/', views.SchedulePositionUpdateView.as_view(), name='update_position'),
]

# schedule_manager/consumers.py に追加（WebSocket通信のための拡張）

async def schedule_update(self, event):
    """スケジュール更新通知のブロードキャスト処理（既存関数の拡張）"""
    message = event["message"]
    
    # クライアントに送信
    await self.send(text_data=json.dumps(message))
    
    # 位置更新の場合、影響を受ける他のスケジュールも更新
    if message.get("action") == "position_update":
        schedule = message.get("schedule", {})
        if schedule:
            # 同じライン内の同じ日付のカードの順序を再整理
            work_center_id = schedule.get("work_center")
            production_date = schedule.get("production_date")
            
            if work_center_id and production_date:
                # データベースから該当するスケジュールを全て取得
                affected_schedules = await self.get_schedules_for_line_date(
                    work_center_id, production_date
                )
                
                # 更新されたスケジュールの情報をクライアントに送信
                if affected_schedules:
                    await self.send(text_data=json.dumps({
                        "action": "sync_line",
                        "work_center": work_center_id,
                        "date": production_date,
                        "schedules": affected_schedules
                    }))

@database_sync_to_async
def get_schedules_for_line_date(self, work_center_id, date_str):
    """特定のラインと日付のスケジュールを取得"""
    try:
        # 日付形式を変換（必要に応じて）
        from datetime import datetime
        if isinstance(date_str, str):
            if '-' in date_str:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
            else:
                # YYYYMMDD形式を想定
                date = datetime.strptime(date_str, '%Y%m%d').date()
        else:
            date = date_str
            
        # 該当するスケジュールを取得してシリアライズ
        schedules = ProductSchedule.objects.filter(
            work_center_id=work_center_id,
            production_date=date
        ).order_by('grid_row')
        
        serializer = ProductScheduleSerializer(schedules, many=True)
        return serializer.data
    except Exception as e:
        print(f"スケジュール取得エラー: {e}")
        return []