import hashlib
from django.shortcuts import render, HttpResponseRedirect
from Store.models import *
from django.core.paginator import Paginator
from Buyer.models import *

from rest_framework import viewsets
from Store.serializer import *
from django_filters.rest_framework import DjangoFilterBackend

def set_password(password):
    md5 = hashlib.md5()
    md5.update(password.encode())
    result = md5.hexdigest()
    return result


def loginValid(fun):
    def inner(request, *args, **kwargs):
        c_user = request.COOKIES.get("username")
        s_user = request.session.get("username")
        if c_user and s_user and c_user == s_user:
            return fun(request, *args, **kwargs)
        else:
            return HttpResponseRedirect("/Store/login/")
    return inner


def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        if username and password:
            seller = Seller()
            seller.username = username
            seller.password = set_password(password)
            seller.nickname = username
            seller.save()
            return HttpResponseRedirect("/Store/login")
    return render(request, "store/register.html")


def login(request):
    response = render(request, "store/login.html")
    response.set_cookie("login_from", "login_page")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        if username and password:
            user = Seller.objects.filter(username=username).first()
            if user:
                web_password = set_password(password)
                cookies = request.COOKIES.get("login_from")
                if web_password == user.password and cookies == "login_page":
                    response = HttpResponseRedirect("/Store/index/")
                    response.set_cookie("username", username)
                    request.session["username"] = username
                    response.set_cookie("user_id", user.id)

                    store = Store.objects.filter(user_id=user.id).first()
                    if store:
                        response.set_cookie("has_store", store.id)
                    else:
                        response.set_cookie("has_store", "")
                    return response
    return response


@loginValid
def index(request):
    return render(request, "store/index.html")


def base(request):
    return render(request, "store/base.html")


@loginValid
def register_store(request):
    type_list = StoreType.objects.all()
    if request.method == "POST":
        post_data = request.POST
        store_name = post_data.get("store_name")
        store_description = post_data.get("store_description")
        print(store_description)
        store_phone = post_data.get("store_phone")
        store_money = post_data.get("store_money")
        store_address = post_data.get("store_address")

        user_id = int(request.COOKIES.get("user_id"))
        type_lists = post_data.getlist("type")
        print(type_lists)
        store_logo = request.FILES.get("store_logo")

        store = Store()
        store.store_name = store_name
        store.store_description = store_description
        store.store_phone = store_phone
        store.store_money = store_money
        store.store_address = store_address
        store.user_id = user_id
        store.store_logo = store_logo
        store.save()

        for i in type_lists:
            store_type = StoreType.objects.get(id=i)
            store.type.add(store_type)
        store.save()

        response = HttpResponseRedirect("/Store/index/")
        response.set_cookie("has_store", store.id)
        return response
    return render(request, "store/register_store.html", locals())


@loginValid
def add_goods(request):
    goods_type_list = GoodsType.objects.all()
    if request.method == "POST":
        goods_name = request.POST.get("goods_name")
        goods_price = request.POST.get("goods_price")
        goods_number = request.POST.get("goods_number")
        goods_description = request.POST.get("goods_description")
        goods_date = request.POST.get("goods_date")
        goods_safeDate = request.POST.get("goods_safeDate")
        goods_type = request.POST.get("goods_type")

        goods_store = request.COOKIES.get("has_store")
        goods_image = request.FILES.get("goods_image")

        goods = Goods()
        goods.goods_name = goods_name
        goods.goods_price = goods_price
        goods.goods_number = goods_number
        goods.goods_description = goods_description
        goods.goods_date = goods_date
        goods.goods_safeDate = goods_safeDate
        goods.goods_image = goods_image
        goods.goods_type = GoodsType.objects.get(id=int(goods_type))
        goods.store_id = Store.objects.get(id=int(goods_store))
        goods.save()

        return HttpResponseRedirect("/Store/list_goods/up")
    return render(request, "store/add_goods.html", locals())


