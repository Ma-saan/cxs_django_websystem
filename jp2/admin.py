from django.contrib import admin
from .models import Jp2, Jp2PDF, Jp2TroubleSafety, Jp2TroubleQuality, Jp2aInspectionItem, Jp2aInspectionRecord, Jp2bInspectionItem, Jp2bInspectionRecord, Jp2cInspectionItem, Jp2cInspectionRecord
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field

class Jp2Resource(resources.ModelResource):
    item_no = Field(attribute='item_no', column_name='品番')
    item_name = Field(attribute='item_name', column_name='製品名')
    specific = Field(attribute='specific', column_name='特殊')
    bottle = Field(attribute='bottle', column_name='ボトル')
    warning = Field(attribute='warning', column_name='注意事項')
    kind_no = Field(attribute='kind_no', column_name='品種')
    class Meta:
        model = Jp2
        skip_unchanged = True
        use_bulk = True

class Jp2PDFInline(admin.TabularInline):
    model = Jp2PDF
    extra = 2  # 初期表示する空のフォームの数

class Jp2Admin(ImportExportModelAdmin):
    inlines =[Jp2PDFInline]
    ordering = ['id']
    list_display = ('id','item_no','item_name','specific','kind_no','bottle', 'warning')
    resource_class = Jp2Resource

admin.site.register(Jp2, Jp2Admin)
admin.site.register(Jp2TroubleQuality)
admin.site.register(Jp2TroubleSafety)    
admin.site.register(Jp2aInspectionItem)
admin.site.register(Jp2aInspectionRecord) 
admin.site.register(Jp2bInspectionItem)
admin.site.register(Jp2bInspectionRecord) 
admin.site.register(Jp2cInspectionItem)
admin.site.register(Jp2cInspectionRecord) 