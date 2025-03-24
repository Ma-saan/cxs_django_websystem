from django.contrib import admin
from .models import Home, EtcTroubleQuality, EtcTroubleSafety, PDFFile

admin.site.register(Home)
admin.site.register(EtcTroubleQuality)
admin.site.register(EtcTroubleSafety) 
admin.site.register(PDFFile) 