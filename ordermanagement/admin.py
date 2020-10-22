from django.contrib import admin
from .models import Item, OrderItem, Order, Payment, Favourite, PromoCode
# Register your models here.
admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Favourite)
admin.site.register(PromoCode)
admin.site.register(Payment)
class OrderAdmin(admin.ModelAdmin):
    list_display  = ['user', 'ordered', 'delievered']  

admin.site.register(Order, OrderAdmin)