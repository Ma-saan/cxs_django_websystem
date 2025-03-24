from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Material, Product, BOM

@admin.register(Material)
class MaterialAdmin(ImportExportModelAdmin):
    list_display = ('material_id', 'material_name', 'unit')
    search_fields = ('material_id', 'material_name')
    list_filter = ('unit',)

@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    list_display = ('product_id', 'product_name', 'production_line')
    search_fields = ('product_id', 'product_name')
    list_filter = ('production_line',)

@admin.register(BOM)
class BOMAdmin(ImportExportModelAdmin):
    list_display = ('relation_id', 'product', 'material', 'quantity_per_unit', 'unit_type')
    search_fields = ('relation_id', 'product__product_id', 'product__product_name', 
                     'material__material_id', 'material__material_name')
    list_filter = ('unit_type',)