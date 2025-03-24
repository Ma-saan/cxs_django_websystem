from django.urls import path
from . import views
from django.views.generic import RedirectView

app_name = 'home'
urlpatterns = [
    path('favicon.ico', RedirectView.as_view(url='/static/img/favicon.ico')),
    path('', views.list_home, name='list_home'),
    path('etc/', views.top_etc, name='top_etc'),
    path('etc/quality/', views.trouble_quality_etc, name='trouble_quality_etc'),
    path('etc/safety/', views.trouble_safety_etc, name='trouble_safety_etc'),
    path('all/', views.top_all, name='top_all'),
    path('all/<str:item_no>', views.detail_all, name='detail_all'),
    path('all/list/', views.list_all, name='list_all'),
    path('all/quality/', views.trouble_quality_all, name='trouble_quality_all'),
    path('all/safety/', views.trouble_safety_all, name='trouble_safety_all'),
    path('pdf_list/', views.pdf_list, name='pdf_list'),
    path('view_pdf/<int:pdf_id>/', views.view_pdf, name='view_pdf'),
]