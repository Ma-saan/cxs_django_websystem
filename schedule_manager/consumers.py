import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ProductSchedule
from .serializers import ProductScheduleSerializer

class ScheduleConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # グループに参加
        await self.channel_layer.group_add(
            "schedule_updates",
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # グループから離脱
        await self.channel_layer.group_discard(
            "schedule_updates",
            self.channel_name
        )

    async def receive(self, text_data):
        """クライアントからメッセージを受信したときの処理"""
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if action == 'sync':
                # 同期リクエスト - 現在の日付の全スケジュールを送信
                date = data.get('date')
                if date:
                    schedules = await self.get_schedules_for_date(date)
                    await self.send(text_data=json.dumps({
                        'action': 'sync',
                        'schedules': schedules
                    }))
                
            elif action == 'update_position':
                # 位置更新リクエスト
                schedule_id = data.get('id')
                grid_row = data.get('grid_row')
                grid_column = data.get('grid_column')
                
                if schedule_id and (grid_row is not None or grid_column is not None):
                    updated = await self.update_schedule_position(
                        schedule_id, grid_row, grid_column
                    )
                    if updated:
                        # 更新が成功したら、グループにブロードキャスト
                        await self.channel_layer.group_send(
                            "schedule_updates",
                            {
                                "type": "schedule_update",
                                "message": {
                                    "action": "position_update",
                                    "schedule_id": schedule_id,
                                    "grid_row": grid_row,
                                    "grid_column": grid_column
                                }
                            }
                        )
                        
        except json.JSONDecodeError:
            pass

    async def schedule_update(self, event):
        """他のコンシューマからスケジュール更新を受け取ったときの処理"""
        message = event["message"]
        # クライアントに送信
        await self.send(text_data=json.dumps(message))
        
    @database_sync_to_async
    def get_schedules_for_date(self, date_str):
        """指定された日付のスケジュールを取得"""
        try:
            # 'YYYYMMDD'または'YY/MM/DD'形式をサポート
            from datetime import datetime
            if '/' in date_str:
                date = datetime.strptime(date_str, '%y/%m/%d').date()
            else:
                date = datetime.strptime(date_str, '%Y%m%d').date()
                
            schedules = ProductSchedule.objects.filter(production_date=date).select_related('work_center')
            serializer = ProductScheduleSerializer(schedules, many=True)
            return serializer.data
        except ValueError:
            return []
            
    @database_sync_to_async
    def update_schedule_position(self, schedule_id, grid_row, grid_column):
        """スケジュールの位置を更新"""
        try:
            schedule = ProductSchedule.objects.get(id=schedule_id)
            if grid_row is not None:
                schedule.grid_row = grid_row
            if grid_column is not None:
                schedule.grid_column = grid_column
            schedule.save(update_fields=['grid_row', 'grid_column', 'last_updated'])
            return True
        except ProductSchedule.DoesNotExist:
            return False