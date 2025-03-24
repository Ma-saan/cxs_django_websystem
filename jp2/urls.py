from django.urls import path
from . import views

app_name = 'jp2';
urlpatterns = [
    path('', views.top_jp2, name='top_jp2'),
    path('<str:item_no>', views.detail_jp2, name='detail_jp2'),
    path('list/', views.list_jp2, name='list_jp2'),
    path('quality/', views.trouble_quality_jp2, name='trouble_quality_jp2'),
    path('safety/', views.trouble_safety_jp2, name='trouble_safety_jp2'),
    path('inspection_page/', views.inspection_page_jp2, name='inspection_page_jp2'),
    path('inspection_page_a/', views.inspection_page_jp2a, name='inspection_page_jp2a'),
    path('inspection_history_a/', views.inspection_history_jp2a, name='inspection_history_jp2a'),
    path('inspection_page_a/save-inspection-results', views.save_inspection_results_a, name='save_inspection_results_a'),
    path('inspection_history_a/save_manager_confirmation/', views.save_manager_confirmation_a, name='save_manager_confirmation_a'),
    path('inspection_page_b/', views.inspection_page_jp2b, name='inspection_page_jp2b'),
    path('inspection_history_b/', views.inspection_history_jp2b, name='inspection_history_jp2b'),
    path('inspection_page_b/save-inspection-results', views.save_inspection_results_b, name='save_inspection_results_b'),
    path('inspection_history_b/save_manager_confirmation/', views.save_manager_confirmation_b, name='save_manager_confirmation_b'),
    path('inspection_page_c/', views.inspection_page_jp2c, name='inspection_page_jp2c'),
    path('inspection_history_c/', views.inspection_history_jp2c, name='inspection_history_jp2c'),
    path('inspection_page_c/save-inspection-results', views.save_inspection_results_c, name='save_inspection_results_c'),
    path('inspection_history_c/save_manager_confirmation/', views.save_manager_confirmation_c, name='save_manager_confirmation_c'),
    path('inspection_item_list_a/', views.inspection_item_list_a, name='inspection_item_list_a'),
    path('inspection_date_list_a/<int:item_id>/', views.inspection_date_list_a, name='inspection_date_list_a'),
    path('inspection_item_list_b/', views.inspection_item_list_b, name='inspection_item_list_b'),
    path('inspection_date_list_b/<int:item_id>/', views.inspection_date_list_b, name='inspection_date_list_b'),
    path('inspection_item_list_c/', views.inspection_item_list_c, name='inspection_item_list_c'),
    path('inspection_date_list_c/<int:item_id>/', views.inspection_date_list_c, name='inspection_date_list_c'),
    path('<int:item_id>/edit_warning/', views.edit_warning, name='edit_warning'),
    path('view_pdf/<int:pdf_id>/', views.view_pdf, name='view_pdf'),
]