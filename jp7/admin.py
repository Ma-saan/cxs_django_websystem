from django.contrib import admin
from .models import Jp7, Jp7PDF, Jp7TroubleQuality, Jp7TroubleSafety, Jp7aInspectionItem, Jp7aInspectionRecord, Jp7bInspectionItem, Jp7bInspectionRecord, Jp7cInspectionItem, Jp7cInspectionRecord
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field

class Jp7Resource(resources.ModelResource):
    item_no = Field(attribute='item_no', column_name='OJ後新充填品番')
    item_name = Field(attribute='item_name', column_name='Item Description')
    seal = Field(attribute='seal', column_name='その他')
    warning = Field(attribute='warning', column_name='注意事項')
    class Meta:
        model = Jp7
        skip_unchanged = True
        use_bulk = True

class Jp7PDFInline(admin.TabularInline):
    model = Jp7PDF
    extra = 2  # 初期表示する空のフォームの数

class Jp7Admin(ImportExportModelAdmin):
    inlines = [Jp7PDFInline]
    ordering = ['id']
    list_display = ('id','item_no','item_name','seal','warning')
    resource_class = Jp7Resource

admin.site.register(Jp7, Jp7Admin)
admin.site.register(Jp7TroubleQuality)
admin.site.register(Jp7TroubleSafety)     
admin.site.register(Jp7aInspectionItem)
admin.site.register(Jp7aInspectionRecord) 
admin.site.register(Jp7bInspectionItem)
admin.site.register(Jp7bInspectionRecord) 
admin.site.register(Jp7cInspectionItem)
admin.site.register(Jp7cInspectionRecord) 