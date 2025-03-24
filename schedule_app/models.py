from django.db import models


class Schedule(models.Model):
    manufacturing_filling = models.CharField(max_length=100, verbose_name='製造/充填')
    production_date = models.CharField(max_length=100, verbose_name='生産日')
    work_center_number = models.CharField(max_length=100, verbose_name='ﾜｰｸｾﾝﾀｰ番号')
    work_center_name = models.CharField(max_length=255, verbose_name='ﾜｰｸｾﾝﾀｰ名')
    product_number = models.CharField(max_length=100, verbose_name='品番')
    product_name = models.CharField(max_length=255, verbose_name='品名')
    production_quantity = models.CharField(max_length=100, verbose_name='生産予定数')
    personnel = models.CharField(max_length=100, verbose_name='人員')
    order_number = models.CharField(max_length=100, verbose_name='ｵｰﾀﾞｰNo.')
    work_order_status = models.CharField(max_length=100, verbose_name='Work Order Status')


class ScheduleAppSchedule(models.Model):
    id = models.BigAutoField(primary_key=True)
    manufacturing_filling = models.CharField(max_length=100)
    order_number = models.CharField(max_length=100)
    personnel = models.CharField(max_length=100)
    product_name = models.CharField(max_length=255)
    product_number = models.CharField(max_length=100)
    production_date = models.CharField(max_length=100)
    production_quantity = models.CharField(max_length=100)
    work_center_name = models.CharField(max_length=255)
    work_center_number = models.CharField(max_length=100)
    work_order_status = models.CharField(max_length=100)


# schedule_app/models.py に追加
class WorkLineAssignment(models.Model):
    schedule = models.ForeignKey(ScheduleAppSchedule, on_delete=models.CASCADE, related_name='assignments')
    line_number = models.CharField(max_length=50)  # 作業ライン番号
    sequence_number = models.IntegerField()  # 順番
    assigned_date = models.DateField()  # 割り当て日
    status = models.CharField(max_length=50, default='pending')  # 状態（pending, in-progress, completed など）
    notes = models.TextField(blank=True, null=True)  # メモ
    
    class Meta:
        ordering = ['assigned_date', 'line_number', 'sequence_number']
        unique_together = ['line_number', 'sequence_number', 'assigned_date']  # 同じライン、同じ日に同じ順番は存在しない


class Meta:
        db_table = 'schedule_app_schedule'  # 明示的にテーブル名を指定
