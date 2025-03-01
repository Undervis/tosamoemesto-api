from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models
from pytils.translit import translify, slugify


class User(AbstractUser):
    photo = models.ImageField(upload_to="user_photo", null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=11)
    addresses = models.ManyToManyField("Address")
    status = models.IntegerField(choices=[(1, "ACTIVE"), (0, "INACTIVE"), (2, "BANNED")], default=0,
                                 verbose_name="Статус пользователя")
    ban_reason = models.TextField(null=True, blank=True, verbose_name="Причина блокировки")
    ban_experienced_at = models.DateTimeField(null=True, blank=True)

    has_discount_card = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def is_birthday_today(self):
        return self.birthday.today() == datetime.today()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.first_name or self.last_name:
            self.username = f"{translify(self.first_name)}{translify(self.last_name)}"


class Address(models.Model):
    address = models.CharField("Адрес", max_length=255)
    primary = models.BooleanField("Основной адрес", default=False)

    def __str__(self):
        return self.address

    class Meta:
        verbose_name = "Адрес"
        verbose_name_plural = "Адреса"


class FoodCategory(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    image = models.ImageField(upload_to='images/food_category', blank=True, null=True)

    def __str__(self):
        return self.title


    def get_food_in_count(self):
        return Food.objects.filter(category=self).count()


class Food(models.Model):
    title = models.CharField(max_length=96)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="images/food", blank=True, null=True)
    category = models.ForeignKey("FoodCategory", on_delete=models.CASCADE, null=True)
    cooking_time = models.IntegerField(blank=True, null=True, default=0)
    accepted_additions = models.ManyToManyField("Addition", blank=True)
    active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    sizes_and_prices = models.ManyToManyField("SizeAndPrice")

    def __str__(self):
        return self.title

    def get_rate(self):
        return FoodFeedback.objects.filter(food=self).aggregate(models.Avg('rating'))['rating__avg']


class Addition(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='images/food_addition', null=True, blank=True)

    def __str__(self):
        return self.title


class FoodFeedback(models.Model):
    text = models.TextField()
    rate = models.FloatField(blank=True, null=True, default=5)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)

    attachments = models.ManyToManyField("Attachment", blank=True)

    def __str__(self):
        return self.text


class Order(models.Model):
    order_items = models.ManyToManyField("Ordering")
    address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True)

    def get_order_weight(self):
        return self.order_items.aggregate(models.Sum('weight'))['weight__sum']

    def get_pre_discount_price(self):
        return self.order_items.all().aggregate(models.Sum('price'))['price__sum'] + \
            self.order_items.model.additions.all().aggregate(models.Sum('price'))['price__sum']

    def get_discount_price(self):
        pass


class Ordering(models.Model):
    main_order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    food = models.ForeignKey(Food, on_delete=models.CASCADE, null=True)
    additions = models.ManyToManyField(Addition, through="AdditionEnrollment", blank=True)
    size = models.ForeignKey("SizeAndPrice", on_delete=models.CASCADE, null=True)
    count = models.IntegerField(default=1)


class AdditionEnrollment(models.Model):
    ordering = models.ForeignKey(Ordering, on_delete=models.CASCADE)
    addition = models.ForeignKey(Addition, on_delete=models.CASCADE, null=True)
    count = models.IntegerField(default=1)


