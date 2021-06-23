from django import template

register = template.Library()


@register.filter(name='is_in_cart')
def is_in_cart(product, cart):
    keys = cart.keys()
    for id in keys:
        if id == str(product.id):
            return True
    return False


@register.filter(name='cart_quantity')
def cart_quantity(product, cart):
    keys = cart.keys()
    for id in keys:
        if id == str(product.id):
            # for getting the value of cart items
            return cart.get(id)
    return 0


@register.filter(name='cart_count')
def cart_count(cart):
    keys = cart.keys()
    count = 0
    for id in keys:
        count = count+1
    return count


@register.filter(name='price_total')
def price_total(product, cart):
    price = product.price * cart_quantity(product, cart)
    return price


@register.filter(name='price_total_order')
def price_total_order(price, q):
    price = price * q
    return price


@register.filter(name='cart_total_price')
def cart_total_price(product, cart):
    sum = 0
    for p in product:
        sum += price_total(p, cart)
    return sum
