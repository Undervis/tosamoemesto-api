from django.urls import path

from main import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'food', views.FoodViewSet)
router.register(r'category', views.CategoryViewSet)
router.register(r'user', views.UserViewSet)
router.register(r'addition', views.AdditionsViewSet)

urlpatterns = router.urls