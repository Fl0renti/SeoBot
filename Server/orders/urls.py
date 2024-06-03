from django.urls import path
from .views import *


app_name = 'orders'
urlpatterns = [
    # Order routes
    path("", ViewOrders.as_view(), name="list_of_orders"),
    path("result1", ViewKeyword.as_view(), name="ViewKeyword"),
    path('update-action/', update_order_action, name='update-action'),

    path("order/new/", CreateNewOrder.as_view(), name="create_order"),
    path("order/<int:pk>/delete/", DeleteOrder.as_view(), name="delete_order"),
    path("order/<int:pk>/update/", UpdateOrder.as_view(), name="update_order"),
    # Profile route
    path("profiles", ViewProfiles.as_view(), name="profile"),
    path("profile/new/", CreateNewProfile.as_view(), name="create_profile"),
    path("profile/<int:pk>/delete/", DeleteProfile.as_view(), name="delete_profile"),
    path("profile/<int:pk>/update/", UpdateProfile.as_view(), name="update_profile"),

    # API route
    path("api/get/orders/web", get_orders_web),
    path("api/get/random/user/web/<int:no>",get_random_proxy_details_web),
    path("api/get/random/user/mobile/<int:no>",get_random_proxy_details_mobile),
    path("api/get/orders/mobile", get_orders_mobile),
    path('update-reached-users/<int:pk>/', update_reached_users, name='update_reached_users'),
    path('update-reached-users-incomplete/<int:pk>/', update_reached_users_incomplete),
    path("api/set/profile/free/<int:pk>/",setProfileFree),
    path("api/get/number/of/profiles",get_number_of_profile_mobile),

    path('api/update-reached-numbers/<int:order_id>/', update_reached_users, name='update_reached_users'),
]