from django.db import models


class Buyer(models.Model):
    username = models.CharField(max_length=32, verbose_name="用户名")
    password = models.CharField(max_length=32, verbose_name="密码")
    email = models.EmailField(verbose_name="用户邮箱")
    phone = models.CharField(max_length=32, verbose_name="联系电话", blank=True, null=True)
    connect_address = models.TextField(verbose_name="联系地址", blank=True, null=True)


class Address(models.Model):
    """
    收货地址
    """
    address = models.TextField(verbose_name="收货地址")
    receiver = models.CharField(max_length=32, verbose_name="接收人")
    recv_phone = models.CharField(max_length=32, verbose_name="收件人电话")
    post_number = models.CharField(max_length=32, verbose_name="邮编")
    buyer_id = models.ForeignKey(to=Buyer, on_delete=models.CASCADE, verbose_name="用户id")


class Order(models.Model):
    order_id = models.CharField(max_length=32, verbose_name="id订单编号")
    goods_count = models.IntegerField(verbose_name="商品数量")
    order_user = models.ForeignKey(to=Buyer, on_delete=models.CASCADE, verbose_name="订单用户")
    order_address = models.ForeignKey(to=Address, on_delete=models.CASCADE, verbose_name="订单地址", blank=True, null=True)
    order_price = models.FloatField(verbose_name="订单总价")

    # 订单状态 未支付1 代发货2 已发货3 已收货4 （已退货0）拒绝发货5
    order_status = models.IntegerField(default=1, verbose_name="订单状态")


class OrderDetail(models.Model):
    order_id = models.ForeignKey(to=Order, on_delete=models.CASCADE, verbose_name="订单编号")
    goods_id = models.IntegerField(verbose_name="商品ID")
    goods_name = models.CharField(max_length=32, verbose_name="商品名称")
    goods_price = models.FloatField(verbose_name="商品价格")
    goods_number = models.IntegerField(verbose_name="商品购买数量")
    goods_total = models.FloatField(verbose_name="商品总价")
    goods_store = models.IntegerField(verbose_name="商店ID")
    goods_image = models.ImageField(verbose_name="商品图片")


class Cart(models.Model):
    goods_name = models.CharField(max_length=32, verbose_name="商品名称")
    goods_price = models.FloatField(verbose_name="商品价格")
    goods_total = models.FloatField(verbose_name="商品总价")
    goods_number = models.IntegerField(verbose_name="商品数量")
    goods_picture = models.ImageField(upload_to="buyer/images", verbose_name="商品图片")
    goods_id = models.IntegerField(verbose_name="商品ID")
    goods_store = models.IntegerField(verbose_name="尚品商店")
    user_id = models.IntegerField(verbose_name="用户ID")




































