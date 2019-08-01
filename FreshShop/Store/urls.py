from django.urls import path, re_path
from Store.views import *

urlpatterns = [
    path('register/', register),
    path('login/', login),
    path("logout/", logout),
    path("index/", index),
    re_path("index/", index),
    path("base/", base),
    path("register_store/", register_store),
    path("add_goods/", add_goods),
    re_path(r"list_goods/(?P<state>\w+)", list_goods),
    re_path("update_goods/(?P<goods_id>\d+)", update_goods),
    re_path("set_goods/(?P<state>\w+)/", set_goods),
    path(r'list_goods_type/', list_goods_type),
    path(r'delete_goods_type/', delete_goods_type),
    path("order_list/", order_list),
    re_path(r"order_list/(?P<state>\w+)", order_list),
    re_path("set_order/(?P<state>\w+)/", set_order),
    path('agl/', ajax_goods_list),
    path('get_add/', get_add),
]