class Banner(models.Model):
    title = models.CharField("Название", max_length=100)
    image = models.ImageField("Изображение", upload_to='banner_images')
    status = models.IntegerField("Статус", choices=[(1, "ACTIVE"), (0, "INACTIVE"), (2, "POSTPONED")])
    show_date_start = models.DateTimeField("Дата начала отображения", null=True, blank=True)
    show_date_end = models.DateTimeField("Дата окончания отображения", null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Баннер"
        verbose_name_plural = "Баннеры"


class SizeAndPrice(models.Model):
    title = models.CharField("Подпись к размеру", max_length=48)
    size = models.IntegerField("Размер", default=0)
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    weight = models.IntegerField("Вес", default=0)

    def __str__(self):
        return f"{self.size} - {self.price}"

    class Meta:
        verbose_name = "Размер и цена"
        verbose_name_plural = "Размеры и цены"


class Discount(models.Model):
    title = models.CharField("Название акции", max_length=100)
    description = models.TextField("Описание акции")
    banner = models.ForeignKey(Banner, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Баннер")

    condition = models.ForeignKey("DiscountCondition", on_delete=models.CASCADE, blank=True,
                                  verbose_name="Условия акции")

    status_choices = [(1, "ACTIVE"), (0, "INACTIVE"), (2, "POSTPONED")]
    status = models.IntegerField("Статус акции", choices=status_choices)

    discount_value = models.DecimalField(decimal_places=2, max_digits=3)

    created_at = models.DateTimeField("Дата начала акции", null=True, blank=True)
    expires_at = models.DateTimeField("Дата окончания акции", null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['status', '-created_at']
        verbose_name = "Акция"
        verbose_name_plural = "Акции"

    def is_active_now(self):
        import datetime
        now = datetime.datetime.now()

        if self.status != 1:
            return False

        if self.created_at and now < self.created_at:
            return False
        if self.expires_at and now > self.expires_at:
            return False

        return True

    def is_applicable_for_order(self, order, user=None):
        """
        Проверяем, применима ли данная скидка к заказу:
         1. Акция активна.
         2. Условие (discount condition) выполнено.
        """
        if not self.is_active_now():
            return False

        if self.condition:
            if not self.condition.is_applicable(order, user=user):
                return False

        return True

    def get_discount_amount(self, order):
        """
        Возвращает абсолютное значение скидки в деньгах (рублях и т.д.),
        исходя из discount_value и order.total_price (пример).
        """
        if not self.discount_value:
            return 0.0
        return (order.get_pre_discount_price() * self.discount_value) / 100.0


class DiscountCondition(models.Model):
    title = models.CharField("Название", max_length=100)
    min_order_price = models.FloatField(null=True, blank=True, default=None, verbose_name="Минимальная цена заказа")
    min_order_weight = models.FloatField(null=True, blank=True, default=None, verbose_name="Минимальный вес заказа")
    food_categories = models.ManyToManyField("FoodCategory", verbose_name="Категории блюд", blank=True)
    foods = models.ManyToManyField("Food", verbose_name="Блюда", blank=True)
    food_size = models.IntegerField(null=True, blank=True)
    user_role = models.ManyToManyField(User, blank=True, default=None, verbose_name="Роли пользователей")
    discount_card = models.BooleanField(default=False, null=True, blank=True, verbose_name="Карта лояльности")
    birthday = models.BooleanField(default=False, null=True, blank=True, verbose_name="День рождения")
    ordering_time_start = models.TimeField(null=True, blank=True, verbose_name="Начало периода времени заказа")
    ordering_time_end = models.TimeField(null=True, blank=True, verbose_name="Окончание периода времени заказа")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Условие акции"
        verbose_name_plural = "Условия акций"

    def is_applicable(self, order, user):
        """
        Логика проверки, применимо ли данное условие к конкретному заказу и пользователю.
        Возвращает True/False.
        """
        # 1. Проверяем минимальную стоимость заказа
        if self.min_order_price is not None:
            if order.get_pre_discount_price() < self.min_order_price:
                return False

        # 2. Проверяем минимальный вес
        if self.min_order_weight is not None:
            if order.get_order_weight() < self.min_order_weight:
                return False

        # 3. Проверяем категории блюд (если указаны),
        #    должны ли ВСЕ блюда входить в эти категории или хотя бы одно?
        #    Это зависит от вашей бизнес-логики.
        #    Ниже пример, если "хотя бы одно" блюдо из указанных категорий:
        if self.food_categories.exists():
            # Получаем все категории, которые есть в заказе
            categories_in_order = {item.food.category for item in order.order_items}
            # Смотрим пересечение
            valid_categories = set(self.food_categories.all())
            if categories_in_order.isdisjoint(valid_categories):
                return False

        # 4. Проверяем конкретные блюда (order_items)
        if self.foods.exists():
            # Аналогично, проверяем, что в заказе присутствует хотя бы одно блюдо из self.order_items
            foods_in_order = {item.food for item in order.order_items}
            valid_foods = set(self.foods.all())
            if foods_in_order.isdisjoint(valid_foods):
                return False

        # 5. Проверяем размер (food_size)
        if self.food_size is not None:
            # Если хотя бы одно блюдо в заказе с нужным размером — пускаем
            sizes_in_order = {item.size for item in order.order_items}
            if self.food_size not in sizes_in_order:
                return False

        # 6. Проверяем роль пользователя (user_role)
        #    Если user_role указаны, значит текущий user должен быть среди них
        if self.user_role.exists():
            if user.groups not in self.user_role.all():
                return False

        # 7. Проверяем наличие discount_card
        #    Допустим, в профиле пользователя или где-то хранится флаг `has_discount_card`
        if self.discount_card:
            if not user.has_discount_card:
                return False

        # 8. Проверяем день рождения
        #    Допустим, логика: если user.profile.birthday == сегодня -> True
        #    Реализуйте, как именно вы определяете "день рождения".
        if self.birthday:
            if not user.is_birthday_today():
                return False

        return True


class Attachment(models.Model):
    file = models.FileField("Файл", upload_to='attachments')

    type_choice = [(0, "IMAGE"), (1, "VIDEO")]
    type = models.IntegerField(choices=type_choice, default=0, verbose_name="Тип вложения")

    def __str__(self):
        return self.file.name

    class Meta:
        verbose_name = "Вложение"
        verbose_name_plural = "Вложения"


class Chat(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owner")
    dialogue_with = models.ForeignKey(User, on_delete=models.CASCADE, related_name="dialogue_with")

    created_at = models.DateTimeField(auto_now_add=True)

    def get_last_message(self):
        return Message.objects.filter(chat=self).order_by('-created_at').first()

    def __str__(self):
        return f'{self.owner} {self.dialogue_with}'


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    is_read = models.BooleanField(default=False)
    attachments = models.ManyToManyField(Attachment, blank=True)

    def __str__(self):
        return f'{self.sender} {self.message}'
