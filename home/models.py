from django.db import models

class Home(models.Model):
    line = models.CharField(max_length=32)
    
    def __str__(self):
        return self.line

class EtcTroubleQuality(models.Model):
    id = models.BigAutoField(primary_key=True)
    発生日 = models.DateField()
    トラブル名 = models.CharField(max_length=256)
    トラブル内容 = models.TextField(blank=True,null=True)
    対策 = models.TextField(blank=True,null=True)
    分類 = models.CharField(blank=True,null=True,max_length=16)
    class Meta:
        db_table = 'etc_trouble_quality'
        verbose_name = 'その他の品質トラブル'
        verbose_name_plural = 'その他の品質トラブル'
    def __str__(self):
        return self.トラブル名
    
class EtcTroubleSafety(models.Model):
    id = models.BigAutoField(primary_key=True)
    発生日 = models.DateField()
    トラブル名 = models.CharField(max_length=256)
    トラブル内容 = models.TextField(blank=True,null=True)
    対策 = models.TextField(blank=True,null=True)
    分類 = models.CharField(blank=True,null=True,max_length=16)
    class Meta:
        db_table = 'etc_trouble_safety'
        verbose_name = 'その他の安全トラブル'
        verbose_name_plural = 'その他の安全トラブル'
    def __str__(self):
        return self.トラブル名   
    
class PDFFile(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='pdfs/')
    class Meta:
        verbose_name = 'PDFファイル'
        verbose_name_plural = 'PDFファイル'
    def __str__(self):
        return self.name