from django.urls import path
from . import views

app_name = "cal"
urlpatterns = [
    path("", views.index, name="index"),
    path("add/", views.add_event, name="add_event"),
    path("list/", views.get_events, name="get_events"),
    path("delete/", views.delete_events, name="delete_events"),
    path('color_mapping/', views.get_color_mapping, name='get_color_mapping'),
    path('update/', views.update_event, name='update_event'),
]