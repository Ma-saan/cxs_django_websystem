from django.urls import path
from . import views

app_name = 'schedule';
urlpatterns = [
    path('<specified_date>', views.schedule, name='schedule'),
    path('product_detail/<str:specified_date3>/<str:product_number>/', views.product_detail, name='product_detail'),
    path('get_schedule_data/', views.get_schedule_data, name='get_schedule_data'),
    path('redirect/<str:item_no>/', views.redirect_to_detail, name='redirect_to_detail'),
]