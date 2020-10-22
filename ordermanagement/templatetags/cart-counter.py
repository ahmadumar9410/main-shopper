from django import template
from ordermanagement.models import Favourite, Item, Order

register = template.Library()

@register.filter
def cart_counter(user):
    if user.is_authenticated:
        try:
            order = Order.objects.filter(user=user, ordered=False)[0]
            return order.items.count()
        except:
            return 0
    else:
        return 0

@register.filter
def favourite(user):
    if user.is_authenticated:
        try:
            items = Favourite.objects.filter(user=user)
            answer = '<table>'
            for item in items:
                answer += f'<tr><td style="color:red"><a href="/product/{item.item.slug}"> {item.item.title}</a></td></tr> '
            answer += '</table>'
            return answer
        except:
            return 0
    else:
        return ''