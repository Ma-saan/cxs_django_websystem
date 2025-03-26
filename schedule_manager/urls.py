from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'work-centers', views.WorkCenterViewSet)
router.register(r'schedules', views.ProductScheduleViewSet)

app_name = 'schedule_manager'

urlpatterns = [
    path('', views.ScheduleManagerView.as_view(), name='index'),
    path('api/', include(router.urls)),
]