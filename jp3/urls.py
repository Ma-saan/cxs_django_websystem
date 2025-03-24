from django.urls import path
from . import views

app_name = 'jp3';
urlpatterns = [
    path('', views.top_jp3, name='top_jp3'),
    path('<str:item_no>', views.detail_jp3, name='detail_jp3'),
    path('list/', views.list_jp3, name='list_jp3'),
    path('quality/', views.trouble_quality_jp3, name='trouble_quality_jp3'),
    path('safety/', views.trouble_safety_jp3, name='trouble_safety_jp3'),
    path('inspection_page/', views.inspection_page_jp3, name='inspection_page_jp3'),
    path('inspection_history/', views.inspection_history_jp3, name='inspection_history_jp3'),
    path('inspection_page/save-inspection-results', views.save_inspection_results, name='save_inspection_results'),
    path('inspection_history/save_manager_confirmation/', views.save_manager_confirmation, name='save_manager_confirmation'),
    path('inspection_item_list/', views.inspection_item_list, name='inspection_item_list'),
    path('inspection_date_list/<int:item_id>/', views.inspection_date_list, name='inspection_date_list'),
    path('<int:item_id>/edit_warning/', views.edit_warning, name='edit_warning'),
    path('view_pdf/<int:pdf_id>/', views.view_pdf, name='view_pdf'),
]