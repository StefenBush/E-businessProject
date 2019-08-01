from django.shortcuts import render,HttpResponseRedirect
from django.http import HttpResponse,JsonResponse
import time

from django.core.paginator import Paginator
from Buyer.models import *
from Store.views import set_password
from Store.models import *

from alipay import AliPay


def loginValid(fun):
    def inner(request, *args, **kwargs):
        c_user = request.COOKIES.get("username")
        s_user = request.session.get("username")
        if c_user and s_user and c_user == s_user:
            return fun(request, *args, **kwargs)
        else:
            return HttpResponseRedirect("/Buyer/login/")
    return inner


def register(request):
    if request.method == "POST":
        username = request.POST.get("user_name")
        password = request.POST.get("pwd")
        email = request.POST.get("email")

        buyer = Buyer()
        buyer.username = username
        buyer.password = set_password(password)
        buyer.email = email
        buyer.save()

        return HttpResponseRedirect("/Buyer/login/")
    return render(request, "buyer/register.html")


def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("pwd")
        if username and password:
            user = Buyer.objects.filter(username=username).first()
            if user:
                web_password = set_password(password)
                if user.password == web_password:
                    response = HttpResponseRedirect("/Buyer/index/")
                    response.set_cookie("username", user.username)
                    request.session["username"] = user.username
                    response.set_cookie("user_id", user.id)
                    return response
    return render(request, "buyer/login.html")


@loginValid
def index(request):
    result_list = []
    goods_type_list = GoodsType.objects.all()
    for goods_type in goods_type_list:
        goods_list = goods_type.goods_set.values()[:4]
        if goods_list:
            goodsType = {
                "id": goods_type.id,
                "name": goods_type.name,
                "description": goods_type.description,
                "picture": goods_type.picture,
                "goods_list": goods_list
            }
            result_list.append(goodsType)
    return render(request, "buyer/index.html", locals())


@loginValid
def goods_list(request):
    goodsList = []
    type_id = request.GET.get("type_id")
    goods_type = GoodsType.objects.filter(id=type_id).first()
    if goods_type:
        goodsList = goods_type.goods_set.filter(goods_under=1)
    return render(request, "buyer/goods_list.html", locals())


def logout(request):
    response = HttpResponseRedirect("/Buyer/login/")
    for key in request.COOKIES:
        response.delete_cookie(key)
    del request.session["username"]
    return response


def base(request):
    return render(request, "buyer/base.html")


def pay_result(request):
    return render(request, "buyer/pay_result.html", locals())