@loginValid
def list_goods(request, state):
    if state == "up":
        state_num = 1
    else:
        state_num = 0
    keywords = request.GET.get("keywords", "")
    page_num = request.GET.get("page_num", 1)
    store_id = request.COOKIES.get("has_store")
    store = Store.objects.get(id=int(store_id))
    if keywords:
        goods_list = store.goods_set.filter(goods_name__contains=keywords, goods_under=state_num)
    else:
        goods_list = store.goods_set.filter(goods_under=state_num)

    paginator = Paginator(goods_list, 3)
    page = paginator.page(int(page_num))
    page_range = paginator.page_range
    return render(request, "store/goods_list.html",
                  {"page": page, "page_range": page_range, "keywords": keywords, "state": state})


# @loginValid
# def goods(request, goods_id):
#     goods_data = Goods.objects.filter(id=goods_id).first()
#     return render(request, "store/goods.html", locals())


@loginValid
def update_goods(request, goods_id):
    goods_data = Goods.objects.filter(id=goods_id).first()
    if request.method == "POST":
        goods_name = request.POST.get("goods_name")
        goods_price = request.POST.get("goods_price")
        goods_number = request.POST.get("goods_number")
        goods_description = request.POST.get("goods_description")
        goods_date = request.POST.get("goods_date")
        goods_safeDate = request.POST.get("goods_safeDate")
        goods_image = request.FILES.get("goods_image")

        goods = Goods.objects.get(id=int(goods_id))
        goods.goods_name = goods_name
        goods.goods_price = goods_price
        goods.goods_number = goods_number
        goods.goods_description = goods_description
        goods.goods_date = goods_date
        goods.goods_safeDate = goods_safeDate
        if goods_image:
            goods.goods_image = goods_image
        goods.save()
        return HttpResponseRedirect("/Store/goods/%s" % goods_id)
    return render(request, "store/update_goods.html", locals())


@loginValid
def list_goods_type(request):
    goods_type_list = GoodsType.objects.all()
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        picture = request.FILES.get("picture")

        goods_type = GoodsType()
        goods_type.name = name
        goods_type.description = description
        goods_type.picture = picture
        goods_type.save()
    return render(request, "store/goods_type_list.html", locals())



@loginValid
def delete_goods_type(request):
    id = int(request.GET.get("id"))
    goods = GoodsType.objects.get(id=id)
    goods.delete()
    return HttpResponseRedirect("/Store/list_goods_type/")


def set_goods(request, state):
    if state == "up":
        state_num = 1
    else:
        state_num = 0
    id = request.GET.get("id")
    referer = request.META.get("HTTP_REFERER")
    if id:
        goods = Goods.objects.filter(id=id).first()
        if state == "delete":
            goods.delete()
        else:
            goods.goods_under = state_num
            goods.save()
    return HttpResponseRedirect(referer)


def logout(request):
    response = HttpResponseRedirect("/Store/login")
    for key in request.COOKIES:
        response.delete_cookie(key)
    return response


def order_list(request):
    store_id = request.COOKIES.get("has_store")
    order_list = OrderDetail.objects.filter(order_id__order_status=2, goods_store=store_id)

    return render(request, "store/order_list.html", locals())


def set_order(request, state):
    if state == "shipment":
        state_num = 2
    elif state == "repulse":
        state_num = 5
    order_id = request.GET.get("order_id")
    referer = request.META.get("HTTP_REFERER")
    if order_id:
        order = Order.objects.filter(order_id=order_id).first()
        order.order_status = state_num
        order.save()
    return HttpResponseRedirect(referer)



# ViewSets define the view behavior
class UserViewSet(viewsets.ModelViewSet):
    queryset = Goods.objects.all()  # 具体返回的数据
    serializer_class = UserSerializer  # 指定过滤的类

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['goods_name', 'goods_price']

class TypeViewSet(viewsets.ModelViewSet):
    queryset = GoodsType.objects.all()
    serializer_class = GoodsTypeSerializer


def ajax_goods_list(request):
    return render(request, 'store/ajax_goods_list.html')


from CeleryTask.tasks import add
from django.http import JsonResponse

def get_add(request):
    add.delay(2, 3)
    return JsonResponse({"statue": 200})
















