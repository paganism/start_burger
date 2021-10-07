from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views


from foodcartapp.models import Product, Restaurant
from foodcartapp.models import Order, OrderItem, RestaurantMenuItem
from django.db.models.query import Prefetch
from geopy.distance import geodesic
import requests
from coordinates.models import Coordinates
from foodcartapp.coordinates_api_functions import (
    fetch_coordinates, parse_coordinates
)
from django.conf import settings
from django.db.models import OuterRef, Subquery


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    default_availability = {restaurant.id: False for restaurant in restaurants}
    products_with_restaurants = []
    for product in products:

        availability = {
            **default_availability,
            **{item.restaurant_id: item.availability for item in product.menu_items.all()},
        }
        orderer_availability = [availability[restaurant.id] for restaurant in restaurants]

        products_with_restaurants.append(
            (product, orderer_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurants': products_with_restaurants,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


def get_distance_for_address(order, restaurant):
    rest_long, rest_lat = parse_coordinates(restaurant.coordinates)

    if not (order.long and order.lat):
        try:
            order.long, order.lat = fetch_coordinates(
                settings.YA_API_KEY,
                order.address
            )
            Coordinates.objects.create(
                address=order.address,
                long=order.long,
                lat=order.lat,
            )
        except (
            requests.exceptions.ReadTimeout,
            requests.exceptions.ConnectionError,
            requests.exceptions.HTTPError
        ):
            return

    return round(
        (geodesic((rest_lat, rest_long), (order.lat, order.long)).km), 2
    )


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):

    subquery_long = Subquery(Coordinates.objects.filter(address=OuterRef('address')).values('long'))
    subquery_lat = Subquery(Coordinates.objects.filter(address=OuterRef('address')).values('lat'))

    orders = Order.objects.annotate_with_price().select_related('restaurant') \
        .prefetch_related(Prefetch(
            'items', queryset=OrderItem.objects.select_related('product')
        )).exclude(status='CLOSED') \
        .order_by('-id')

    orders_with_coord = orders.annotate(long=subquery_long).annotate(lat=subquery_lat)

    orders_list = []
    for order in orders_with_coord:
        avail_restaurants = []
        
        for item in order.items.all():
            item_restaurants = []

            menu_items = RestaurantMenuItem.objects.select_related('product') \
                .filter(
                product=item.product,
                availability=True
            ).select_related('restaurant')
            for menu_item in menu_items:
                item_restaurants.append(menu_item.restaurant)
            if not avail_restaurants:
                avail_restaurants += item_restaurants

            avail_restaurants = list(set(item_restaurants) & set(avail_restaurants))
        
        rest_distance = []
        for restaurant in avail_restaurants:
            distance = get_distance_for_address(order, restaurant)
            rest_distance.append(
                {
                    'name': restaurant.name,
                    'distance': distance,
                }
            )

        order.restaurants = sorted(rest_distance, key=lambda x: x['distance'])
        orders_list.append(order)

        
    return render(request, template_name='order_items.html', context={
        'order_items': orders_list
    })
