from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from schedule_app.views import schedule_view

urlpatterns = [
    path('grappelli/', include('grappelli.urls')),
    path('admin/', admin.site.urls),
    path('fi/', include('home.urls')),
    path('jp1/', include('jp1.urls')),
    path('jp2/', include('jp2.urls')),
    path('jp3/', include('jp3.urls')),
    path('jp4/', include('jp4.urls')),
    path('jp6a/', include('jp6a.urls')),
    path('jp6b/', include('jp6b.urls')),
    path('jp7/', include('jp7.urls')),
    path('schedule/', include('schedule.urls')),
    path('mr/', include('meetingRoom.urls')),
    path('schedule_app/', include('schedule_app.urls')),
    path('inventory/', include('inventory.urls')),
    path('schedule_manager/', include('schedule_manager.urls')),  

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
