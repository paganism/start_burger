from django.templatetags.static import static

from .models import Order, OrderItem
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Product
from rest_framework import serializers
from django.http import JsonResponse
from django.db import transaction


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            },
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


class OrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']


class OrderSerializer(serializers.ModelSerializer):

    products = OrderItemSerializer(many=True, allow_empty=False)
    firstname = serializers.CharField(source='customer_first_name')
    lastname = serializers.CharField(source='customer_last_name')

    class Meta:
        model = Order
        fields = [
            'firstname', 'lastname', 'phonenumber',
            'address', 'products'
        ]


@transaction.atomic
@api_view(["POST"])
def register_order(request):
    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)  # выкинет ValidationError

    order = Order.objects.create(
        customer_first_name=serializer.validated_data['customer_first_name'],
        customer_last_name=serializer.validated_data['customer_last_name'],
        address=serializer.validated_data['address'],
        phonenumber=serializer.validated_data['phonenumber']
    )
    products_fields = serializer.validated_data['products']

    for product in products_fields:
        OrderItem.objects.create(
            order=order,
            product=product['product'],
            quantity=product['quantity'],
            price=product['quantity'] * product['product'].price
        )

    return Response(serializer.data, status=201)
