from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets
from rest_framework.viewsets import ModelViewSet

from main.models import Food, FoodCategory, User, Addition
from main.serializers import FoodCategorySerializer, UserSerializer, AdditionSerializer, \
    FoodSerializer


# Create your views here.
@extend_schema_view(
    list=extend_schema(summary="Список всех блюд"),
    retrieve=extend_schema(summary="Получение одного блюда"),
    create=extend_schema(summary="Создание блюда")
)
@extend_schema(
    parameters=[]
)
class FoodViewSet(ModelViewSet):
    queryset = Food.objects.all()
    serializer_class = FoodSerializer

    def get_queryset(self):
        params = self.request.query_params
        foods = Food.objects.all()
        if params:
            if params.get('category'):
                foods = Food.objects.filter(category__id=params.get('category'))

        return foods


class CategoryViewSet(ModelViewSet):
    queryset = FoodCategory.objects.all()
    serializer_class = FoodCategorySerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class AdditionsViewSet(viewsets.ModelViewSet):
    queryset = Addition.objects.all()
    serializer_class = AdditionSerializer
