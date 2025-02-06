from django.http import HttpResponse
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PartnerViewSet, ProductViewSet, CategoryListCreate


def home_view(request):
    return HttpResponse("<h1>Welcome to the homepage!</h1>")

router = DefaultRouter()
router.register(r'partners', PartnerViewSet)
router.register(r'products', ProductViewSet)

urlpatterns = [
    path('categories/', CategoryListCreate.as_view(), name='category-list-create'),
    path('api/', include(router.urls)),
    path("", home_view, name="home"),  # Asosiy sahifa uchun yo‘nalish
]

