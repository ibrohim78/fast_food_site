from .cart import Cart

def cart_count(request):
    cart = Cart(request)
    return {
        'cart_count': cart.__len__(),
        'cart_total': cart.get_total_price(),
    }