def pay_order(request):
    money = request.GET.get("money")
    order_id = request.GET.get("order_id")

    alipay_public_key_string = """-----BEGIN PUBLIC KEY-----
    MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2S+kYwi9NbLqou7G3bzQUuqkdGpGHlSD6ro7xq3D4nE7gPV6WeP4gWVcOeSPMFDuHmTtAaV6TLM8/K8AB7VH5BvQIlfCndrknjqLU1R4dB4Q+MLBS6IjizKkfBkk3Ebra9xBJidDB5Rlraj1sgrFTGg2tLt70Tuol6A4/0SVeTn5MDR67m5ug11DJsA/jy6zakwonE7YklqMBmZU1FxtMgvFAsv7/iYnAtREsSWpdWNdG+cJg0afBwm7E7SGUEEwDwMxeQQDSbJizn6qxhKNvA1zULvxkf5LZLkyqLDg4ZrhNbD05kwSDUDcDtbgKk1aI9sg7J6ojCXj+X12Hn1tLwIDAQAB
    -----END PUBLIC KEY-----"""

    app_private_key_string = """-----BEGIN RSA PRIVATE KEY-----
    MIIEpAIBAAKCAQEA2S+kYwi9NbLqou7G3bzQUuqkdGpGHlSD6ro7xq3D4nE7gPV6WeP4gWVcOeSPMFDuHmTtAaV6TLM8/K8AB7VH5BvQIlfCndrknjqLU1R4dB4Q+MLBS6IjizKkfBkk3Ebra9xBJidDB5Rlraj1sgrFTGg2tLt70Tuol6A4/0SVeTn5MDR67m5ug11DJsA/jy6zakwonE7YklqMBmZU1FxtMgvFAsv7/iYnAtREsSWpdWNdG+cJg0afBwm7E7SGUEEwDwMxeQQDSbJizn6qxhKNvA1zULvxkf5LZLkyqLDg4ZrhNbD05kwSDUDcDtbgKk1aI9sg7J6ojCXj+X12Hn1tLwIDAQABAoIBAHzTkBTHehA6A/efazcYhVeSuvCaADEAfE1VunOHfbVRRVTqQecWSsb8HdS8U7v+V82qTjoLBM6+mcfVQRwtCePGRIroi9e0bn+uwFMlkpGSkkiXjwdMakdf1P/qZ7AfJsH4do1aNYFOvl3gZU5uOFWg9AhOVWy9cDmtgfTdU1e3dc6nvIDaCKW7HprExKEiLpaMj9yNdiaH2V0iQrIejMUIZF7iTRsVnmSWBdllfN1b9Jb59sDyIMqPUq8DT2NHIq+Zd9wRARkZnmDiXHJmZCdEM0qJgcyOVPcDFlMdxMH+1zbrXp49Rp5nynXcuPvweg8H4/swGjQH37mWtVSgi/ECgYEA+aevDcmRDfQ+tXF/2haPaBxzcz/g5TV5TzqTlBi2T9OSw3J76ho3V4WFXAouJtM+TSxJt0KInr4DfI5naB03V6G5XMwX1GDBlhTX6ePpzaMm4VWaeC8FqNl5fPsm1hOJj1hyy2F9AJA+cfmxIO7TeHc5zSjrduz5BvP4HuHYRScCgYEA3rS1K4OTY1/Wn/24EkwpVnV0dXCsfIAo8m/X5GCmdI5b6HE96rFiEv8qCsti7rJ6TZRuJjn3jEsQAk1k45jIp5OA5hyFOTSswfhJ7QxOBKCwubGycGh7ctE5aDmH5TjzWKKUQVz7kLgWdvUUrqo9ni0Dt/aXQgp9aL7gSm4hbLkCgYBjE/o0FY+coxcT+SRNT/C/17K1xV8id/NZzxxshNYtngC70j59LMRT1qiTW3Lvc5xhEjd7JEuF/FDz6Kv/NMEW5RbkThcS8QdC4ajCqPHL63jtqoRwN/EeDpjZUe8avIw2OFrufhUW2Sf/IaH7OOzx/RcSZa/09Zzq9n28+9JRtwKBgQChNmzjV/bMe+bwoAisbieKZ7HrBapG4btCbEX7Ex/LxfWwGLF6f/d/yuhTMhGmutof6K+nylRxYTDwibfbrZCrBfLMIJ8r3v6j1ykkiMC9RtlHQuPpzSh34A7PbL3757L4WZA6lKWiiC/y4sya969tHibP95hc/Rz1Qx83oeteOQKBgQDT2rPgLnrbH7YTkcdONWDhyhQjrP0hp0fKHxiim/SD8tI1cjeA14timp7SZzO6a5yMux22dKKx4QXhA0GUOS5QtQlsST/z4eFPMLjp5d6ThnVCBjZOta3ZNLwfUSYWcWP5vmTCLF/gBGIy8N78PKCXEX1pkmA4HKzWAirgZ2QiHg==
    -----END RSA PRIVATE KEY-----"""

    alipay = AliPay(
        appid="2016101000652500",
        app_notify_url=None,
        app_private_key_string=app_private_key_string,
        alipay_public_key_string=alipay_public_key_string,
        sign_type="RSA2"
    )

    order_string = alipay.api_alipay_trade_page_pay(
        out_trade_no=order_id,
        total_amount=str(money),
        subject="水果交易",
        return_url="http://127.0.0.1:8000/Buyer/pay_result/",
        notify_url="http://127.0.0.1:8000/Buyer/pay_result/",
    )


    order = Order.objects.get(order_id = order_id)
    order.order_status = 2
    order.save()

    return HttpResponseRedirect("https://openapi.alipaydev.com/gateway.do?" + order_string)


def goods_detail(request):
    goods_id = request.GET.get("goods_id")
    if goods_id:
        goods = Goods.objects.filter(id=goods_id).first()
        if goods:
            return render(request, "buyer/detail.html", locals())
    return HttpResponse("没有您想要的商品")


