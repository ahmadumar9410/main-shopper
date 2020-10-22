from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, render
from ordermanagement.models import Favourite, Item, Order, OrderItem, Payment, PromoCode
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.models import User, auth


# Create your views here.


def index(request):
    return render(request, 'index.html')


def cart(request):
    try:
        order = Order.objects.get(user=request.user, ordered=False)
        if request.method == 'POST':
            coupon = request.POST['coupon']
            # print(coupon)
            coupon_qs = PromoCode.objects.filter(code=coupon)
            if len(coupon_qs) > 0:
                coupon_db = coupon_qs[0]
                if order.sub_total() > coupon_db.minimum_amount:
                    print('**********************************')
                    print('         Coupon redeemed')
                    print('**********************************')
                    messages.info(request, 'Coupon Successfully Redeemed!!')
                    order.coupon = coupon_db
                    order.save()
                    context = {'order': order}
                else:
                    print('**********************************')
                    print('        Do More Shopping')
                    print('**********************************')
                    context = {'order': order, 'redeemed': False}
                    messages.info(request, 'Do More Shopping at least of ₹' +
                                  str(coupon_db.minimum_amount)+' to redeem this coupon.')
                return render(request, 'cart.html', context)
            else:
                print('Coupon Failed')
                messages.info(request, 'Coupon does not exist')

                context = {'order': order, 'redeemed': False}
                return render(request, 'cart.html', context)
        else:
            context = {'order': order, 'redeemed': True}
            return render(request, 'cart.html', context)
    except ObjectDoesNotExist:
        messages.warning(request, 'You does not have an active order.')
        return redirect('/')


def register(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if password1 == password2:
            if User.objects.filter(username=username).exists():
                print("Username Taken")
                messages.info(request, 'Username taken')
            elif User.objects.filter(email=email).exists():
                print("Email already taken")
                messages.info(request, 'Email taken')

            else:
                user = User.objects.create_user(username=username, email=email, password=password1,
                                                first_name=first_name,
                                                last_name=last_name)
                user.save()
                print(first_name, last_name)
                return redirect('/login/')
        else:
            messages.info(request, 'Password Not Same')

    return render(request, 'register.html')


def login(request):
    if request.method == 'POST':
        username = request.POST['username1']
        password = request.POST['password1']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            print("User is not none")
            return redirect("/")
        else:
            messages.info(request, 'Invalid credentials')
            print("User is None")
            print(username, password, user)
            return redirect("/login")

    else:
        return render(request, 'login.html')


def logout(request):
    auth.logout(request)
    return redirect("/")


def checkout(request):
    order = Order.objects.filter(user=request.user, ordered=False)
    if len(order) > 0:
        if request.method == 'POST':
            fname = request.POST['fname']
            lname = request.POST['lname']
            address = request.POST['address'] + ', ' + request.POST['address2']
            state = request.POST['state']
            postal_zip = request.POST['postal_zip']
            email = request.POST['email']
            phone = request.POST['phone']
            payment = Payment.objects.create(user=request.user, first_name=fname, last_name=lname,
                                             address=address, state=state, postal_zip=postal_zip, email=email, phone=phone)
            order[0].ordered = True
            order[0].items.update(ordered=True)
            order[0].order_placement = timezone.now()
            order[0].payment = payment
            for orderitems in order[0].items.all():
                orderitems.save()
            order[0].save()
            return redirect('/thankyou/')
        return render(request, 'checkout.html', {'order': order[0]})
    else:
        messages.warning(request, 'You does not have an active order.')
        return redirect('/')


def shop(request):
    items = Item.objects.all()
    context = {
        'items': items
    }
    return render(request, 'shop.html', context)


def thankyou(request):
    return render(request, 'thankyou.html')


def remove(request, slug):
    item = Item.objects.filter(slug=slug)[0]
    order_item = OrderItem.objects.filter(
        user=request.user, ordered=False, item=item)[0]
    order = Order.objects.filter(user=request.user, ordered=False)
    order[0].items.remove(order_item)
    order_item.delete()
    messages.warning(request, 'Item successfully removed!!')
    return redirect('/cart')


def product(request, slug):
    item = Item.objects.filter(slug=slug)
    items = Item.objects.all()
    if request.method == 'POST':
        quantity = request.POST['quantity']
        order_qs = Order.objects.filter(user=request.user, ordered=False)
        print(order_qs)
        if len(order_qs) > 0:
            item = item[0]
            order_item = OrderItem.objects.filter(
                user=request.user, ordered=False, item=item)
            if len(order_item):
                order_item[0].quantity = quantity
                order_item[0].save()
                messages.warning(request, 'Quantity updated in cart!')
                order = order_qs[0]
                order.items.add(order_item[0])
            else:
                size = request.POST['size']
                order_item = OrderItem.objects.create(
                    user=request.user, item=item, ordered=False, quantity=quantity, size=size)
                order = order_qs[0]
                order.items.add(order_item)
                messages.info(request, 'Item added in your cart.')

            return redirect('/product/'+item.slug)

        else:
            item = item[0]
            order = Order(user=request.user, ordered=False)
            size = request.POST['size']
            order.save()
            order_item = OrderItem(
                item=item, quantity=quantity, user=request.user,  size=size)
            order_item.save()
            order.items.add(order_item)
            print(quantity)
            messages.info(request, 'Item added in your cart.')
            return redirect('/product/'+item.slug)
    is_favourite = Favourite.objects.filter(user=request.user, item=item[0])

    if len(item) > 0:
        order_item = OrderItem.objects.filter(
            user=request.user, item=item[0], ordered=False)
        if len(order_item) > 0:
            item = item[0]
            if len(is_favourite) > 0:
                context = {'is_favourite': True, 'item': item,
                           'items': items, 'order_item': True, 'order': order_item[0]}
            else:
                context = {'item': item,
                           'items': items, 'order_item': True, 'order': order_item[0]}
        else:
            item = item[0]
            if len(is_favourite) > 0:
                context = {'is_favourite': True, 'item': item,
                           'items': items, 'order_item': False}
            else:
                context = {'item': item,
                           'items': items, 'order_item': False}

        return render(request, 'shop-single.html', context)
    else:
        return redirect('/')


def search(request):

    query = request.GET['query']
    if query != '':

        items = Item.objects.filter(title__icontains=query)
        if len(items) > 0:
            context = {
                'items': items,
                'length': len(items)
            }
        else:
            context = {
                'items': items,
                'length': 0,
                'true': True
            }

        return render(request, 'search.html', context)
    else:
        messages.info(request, 'Please type something in search box.')
        return redirect('/')


def favourite(request, slug):
    item = Item.objects.filter(slug=slug)
    favourite_list = Favourite.objects.filter(user=request.user, item=item[0])
    if len(favourite_list) == 0:
        favourite = Favourite.objects.create(user=request.user, item=item[0])
    else:
        favourite = Favourite.objects.filter(
            user=request.user, item=item[0])[0]
        favourite.delete()
    return redirect(f'/product/{slug}/')
