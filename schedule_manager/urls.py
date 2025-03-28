from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import csv_importer

router = DefaultRouter()
router.register(r'schedules', views.ProductScheduleViewSet, basename='schedule')
router.register(r'work-centers', views.WorkCenterViewSet)

app_name = 'schedule_manager'

urlpatterns = [
    path('', views.ScheduleManagerView.as_view(), name='index'),
    path('api/', include(router.urls)),
    path('import-csv/', csv_importer.csv_importer_view, name='import_csv'),
    path('api/save-to-db/', views.DatabaseSyncView.as_view(), name='save_to_db'),
    path('api/load-from-db/', views.DatabaseSyncView.as_view(), name='load_from_db'),
]