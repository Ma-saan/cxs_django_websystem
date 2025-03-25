from django.db import models

class WorkCenter(models.Model):
    """作業ラインや製造工程を表すモデル"""
    name = models.CharField("ワークセンター名", max_length=50)
    display_name = models.CharField("表示名", max_length=50)
    color = models.CharField("表示色", max_length=20, default="#FFFFFF")
    order = models.IntegerField("表示順", default=0)
    
    def __str__(self):
        return self.display_name
    
    class Meta:
        verbose_name = "ワークセンター"
        verbose_name_plural = "ワークセンター"

class ProductSchedule(models.Model):
    """製品の生産予定を表すモデル"""
    production_date = models.DateField("生産日")
    work_center = models.ForeignKey(WorkCenter, on_delete=models.CASCADE, verbose_name="ワークセンター")
    product_number = models.CharField("品番", max_length=50)
    product_name = models.CharField("製品名", max_length=255)
    production_quantity = models.IntegerField("生産数", default=0)
    grid_row = models.IntegerField("縦位置", default=0)
    grid_column = models.IntegerField("横位置", default=0)
    display_color = models.CharField("表示色", max_length=20, default="#FFFFFF")
    notes = models.TextField("備考", blank=True, null=True)
    last_updated = models.DateTimeField("最終更新日時", auto_now=True)
    
    def __str__(self):
        return f"{self.production_date} - {self.product_name}"
    
    class Meta:
        verbose_name = "生産予定"
        verbose_name_plural = "生産予定"
        # 同じ日付・ワークセンター・製品の組み合わせは一意
        unique_together = ('production_date', 'work_center', 'product_number')

class ScheduleAttribute(models.Model):
    """生産予定の追加属性（アイコン表示など）"""
    schedule = models.ForeignKey(ProductSchedule, on_delete=models.CASCADE, related_name="attributes")
    attribute_type = models.CharField("属性タイプ", max_length=50)
    # 例: 'mixing', 'rapid_fill', 'special_transfer' などの値
    value = models.CharField("値", max_length=255, blank=True, null=True)
    
    def __str__(self):
        return f"{self.schedule} - {self.attribute_type}"
    
    class Meta:
        verbose_name = "予定属性"
        verbose_name_plural = "予定属性"