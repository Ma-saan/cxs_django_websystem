from django.contrib import admin
from .models import Jp4, Jp4PDF, Jp4TroubleQuality, Jp4TroubleSafety, Jp4InspectionItem, Jp4InspectionRecord
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field

class Jp4Resource(resources.ModelResource):
    item_no = Field(attribute='item_no', column_name='品番')
    item_name = Field(attribute='item_name', column_name='品名')
    specific = Field(attribute='specific', column_name='特殊')
    cap = Field(attribute='cap', column_name='キャップ')
    warning = Field(attribute='warning', column_name='注意事項')
    kind_no = Field(attribute='kind_no', column_name='品種')
    class Meta:
        model = Jp4
        skip_unchanged = True
        use_bulk = True

class Jp4PDFInline(admin.TabularInline):
    model = Jp4PDF
    extra = 2  # 初期表示する空のフォームの数

class Jp4Admin(ImportExportModelAdmin):
    inlines = [Jp4PDFInline]
    ordering = ['id']
    list_display = ('id','item_no','item_name','specific','kind_no','cap', 'warning')
    resource_class = Jp4Resource
    
admin.site.register(Jp4, Jp4Admin)
admin.site.register(Jp4TroubleQuality)
admin.site.register(Jp4TroubleSafety)
admin.site.register(Jp4InspectionItem)
admin.site.register(Jp4InspectionRecord)        