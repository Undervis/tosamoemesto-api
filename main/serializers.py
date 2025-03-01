from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from main.models import Food, User, Address, FoodCategory, Addition, FoodFeedback, Order, SizeAndPrice


class FoodCategorySerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = FoodCategory
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['count_in'] = instance.get_food_in_count()
        return data


class AdditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Addition
        fields = '__all__'


class SizesAndPricesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SizeAndPrice
        fields = '__all__'


class FoodSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=FoodCategory.objects.all())
    accepted_additions = serializers.PrimaryKeyRelatedField(many=True, queryset=Addition.objects.all())
    sizes_and_prices = SizesAndPricesSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Food
        fields = '__all__'
        depth = 1

    def create(self, validated_data):
        food = Food.objects.create(title=validated_data['title'],
                                   cooking_time=validated_data['cooking_time'],
                                   category=validated_data['category'], image=validated_data['image'],
                                   description=validated_data['description'], active=validated_data['active'])
        for size in validated_data['sizes_and_prices']:
            food.sizes_and_prices.create(**size)
        for addition in validated_data['accepted_additions']:
            food.accepted_additions.add(addition)
        food.save()
        return food

    def update(self, instance, validated_data):
        print(validated_data)
        food = instance
        food.category = validated_data['category']
        food.description = validated_data['description']
        food.active = validated_data['active']
        try:
            food.image = validated_data['image']
        except KeyError:
            pass
        food.cooking_time = validated_data['cooking_time']
        food.sizes_and_prices.all().delete()
        for size in validated_data['sizes_and_prices']:
            food.sizes_and_prices.create(**size)
        food.accepted_additions.set(validated_data['accepted_additions'])
        food.save()
        return food


    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['category'] = FoodCategorySerializer(instance.category).data
        data['accepted_additions'] = AdditionSerializer(instance.accepted_additions.all(), many=True).data
        try:
            data['created_by'] = {"id": instance.created_by.id, 'username': instance.created_by.username}
        except AttributeError:
            data['created_by'] = "Anonymous"
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'


class FoodFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodFeedback
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
