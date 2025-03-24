from django.db import models

class Material(models.Model):
    material_id = models.CharField("材料品番", max_length=50, primary_key=True)
    material_name = models.CharField("材料名", max_length=255)
    unit = models.CharField("単位", max_length=20)
    
    def __str__(self):
        return f"{self.material_id}: {self.material_name}"
    
    class Meta:
        verbose_name = "材料"
        verbose_name_plural = "材料"
        ordering = ['material_id']

class Product(models.Model):
    product_id = models.CharField("製品品番", max_length=50, primary_key=True)
    product_name = models.CharField("製品名", max_length=255)
    production_line = models.CharField("生産ライン", max_length=50)
    
    def __str__(self):
        return f"{self.product_id}: {self.product_name}"
    
    class Meta:
        verbose_name = "製品"
        verbose_name_plural = "製品"
        ordering = ['product_id']

class BOM(models.Model):
    relation_id = models.CharField("関連ID", max_length=50)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="製品")
    material = models.ForeignKey(Material, on_delete=models.CASCADE, verbose_name="材料")
    quantity_per_unit = models.DecimalField("数量", max_digits=10, decimal_places=2)
    unit_type = models.CharField("単位種別", max_length=20)
    
    def __str__(self):
        return f"{self.product.product_id} - {self.material.material_id}"
    
    class Meta:
        verbose_name = "BOM"
        verbose_name_plural = "BOM"
        unique_together = ('product', 'material')