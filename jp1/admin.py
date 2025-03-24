from django.contrib import admin
from .models import Jp1, Jp1PDF, Jp1TroubleQuality, Jp1TroubleSafety, Jp1InspectionItem, Jp1InspectionRecord
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field

class Jp1Resource(resources.ModelResource):
    item_no = Field(attribute='item_no', column_name='品番')
    item_name = Field(attribute='item_name', column_name='製品名')
    quantity = Field(attribute='quantity', column_name='入り数')
    duskin = Field(attribute='duskin', column_name='ダスキン')
    quasi_drug = Field(attribute='quasi_drug', column_name='医薬部外品')
    bottle = Field(attribute='bottle', column_name='グリーン')
    accessories = Field(attribute='accessories', column_name='付属品')
    warning = Field(attribute='warning', column_name='注意事項')
    kind_no = Field(attribute='kind_no', column_name='品種番号')
    class Meta:
        model = Jp1
        skip_unchanged = True
        use_bulk = True

class Jp1PDFInline(admin.TabularInline):
    model = Jp1PDF
    extra = 2  # 初期表示する空のフォームの数

class Jp1Admin(ImportExportModelAdmin):
    inlines = [Jp1PDFInline] 
    ordering = ['id']
    list_display = ('id','item_no','item_name','quantity','kind_no','duskin','quasi_drug', 'bottle', 'accessories', 'warning')
    resource_class = Jp1Resource

admin.site.register(Jp1, Jp1Admin)   
admin.site.register(Jp1TroubleQuality)
admin.site.register(Jp1TroubleSafety)   
admin.site.register(Jp1InspectionItem)
admin.site.register(Jp1InspectionRecord)   