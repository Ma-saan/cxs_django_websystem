from django.contrib import admin
from .models import Jp6a, Jp6aPDF, Jp6aTroubleQuality, Jp6aTroubleSafety, Jp6aInspectionItem, Jp6aInspectionRecord
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field

class Jp6aResource(resources.ModelResource):
    item_no = Field(attribute='item_no', column_name='品番')
    item_name = Field(attribute='item_name', column_name='製品名')
    specific = Field(attribute='specific', column_name='特殊')
    bottle = Field(attribute='bottle', column_name='ボトル')
    warning = Field(attribute='warning', column_name='注意事項')
    kind_no = Field(attribute='kind_no', column_name='品種')
    class Meta:
        model = Jp6a
        skip_unchanged = True
        use_bulk = True

class Jp6aPDFInline(admin.TabularInline):
    model = Jp6aPDF
    extra = 2  # 初期表示する空のフォームの数

class Jp6aAdmin(ImportExportModelAdmin):
    inlines = [Jp6aPDFInline]
    ordering = ['id']
    list_display = ('id','item_no','item_name','specific','kind_no','bottle', 'warning')
    resource_class = Jp6aResource

admin.site.register(Jp6a, Jp6aAdmin)
admin.site.register(Jp6aTroubleQuality)
admin.site.register(Jp6aTroubleSafety)
admin.site.register(Jp6aInspectionItem)
admin.site.register(Jp6aInspectionRecord)       