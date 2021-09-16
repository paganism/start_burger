from django.http import JsonResponse
from django.templatetags.static import static
import json
from .models import Order, OrderItem
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST
)

from .models import Product


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


@permission_classes((AllowAny,))
@api_view(["POST"])
def register_order(request):
    order = request.data
    order_object = Order.objects.create(
        customer_first_name=order['firstname'],
        customer_last_name=order['lastname'],
        address=order['address'],
        phonenumber=order['phonenumber']
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

    for item in order['products']:
        order_item = OrderItem.objects.create(
            order=order_object,
            product_id=item['product'],
            quantity=item['quantity']
        )
        order_item.save()

    return Response(data={}, status=HTTP_200_OK)
