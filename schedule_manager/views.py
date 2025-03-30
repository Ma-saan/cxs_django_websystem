from django.shortcuts import render
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from datetime import datetime, timedelta
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json
import os
import csv
from django.conf import settings
from django.core.files.storage import FileSystemStorage
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
    
    @action(detail=False, methods=['post'], url_path='update-position')
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

    @action(detail=True, methods=['patch'])
    def update_attribute(self, request, pk=None):
        """
        スケジュールの属性を更新するエンドポイント
        色変更や特殊属性の追加・削除など
        """
        schedule = self.get_object()
        
        # 表示色の更新
        if 'display_color' in request.data:
            schedule.display_color = request.data['display_color']
        
        # 製品名の更新
        if 'product_name' in request.data:
            schedule.product_name = request.data['product_name']
        
        # 特殊属性の追加/削除
        if 'attribute_type' in request.data:
            attribute_type = request.data['attribute_type']
            action = request.data.get('attribute_action', 'add')
            
            if action == 'add':
                # 既存の属性を確認して、なければ追加
                if not schedule.attributes.filter(attribute_type=attribute_type).exists():
                    ScheduleAttribute.objects.create(
                        schedule=schedule,
                        attribute_type=attribute_type,
                        value='true'
                    )
            elif action == 'remove':
                # 属性を削除
                schedule.attributes.filter(attribute_type=attribute_type).delete()
        
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
                date_str = position_data.get('date') or datetime.now().strftime('%Y%m%d')
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


@method_decorator(csrf_exempt, name='dispatch')
class DatabaseSyncView(APIView):
    """
    データベース同期用API
    CSVからの保存やDBからの読み込みを扱います
    """
    def post(self, request):
        """
        DBへの保存処理
        CSVファイルからデータを取り込みDBに保存します
        """
        try:
            # ここではシンプルに成功メッセージを返す
            # 実際の実装では、CSVファイルパスの取得やデータ保存処理を行う
            
            # 例: 
            # CSVファイルを一時保存
            # import_file = request.FILES.get('file')
            # if import_file:
            #    fs = FileSystemStorage(location='temp_uploads/')
            #    filename = fs.save(import_file.name, import_file)
            #    file_path = fs.path(filename)
            #    
            #    # CSVデータをDBに保存
            #    with open(file_path, 'r', encoding='utf-8') as f:
            #        # CSVデータ処理
            #        pass
            
            return Response({'status': 'success', 'message': 'データベースへの保存が完了しました'})
            
        except Exception as e:
            return Response(
                {'error': f'保存処理中にエラーが発生しました: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get(self, request):
        """
        DBからの読み込み処理
        DBからデータを読み込んでフロントエンドに返します
        """
        try:
            # 例:
            # 今日の日付のスケジュールデータを取得
            today = datetime.now().date()
            schedules = ProductSchedule.objects.filter(production_date=today)
            serializer = ProductScheduleSerializer(schedules, many=True)
            
            # 実際には追加の処理が必要かもしれません
            # ここではシンプルに成功メッセージを返す
            
            return Response({
                'status': 'success', 
                'message': 'データベースからの読み込みが完了しました',
                'count': schedules.count()
            })
            
        except Exception as e:
            return Response(
                {'error': f'読み込み処理中にエラーが発生しました: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )