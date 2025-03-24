from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.index, name='index'),
    path('products/', views.product_list, name='product_list'),
    path('products/<str:pk>/', views.product_detail, name='product_detail'),
    path('materials/', views.material_list, name='material_list'),
    path('materials/<str:pk>/', views.material_detail, name='material_detail'),
    path('bom/', views.bom_list, name='bom_list'),
    path('products/<str:product_id>/bom/', views.product_bom, name='product_bom'),
]