def setOrderId(user_id, goods_id, store_id):
    strtime = time.strftime("%Y%m%d%H%M%S", time.localtime())
    return strtime+str(user_id)+str(goods_id)+str(store_id)


def place_order(request):
    if request.method == "POST":
        count = int(request.POST.get("count"))
        goods_id = request.POST.get("goods_id")
        user_id = request.COOKIES.get("user_id")
        goods = Goods.objects.get(id=goods_id)
        store_id = goods.store_id.id
        price = goods.goods_price

        order = Order()
        order.order_id = setOrderId(str(user_id), str(goods_id), str(store_id))
        order.goods_count = count
        order.order_user = Buyer.objects.get(id=user_id)
        order.order_price = count*price
        order.order_status = 1
        order.save()

        order_detail = OrderDetail()
        order_detail.order_id = order
        order_detail.goods_id = goods_id
        order_detail.goods_name = goods.goods_name
        order_detail.goods_price = goods.goods_price
        order_detail.goods_number = count
        order_detail.goods_total = count*goods.goods_price
        order_detail.goods_store = store_id
        order_detail.goods_image = goods.goods_image
        order_detail.save()

        detail = [order_detail]

        return render(request, "buyer/place_order.html", locals())
    else:
        order_id = request.GET.get("order_id")
        if order_id:
            order = Order.objects.get(id=order_id)
            detail = order.orderdetail_set.all()
            return render(request, "buyer/place_order.html", locals())
        else:
            return HttpResponse("非法请求")



# def cart(request):
#     user_id = request.COOKIES.get("user_id")
#     goods_list = Cart.objects.filter(user_id=user_id)
#     return render(request, "buyer/cart.html", locals())


def add_cart(request):
    result = {"state": "error", "data": ""}
    if request.method == "POST":
        count = int(request.POST.get("count"))
        goods_id = request.POST.get("goods_id")
        goods = Goods.objects.get(id=int(goods_id))
        user_id = request.COOKIES.get("user_id")

        cart = Cart()
        cart.goods_name = goods.goods_name
        cart.goods_price = goods.goods_price
        cart.goods_total = goods.goods_price*count
        cart.goods_number = count
        cart.goods_picture = goods.goods_image
        cart.goods_id = goods.id
        cart.goods_store = goods.store_id.id
        cart.user_id = user_id
        cart.save()
        result["state"] = "success"
        result["data"] = "商品添加成功"
    else:
        result["data"] = "请求错误"
    return JsonResponse(result)


def cart(request):
    user_id = request.COOKIES.get("user_id")
    goods_list = Cart.objects.filter(user_id=user_id)
    if request.method == "POST":
        post_data = request.POST
        cart_data = []
        for k, v in post_data.items():
            if k.startswith("goods_"):
                cart_data.append(Cart.objects.get(id=int(v)))
        goods_count = len(cart_data)
        goods_total = sum([int(i.goods_total) for i in cart_data])

        '''
        from django.db.models import Sum
        修改使用聚类查询返回指定商品的总价
        1.查询到所有的商品
        cart_data = []
        for k, v in post_data.items():
            if k.startswith("goods_"):
                    cart_data.append(int(v))
        2.使用in方法进行范围的划定，然后使用sum方法进行计算
        cart_goods = Cart.objects.filter(id__in=cart_data).aggregate(Sum("goods_total"))
        print(cart_goods)
        
        '''
        order = Order()
        order.order_id = setOrderId(user_id, goods_count, "1")

        order.goods_count = goods_count
        order.order_user = Buyer.objects.get(id=user_id)
        order.order_price = goods_total
        order.order_status = 1
        order.save()

        for detail in cart_data:
            order_detail = OrderDetail()
            order_detail.order_id = order
            order_detail.goods_id = detail.goods_id
            order_detail.goods_name = detail.goods_name
            order_detail.goods_price = detail.goods_price
            order_detail.goods_number = detail.goods_number
            order_detail.goods_total = detail.goods_total
            order_detail.goods_store = detail.goods_store
            order_detail.goods_image = detail.goods_picture
            order_detail.save()

        url = "/Buyer/place_order/?order_id=%s"% order.id
        return HttpResponseRedirect(url)
    return render(request, "buyer/cart.html", locals())





