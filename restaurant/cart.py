# restaurant/cart.py

from decimal import Decimal
from django.conf import settings
from .models import Product

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)  # ♻️ BU YER
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
    
    def add(self, product, quantity=1, override_quantity=False):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.price)
            }
        
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        
        self.save()
    
    def save(self):
        self.session.modified = True
    
    def remove(self, product_id):
        product_id = str(product_id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()
    
    def update(self, product_id, quantity):
        product_id = str(product_id)
        if product_id in self.cart and quantity > 0:
            self.cart[product_id]['quantity'] = quantity
            self.save()
    
    def clear(self):
        if settings.CART_SESSION_ID in self.session:  # ♻️ BU YERNI QO'SHING
            del self.session[settings.CART_SESSION_ID]
        self.save()
    
    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        
        for product in products:
            cart[str(product.id)]['product'] = product
        
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item
    
    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())
    
    def get_total_price(self):
        return sum(
            Decimal(item['price']) * item['quantity']
            for item in self.cart.values()
        )
        
        # restaurant/cart.py faylida:

from decimal import Decimal
# from django.conf import settings  # ♻️ VAQTINCHA IZOHGA OLING
from .models import Product

CART_SESSION_ID = 'cart'  # ♻️ BU YERNI QO'SHING - to'g'ridan-to'g'ri

class Cart:
    def __init__(self, request):
        self.session = request.session
        # cart = self.session.get(settings.CART_SESSION_ID)  # ♻️ IZOHGA OLING
        cart = self.session.get(CART_SESSION_ID)  # ♻️ BU YERNI QO'SHING
        if not cart:
            # cart = self.session[settings.CART_SESSION_ID] = {}  # ♻️ IZOHGA OLING
            cart = self.session[CART_SESSION_ID] = {}  # ♻️ BU YERNI QO'SHING
        self.cart = cart
    
    # ... qolgan metodlar
    
    def clear(self):
        # if settings.CART_SESSION_ID in self.session:  # ♻️ IZOHGA OLING
        if CART_SESSION_ID in self.session:  # ♻️ BU YERNI QO'SHING
            # del self.session[settings.CART_SESSION_ID]  # ♻️ IZOHGA OLING
            del self.session[CART_SESSION_ID]  # ♻️ BU YERNI QO'SHING
        self.save()