from django.contrib import admin
from .models import Jp6b, Jp6bPDF, Jp6bTroubleQuality, Jp6bTroubleSafety, Jp6bInspectionItem, Jp6bInspectionRecord
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field

class Jp6bResource(resources.ModelResource):
    item_no = Field(attribute='item_no', column_name='品番')
    item_name = Field(attribute='item_name', column_name='製品名')
    specific = Field(attribute='specific', column_name='特殊')
    bottle = Field(attribute='bottle', column_name='ボトル')
    warning = Field(attribute='warning', column_name='注意事項')
    kind_no = Field(attribute='kind_no', column_name='品種')
    class Meta:
        model = Jp6b
        skip_unchanged = True
        use_bulk = True

class Jp6bPDFInline(admin.TabularInline):
    model = Jp6bPDF
    extra = 2  # 初期表示する空のフォームの数

class Jp6bAdmin(ImportExportModelAdmin):
    inlines = [Jp6bPDFInline]
    ordering = ['id']
    list_display = ('id','item_no','item_name','specific','kind_no','bottle', 'warning')
    resource_class = Jp6bResource

admin.site.register(Jp6b, Jp6bAdmin)
admin.site.register(Jp6bTroubleQuality)
admin.site.register(Jp6bTroubleSafety)    
admin.site.register(Jp6bInspectionItem)
admin.site.register(Jp6bInspectionRecord)  