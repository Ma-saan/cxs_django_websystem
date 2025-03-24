from django.urls import path
from schedule_app.views import upload_view, schedule_view
from . import views

urlpatterns = [
    path('upload/', upload_view, name='upload_view'),
    path('schedule_list/', schedule_view, name='schedule_view'),
    path('line-assignment/', views.line_assignment_view, name='line_assignment'),
    path('update-assignment/', views.update_assignment, name='update_assignment'),
]
