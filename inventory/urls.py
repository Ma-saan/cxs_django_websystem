from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.index, name='index'),
    path('products/', views.product_list, name='product_list'),
    path('products/new/', views.product_create, name='product_create'),
    path('products/<str:pk>/', views.product_detail, name='product_detail'),
    path('products/<str:pk>/edit/', views.product_edit, name='product_edit'),
    path('products/<str:pk>/delete/', views.product_delete, name='product_delete'),
    path('materials/', views.material_list, name='material_list'),
    path('materials/new/', views.material_create, name='material_create'),
    path('materials/<str:pk>/', views.material_detail, name='material_detail'),
    path('materials/<str:pk>/edit/', views.material_edit, name='material_edit'),
    path('materials/<str:pk>/delete/', views.material_delete, name='material_delete'),
    path('bom/', views.bom_list, name='bom_list'),
    path('products/<str:product_id>/bom/', views.product_bom, name='product_bom'),
]