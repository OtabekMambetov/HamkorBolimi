from django.urls import path
from . import views

urlpatterns = [
    path('', views.customer_home, name='customer_home'),
    path('order/<int:product_id>/', views.place_order, name='place_order'),
]
