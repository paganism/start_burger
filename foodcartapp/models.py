from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import Sum, F
from django.utils import timezone
from django.conf import settings
from foodcartapp.coordinates_api_functions import (
    fetch_coordinates, parse_coordinates
)
from geopy.distance import geodesic
import requests
from coordinates.models import Coordinates


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )
    coordinates = models.JSONField(verbose_name='Координаты')

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):
    def annotate_with_price(self):
        return self.annotate(
            order_price=Sum(F('items__product__price') * F('items__quantity'))
        )


class Order(models.Model):
    STATUS_CHOICES = [
        ('NEW', 'Новый'),
        ('IN_PROGRESS', 'В работе'),
        ('CLOSED', 'Завершён'),
    ]
    PAYMENT_CHOICES = [
        ('NON_CACHE', 'Электронно'),
        ('CACHE', 'Наличностью'),
        ('', ''),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='NEW',
        verbose_name='Статус',
        db_index=True
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_CHOICES,
        default='',
        verbose_name='Способ оплаты',
        db_index=True,
        blank=True
    )
    address = models.TextField(
        verbose_name='Адрес доставки'
    )
    customer_first_name = models.CharField(
        max_length=50,
        verbose_name='Имя'
    )
    customer_last_name = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Фамилия'
    )
    phonenumber = PhoneNumberField(
        verbose_name='Мобильный номер',
        db_index=True
    )
    comment = models.TextField(
        verbose_name='Комментарий',
        blank=True
    )
    registrated_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='дата регистрации',
        db_index=True
    )
    called_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='время звонка',
        db_index=True
    )
    delivered_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='время доставки',
        db_index=True
    )
    restaurant = models.ForeignKey(
        Restaurant,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='ресторан',
        related_name='orders'
    )
    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f"{self.id} {self.customer_first_name} {self.address}"

    def get_available_restaurants_for_cart(self):
        restaurants = []
        for item in self.items.all():
            item_restaurants = []
            menu_items = RestaurantMenuItem.objects.filter(
                product=item.product,
                availability=True
            )
            for menu_item in menu_items:
                item_restaurants.append(menu_item.restaurant)
            if not restaurants:
                restaurants += item_restaurants
            restaurants = list(set(item_restaurants) & set(restaurants))
        return restaurants

    def get_distance_for_address(self, restaurant):
        rest_long, rest_lat = parse_coordinates(restaurant.coordinates)

        client_coordinates_objects = Coordinates.objects.filter(
            address=self.address
        )

        if client_coordinates_objects.first():
            coordinates = client_coordinates_objects.first()
            client_long = coordinates.long
            client_lat = coordinates.lat

        else:
            try:
                client_long, client_lat = fetch_coordinates(
                    settings.YA_API_KEY,
                    self.address
                )
                Coordinates.objects.create(
                    address=self.address,
                    long=client_long,
                    lat=client_lat,
                )
            except (
                requests.exceptions.ReadTimeout,
                requests.exceptions.ConnectionError,
                requests.exceptions.HTTPError
            ):
                return

        return round(
            (geodesic((rest_lat, rest_long), (client_lat, client_long)).km), 2
        )

    def get_distance_for_order(self):

        if self.restaurant:
            return self.get_distance_for_address(self.restaurant)

        avail_restaurants = self.get_available_restaurants_for_cart()

        rest_distance = []

        for restaurant in avail_restaurants:
            distance = self.get_distance_for_address(restaurant)
            rest_distance.append(
                {
                    'name': restaurant.name,
                    'distance': distance
                }
            )
        return sorted(rest_distance, key=lambda x: x['distance'])


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name='items',
        on_delete=models.CASCADE,
        verbose_name='заказ'
    )
    product = models.ForeignKey(
        Product,
        related_name='order_items',
        on_delete=models.CASCADE,
        verbose_name='Товар'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name='Количество',
        validators=[MinValueValidator(1), MaxValueValidator(50)]
    )
    price = models.DecimalField(
        verbose_name='цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    class Meta:
        verbose_name = 'Элемент заказа'
        verbose_name_plural = 'Элементы заказа'

    def __str__(self):
        return f"\
            {self.product.name} \
            {self.order.customer_first_name} \
            {self.order.customer_last_name} \
            {self.order.address[:50]}"
