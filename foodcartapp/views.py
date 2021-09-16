from django.http import JsonResponse
from django.templatetags.static import static
import phonenumbers
from .models import Order, OrderItem
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST
)

from .models import Product
from django.core.exceptions import ObjectDoesNotExist
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


@transaction.atomic
@permission_classes((AllowAny,))
@api_view(["POST"])
def register_order(request):

    order = request.data

    # Нет ключей order
    if not 'firstname' in order \
        and not 'lastname' in order \
            and not 'phonenumber' in order \
                and not 'address' in order:
        return Response(
            {'error': 'there are no order data'},
            status=HTTP_400_BAD_REQUEST
        )

    # Все ключи не null
    if order.get('firstname') is None \
        and order.get('lastname') is None \
            and order.get('address') is None \
            and order.get('phonenumber') is None:
        return Response(
            {'error': 'firstname, lastname, \
                phonenumber, address cannot be empty'},
            status=HTTP_400_BAD_REQUEST
        )

    # firstname не список
    if not isinstance(order['firstname'], str):
        return Response(
            {'error': 'firstname Not a valid string'},
            status=HTTP_400_BAD_REQUEST
        )

    # firstname не пустое
    if order['firstname'] is None:
        return Response(
            {'error': 'firstname cannot be empty'},
            status=HTTP_400_BAD_REQUEST
        )

    # phonenumber не пустой
    if not order['phonenumber']:
        return Response(
            {'error': 'phonenumber cannot be empty'},
            status=HTTP_400_BAD_REQUEST
        )

    # phonenumber валиден
    phonenumber = phonenumbers.parse(order['phonenumber'])
    if not phonenumbers.is_valid_number(phonenumber):
        return Response(
            {'error': 'phonenumber is invalid'},
            status=HTTP_400_BAD_REQUEST
        )

    # Продукты должны присутствовать в наборе данных
    try:
        order['products']
    except KeyError:
        return Response(
            {'error': 'there are no products'},
            status=HTTP_400_BAD_REQUEST
        )

    # Продукты - не пустой список
    if isinstance(order['products'], list) and len(order['products']) == 0:
        return Response(
            {'error': 'products are empty'},
            status=HTTP_400_BAD_REQUEST
        )

    # Продукты - это не null
    if order['products'] is None:
        return Response(
            {'error': 'products are null'},
            status=HTTP_400_BAD_REQUEST
        )

    # Продукты - это список
    if not isinstance(order['products'], list):
        return Response(
            {'error': 'products key is not presented or not list'},
            status=HTTP_400_BAD_REQUEST
        )

    # Проверка на существование products
    for item in order['products']:
        try:
            OrderItem.objects.get(product_id=item['product'])
        except ObjectDoesNotExist:
            return Response(
                {'error': 'product id not found'},
                status=HTTP_400_BAD_REQUEST
            )

    order_object = Order.objects.create(
        customer_first_name=order['firstname'],
        customer_last_name=order['lastname'],
        address=order['address'],
        phonenumber=order['phonenumber']
    )

    for item in order['products']:
        order_item = OrderItem.objects.create(
            order=order_object,
            product_id=item['product'],
            quantity=item['quantity']
        )
        order_item.save()

    return Response(data={}, status=HTTP_200_OK)
