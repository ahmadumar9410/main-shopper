from django.db import models

colors = (
    ('Red', 'Red'),
    ('Green', 'Green'),
    ('Blue', 'Blue'),
    ('Purple', 'Purple'),
    ('White', 'White'),
)
size = (
    ('Small', 'Small'),
    ('Medium', 'Medium'),
    ('Large', 'Large'),
)


# Create your models here.


class Item(models.Model):
    title = models.CharField(max_length=150)
    price = models.FloatField()
    description = models.TextField()
    color = models.CharField(choices=colors, max_length=6)
    size = models.CharField(choices=size, max_length=6)
    image = models.ImageField(upload_to='shop/images')
    slug = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.title}   of  {self.size} size'


class OrderItem(models.Model):
    user = models.CharField(max_length=50)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    size = models.CharField(choices=size, max_length=6)
    quantity = models.IntegerField()
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.quantity} {self.item}'

    def total_item_price(self):
        return self.quantity * self.item.price


class Payment(models.Model):
    user = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    address = models.CharField(max_length=2350)
    state = models.CharField(max_length=50)
    postal_zip = models.CharField(max_length=50)
    email = models.EmailField(max_length=254)
    phone = models.IntegerField()

    def __str__(self):
        return self.user


class Favourite(models.Model):
    user = models.CharField(max_length=50)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    def __str__(self):
        return self.item.title + ' by ' + self.user


class PromoCode(models.Model):
    code = models.CharField(max_length=50)
    minimum_amount = models.IntegerField()
    discount = models.IntegerField()

    def __str__(self):
        return self.code


class Order(models.Model):
    user = models.CharField(max_length=50)
    items = models.ManyToManyField(OrderItem)
    ordered = models.BooleanField(default=False)
    order_placement = models.DateTimeField(
        auto_now=False, auto_now_add=False, blank=True, null=True)
    payment = models.ForeignKey(Payment, null=True, blank=True, on_delete=models.CASCADE)
    delievered = models.BooleanField(default=False)
    coupon = models.ForeignKey(PromoCode, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.user

    def sub_total(self):
        total = 0
        for orderitem in self.items.all():
            total += orderitem.total_item_price()
        return total

    def discount_price(self):
        try:
            return str(self.sub_total() - self.coupon.discount)
        except:
            return str(self.sub_total())

