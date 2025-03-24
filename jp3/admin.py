from django.contrib import admin
from .models import Jp3, Jp3PDF ,Jp3TroubleQuality, Jp3TroubleSafety, Jp3InspectionItem, Jp3InspectionRecord
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field

class Jp3Resource(resources.ModelResource):
    item_no = Field(attribute='item_no', column_name='品番')
    item_name = Field(attribute='item_name', column_name='製品名')
    specific = Field(attribute='specific', column_name='特殊')
    bottle = Field(attribute='bottle', column_name='ボトル')
    warning = Field(attribute='warning', column_name='注意事項')
    kind_no = Field(attribute='kind_no', column_name='品種')
    class Meta:
        model = Jp3
        skip_unchanged = True
        use_bulk = True

class Jp3PDFInline(admin.TabularInline):
    model = Jp3PDF
    extra = 2  # 初期表示する空のフォームの数

#@admin.register(Jp3)

class Jp3Admin(ImportExportModelAdmin):
    inlines = [Jp3PDFInline] 
    ordering = ['id']
    list_display = ('id','item_no','item_name')
    resource_class = Jp3Resource

admin.site.register(Jp3, Jp3Admin)
admin.site.register(Jp3TroubleQuality)
admin.site.register(Jp3TroubleSafety) 
admin.site.register(Jp3InspectionItem)
admin.site.register(Jp3InspectionRecord)
