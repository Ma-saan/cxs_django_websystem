from django.urls import path
from . import views

app_name = 'jp7';
urlpatterns = [
    path('', views.top_jp7, name='top_jp7'),
    path('<str:item_no>', views.detail_jp7, name='detail_jp7'),
    path('list/', views.list_jp7, name='list_jp7'),
    path('quality/', views.trouble_quality_jp7, name='trouble_quality_jp7'),
    path('safety/', views.trouble_safety_jp7, name='trouble_safety_jp7'),
    path('inspection_page/', views.inspection_page_jp7, name='inspection_page_jp7'),
    path('inspection_page_a/', views.inspection_page_jp7a, name='inspection_page_jp7a'),
    path('inspection_history_a/', views.inspection_history_jp7a, name='inspection_history_jp7a'),
    path('inspection_page_a/save-inspection-results', views.save_inspection_results_a, name='save_inspection_results_a'),
    path('inspection_history_a/save_manager_confirmation/', views.save_manager_confirmation_a, name='save_manager_confirmation_a'),
    path('inspection_page_b/', views.inspection_page_jp7b, name='inspection_page_jp7b'),
    path('inspection_history_b/', views.inspection_history_jp7b, name='inspection_history_jp7b'),
    path('inspection_page_b/save-inspection-results', views.save_inspection_results_b, name='save_inspection_results_b'),
    path('inspection_history_b/save_manager_confirmation/', views.save_manager_confirmation_b, name='save_manager_confirmation_b'),
    path('inspection_page_c/', views.inspection_page_jp7c, name='inspection_page_jp7c'),
    path('inspection_history_c/', views.inspection_history_jp7c, name='inspection_history_jp7c'),
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