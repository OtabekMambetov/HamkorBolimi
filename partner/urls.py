from django.urls import path
from . import views

urlpatterns = [
    path('', views.partner_home, name='partner_home'),
    path('statistics/', views.partner_statistics, name='partner_statistics'),
]
