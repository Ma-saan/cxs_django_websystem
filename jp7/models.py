from django.db import models

class Jp7(models.Model):
    item_no = models.CharField(verbose_name='品番', max_length=32)
    item_name = models.CharField(verbose_name='製品名', max_length=256)
    seal = models.CharField(verbose_name='封印', max_length=20, blank=True, null=True)
    warning = models.TextField(verbose_name='注意事項', blank=True, null=True)
    class Meta:
        db_table = 'jp7_items'
        verbose_name = 'JP7'
        verbose_name_plural = 'JP7製品一覧'
        app_label = 'jp7'
    
    def __str__(self):
        return self.item_name
    
class Jp7PDF(models.Model):
    jp7 = models.ForeignKey(Jp7, related_name='pdf_files', on_delete=models.CASCADE)
    name = models.CharField(verbose_name='PDF名', max_length=100)
    file = models.FileField(upload_to='jp7_pdfs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'jp7_pdfs'
        verbose_name = 'JP7 PDF'
        verbose_name_plural = 'JP7 PDFs'
        app_label = 'jp7'
    
    def __str__(self):
        return self.name   
    
class Jp7TroubleQuality(models.Model):
    id = models.BigAutoField(primary_key=True)
    発生日 = models.DateField()
    トラブル名 = models.CharField(max_length=256)
    トラブル内容 = models.TextField(blank=True,null=True)
    対策 = models.TextField(blank=True,null=True)
    分類 = models.CharField(blank=True,null=True,max_length=16)
    class Meta:
        db_table = 'jp7_trouble_quality'
        verbose_name = 'JP7品質トラブル'
        verbose_name_plural = 'JP7品質トラブル'
    def __str__(self):
        return self.トラブル名
    
class Jp7TroubleSafety(models.Model):
    id = models.BigAutoField(primary_key=True)
    発生日 = models.DateField()
    トラブル名 = models.CharField(max_length=256)
    トラブル内容 = models.TextField(blank=True,null=True)
    対策 = models.TextField(blank=True,null=True)
    分類 = models.CharField(blank=True,null=True,max_length=16)
    class Meta:
        db_table = 'jp7_trouble_safety'
        verbose_name = 'JP7安全トラブル'
        verbose_name_plural = 'JP7安全トラブル'
    def __str__(self):
        return self.トラブル名     

class Jp7aInspectionItem(models.Model):
    name = models.CharField(verbose_name='点検項目', max_length=100)
    equipment_name = models.CharField(verbose_name='機器名',max_length=100)
    inspection_frequency = models.CharField(verbose_name='点検頻度',max_length=50)
    responsible_person = models.CharField(verbose_name='担当',max_length=100)
    class Meta:
        verbose_name = 'JP7A保守点検'
        verbose_name_plural = 'JP7A保守点検'
    def __str__(self):
        return f"{self.name} - {self.equipment_name}"

class Jp7aInspectionRecord(models.Model):
    item = models.ForeignKey(Jp7aInspectionItem, on_delete=models.CASCADE)
    inspection_date = models.DateField()
    result = models.BooleanField(default=False)
    manager_confirmation_date = models.DateTimeField(blank=True, null=True)
    class Meta:
        verbose_name = 'JP7A保守点検記録'
        verbose_name_plural = 'JP7A保守点検記録'
    def __str__(self):
        return f"{self.item} - {self.inspection_date}"       
    
class Jp7bInspectionItem(models.Model):
    name = models.CharField(verbose_name='点検項目', max_length=100)
    equipment_name = models.CharField(verbose_name='機器名',max_length=100)
    inspection_frequency = models.CharField(verbose_name='点検頻度',max_length=50)
    responsible_person = models.CharField(verbose_name='担当',max_length=100)
    class Meta:
        verbose_name = 'JP7B保守点検'
        verbose_name_plural = 'JP7B保守点検'
    def __str__(self):
        return f"{self.name} - {self.equipment_name}"

class Jp7bInspectionRecord(models.Model):
    item = models.ForeignKey(Jp7bInspectionItem, on_delete=models.CASCADE)
    inspection_date = models.DateField()
    result = models.BooleanField(default=False)
    manager_confirmation_date = models.DateTimeField(blank=True, null=True)
    class Meta:
        verbose_name = 'JP7B保守点検記録'
        verbose_name_plural = 'JP7B保守点検記録'
    def __str__(self):
        return f"{self.item} - {self.inspection_date}" 
       
class Jp7cInspectionItem(models.Model):
    name = models.CharField(verbose_name='点検項目', max_length=100)
    equipment_name = models.CharField(verbose_name='機器名',max_length=100)
    inspection_frequency = models.CharField(verbose_name='点検頻度',max_length=50)
    responsible_person = models.CharField(verbose_name='担当',max_length=100)
    class Meta:
        verbose_name = 'JP7C保守点検'
        verbose_name_plural = 'JP7C保守点検'
    def __str__(self):
        return f"{self.name} - {self.equipment_name}"

class Jp7cInspectionRecord(models.Model):
    item = models.ForeignKey(Jp7cInspectionItem, on_delete=models.CASCADE)
    inspection_date = models.DateField()
    result = models.BooleanField(default=False)
    manager_confirmation_date = models.DateTimeField(blank=True, null=True)
    class Meta:
        verbose_name = 'JP7C保守点検記録'
        verbose_name_plural = 'JP7C保守点検記録'
    def __str__(self):
        return f"{self.item} - {self.inspection_date}"    