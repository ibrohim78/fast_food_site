# restaurant/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
import json
from datetime import datetime
from .models import Product, Category, Table, Order, OrderItem, Reservation
from .telegram_bot import send_order_notification, send_reservation_notification

# ==================== ASOSIY SAHIFALAR ====================

def home(request):
    """Bosh sahifa"""
    categories = Category.objects.all()[:6]
    featured_products = Product.objects.filter(is_available=True)[:8]
    
    context = {
        'categories': categories,
        'featured_products': featured_products,
    }
    return render(request, 'restaurant/home.html', context)

def menu(request):
    """Menyu sahifasi"""
    products = Product.objects.filter(is_available=True)
    categories = Category.objects.all()
    
    # Kategoriya bo'yicha filtrlash
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    
    context = {
        'products': products,
        'categories': categories,
        'selected_category': category_id,
    }
    return render(request, 'restaurant/menu.html', context)

def about(request):
    """Biz haqimizda sahifasi"""
    return render(request, 'restaurant/about.html')

def contact(request):
    """Aloqa sahifasi"""
    if request.method == 'POST':
        # Kontakt formasi
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        
        if name and message:
            # Bu yerda email yuborish yoki ma'lumotlarni saqlash kodi bo'ladi
            # Hozircha faqat muvaffaqiyat xabarini ko'rsatamiz
            
            # Telegramga xabar yuborish (admin uchun)
            telegram_message = f"""
📩 YANGI KONTAKT XABARI

👤 Ism: {name}
📧 Email: {email if email else 'Yo\'q'}
📞 Telefon: {phone if phone else 'Yo\'q'}
📌 Mavzu: {subject if subject else 'Boshqa'}
📝 Xabar:
{message}
"""
            send_reservation_notification({'customer_name': name, 'phone': phone or 'Yo\'q'})
            
            messages.success(request, 'Xabaringiz muvaffaqiyatli yuborildi! Tez orada siz bilan bog\'lanamiz.')
            return redirect('restaurant:contact')
        else:
            messages.error(request, 'Iltimos, ism va xabaringizni kiriting!')
    
    return render(request, 'restaurant/contact.html')

# ==================== BUYURTMA FUNKSIYALARI ====================

def order(request):
    """Buyurtma sahifasi"""
    if request.method == 'POST':
        try:
            # Ma'lumotlarni olish
            name = request.POST.get('name', '').strip()
            phone = request.POST.get('phone', '').strip()
            address = request.POST.get('address', '').strip()
            delivery_type = request.POST.get('delivery_type', 'delivery')
            table_id = request.POST.get('table')
            notes = request.POST.get('notes', '').strip()
            
            # Cart ma'lumotlari
            cart_data = json.loads(request.POST.get('cart_data', '[]'))
            
            # Validatsiya
            if not name:
                messages.error(request, 'Iltimos, ismingizni kiriting!')
                return redirect('restaurant:order')
            
            if not phone or len(phone) < 9:
                messages.error(request, 'Iltimos, to\'g\'ri telefon raqamini kiriting!')
                return redirect('restaurant:order')
            
            if not cart_data:
                messages.error(request, 'Savat bo\'sh! Iltimos, taom tanlang.')
                return redirect('restaurant:order')
            
            # Table obyekti
            table = None
            if table_id and delivery_type == 'dine_in':
                try:
                    table = Table.objects.get(id=table_id)
                except Table.DoesNotExist:
                    table = None
            
            # Buyurtmani yaratish
            order = Order.objects.create(
                customer_name=name,
                phone=phone,
                address=address if delivery_type == 'delivery' else '',
                table=table,
                total_price=0,
                status='pending'
            )
            
            # OrderItem'larni yaratish va jami narxni hisoblash
            total_price = 0
            for item in cart_data:
                try:
                    product = Product.objects.get(id=item['id'])
                    quantity = int(item['quantity'])
                    item_total = product.price * quantity
                    
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price=product.price
                    )
                    
                    total_price += item_total
                    
                except (Product.DoesNotExist, ValueError, KeyError):
                    continue
            
            # Jami narxni yangilash
            order.total_price = total_price
            order.save()
            
            # Telegramga xabar yuborish
            send_order_notification(order)
            
            # Muvaffaqiyatli sahifaga yo'naltirish
            messages.success(request, f'✅ Buyurtma muvaffaqiyatli qabul qilindi! Buyurtma raqami: #{order.id}')
            return redirect('restaurant:order_success', order_id=order.id)
            
        except Exception as e:
            messages.error(request, f'Xatolik yuz berdi: {str(e)}')
            return redirect('restaurant:order')
    
    # GET so'rovi uchun
    products = Product.objects.filter(is_available=True)
    tables = Table.objects.filter(is_available=True)
    categories = Category.objects.all()
    
    context = {
        'products': products,
        'tables': tables,
        'categories': categories,
    }
    return render(request, 'restaurant/order.html', context)

def order_success(request, order_id):
    """Buyurtma muvaffaqiyatli sahifasi"""
    try:
        order = Order.objects.get(id=order_id)
        items = OrderItem.objects.filter(order=order)
        
        context = {
            'order': order,
            'items': items,
        }
        return render(request, 'restaurant/order_success.html', context)
        
    except Order.DoesNotExist:
        messages.error(request, 'Buyurtma topilmadi!')
        return redirect('restaurant:home')

# ==================== BRON FUNKSIYALARI ====================

def reservation(request):
    """Stol bron qilish sahifasi"""
    if request.method == 'POST':
        try:
            # Ma'lumotlarni olish
            name = request.POST.get('name', '').strip()
            phone = request.POST.get('phone', '').strip()
            email = request.POST.get('email', '').strip()
            table_id = request.POST.get('table')
            date_str = request.POST.get('date')
            time = request.POST.get('time')
            guests = request.POST.get('guests', '2')
            special_requests = request.POST.get('special_requests', '').strip()
            
            # Validatsiya
            if not name:
                messages.error(request, 'Iltimos, ismingizni kiriting!')
                return redirect('restaurant:reservation')
            
            if not phone or len(phone) < 9:
                messages.error(request, 'Iltimos, to\'g\'ri telefon raqamini kiriting!')
                return redirect('restaurant:reservation')
            
            if not table_id:
                messages.error(request, 'Iltimos, stol tanlang!')
                return redirect('restaurant:reservation')
            
            if not date_str:
                messages.error(request, 'Iltimos, sana tanlang!')
                return redirect('restaurant:reservation')
            
            if not time:
                messages.error(request, 'Iltimos, vaqt tanlang!')
                return redirect('restaurant:reservation')
            
            # Sana formatlash
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Table obyekti
            table = Table.objects.get(id=table_id)
            
            # Mehmonlar soni
            try:
                guests_int = int(guests)
                if guests_int > table.capacity:
                    messages.error(request, f'Stol sig\'imi {table.capacity} kishilik!')
                    return redirect('restaurant:reservation')
            except ValueError:
                guests_int = 2
            
            # Bronni yaratish
            reservation = Reservation.objects.create(
                customer_name=name,
                phone=phone,
                email=email,
                table=table,
                date=date,
                time=time,
                guests=guests_int,
                special_requests=special_requests
            )
            
            # Telegramga xabar yuborish
            send_reservation_notification(reservation)
            
            # Muvaffaqiyatli sahifaga yo'naltirish
            messages.success(request, f'✅ Bron muvaffaqiyatli qabul qilindi! Bron raqami: #{reservation.id}')
            return redirect('restaurant:reservation_success')
            
        except Table.DoesNotExist:
            messages.error(request, 'Tanlangan stol topilmadi!')
            return redirect('restaurant:reservation')
        except ValueError:
            messages.error(request, 'Sana noto\'g\'ri formatda!')
            return redirect('restaurant:reservation')
        except Exception as e:
            messages.error(request, f'Xatolik yuz berdi: {str(e)}')
            return redirect('restaurant:reservation')
    
    # GET so'rovi uchun
    tables = Table.objects.filter(is_available=True)
    
    context = {
        'tables': tables,
    }
    return render(request, 'restaurant/reservation.html', context)

def reservation_success(request):
    """Bron muvaffaqiyatli sahifasi"""
    return render(request, 'restaurant/reservation_success.html')

# ==================== SAVAT FUNKSIYALARI ====================

def cart(request):
    """Savat sahifasi"""
    # Session orqali savat ma'lumotlarini olish
    cart_items = request.session.get('cart', [])
    
    # Taomlar ma'lumotlarini olish
    cart_with_details = []
    subtotal = 0
    
    for item in cart_items:
        try:
            product = Product.objects.get(id=item['id'])
            quantity = int(item['quantity'])
            item_total = product.price * quantity
            
            cart_with_details.append({
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'quantity': quantity,
                'total': item_total,
                'image': product.image.url if product.image else '/static/images/default.jpg'
            })
            
            subtotal += item_total
            
        except (Product.DoesNotExist, ValueError, KeyError):
            continue
    
    # Yetkazib berish narxi
    delivery_fee = 0 if subtotal > 50000 else 15000
    total = subtotal + delivery_fee
    
    context = {
        'cart_items': cart_with_details,
        'subtotal': subtotal,
        'delivery_fee': delivery_fee,
        'total': total,
        'free_delivery_threshold': 50000,
        'cart_count': len(cart_with_details),
    }
    
    return render(request, 'restaurant/cart.html', context)

def add_to_cart(request):
    """Savatga mahsulot qo'shish"""
    if request.method == 'POST':
        try:
            product_id = int(request.POST.get('product_id'))
            quantity = int(request.POST.get('quantity', 1))
            
            # Mahsulot mavjudligini tekshirish
            product = Product.objects.get(id=product_id, is_available=True)
            
            # Session da savat
            cart = request.session.get('cart', [])
            
            # Mahsulot savatda bormi?
            found = False
            for item in cart:
                if item['id'] == product_id:
                    item['quantity'] += quantity
                    found = True
                    break
            
            # Agar yo'q bo'lsa, qo'shish
            if not found:
                cart.append({
                    'id': product_id,
                    'quantity': quantity,
                    'name': product.name,
                    'price': float(product.price)
                })
            
            # Session ni yangilash
            request.session['cart'] = cart
            request.session.modified = True
            
            # Agar AJAX so'rovi bo'lsa
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                cart_count = sum(item['quantity'] for item in cart)
                return JsonResponse({
                    'success': True,
                    'message': f'{product.name} savatga qo\'shildi',
                    'cart_count': cart_count
                })
            
            messages.success(request, f'{product.name} savatga qo\'shildi')
            return redirect(request.META.get('HTTP_REFERER', 'restaurant:menu'))
            
        except (Product.DoesNotExist, ValueError):
            messages.error(request, 'Mahsulot topilmadi yoki miqdor noto\'g\'ri!')
            return redirect('restaurant:menu')
    
    return redirect('restaurant:menu')

def update_cart(request):
    """Savatdagi mahsulot miqdorini o'zgartirish"""
    if request.method == 'POST':
        try:
            product_id = int(request.POST.get('product_id'))
            quantity = int(request.POST.get('quantity', 1))
            
            if quantity < 1:
                return remove_from_cart(request, product_id)
            
            # Session da savat
            cart = request.session.get('cart', [])
            
            # Mahsulotni topish va miqdorni yangilash
            for item in cart:
                if item['id'] == product_id:
                    item['quantity'] = quantity
                    break
            
            # Session ni yangilash
            request.session['cart'] = cart
            request.session.modified = True
            
            # Jami narxlarni hisoblash
            subtotal = 0
            for item in cart:
                try:
                    product = Product.objects.get(id=item['id'])
                    subtotal += product.price * item['quantity']
                except Product.DoesNotExist:
                    continue
            
            delivery_fee = 0 if subtotal > 50000 else 15000
            total = subtotal + delivery_fee
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                cart_count = sum(item['quantity'] for item in cart)
                return JsonResponse({
                    'success': True,
                    'cart_count': cart_count,
                    'subtotal': subtotal,
                    'delivery_fee': delivery_fee,
                    'total': total
                })
            
            messages.success(request, 'Savat yangilandi')
            return redirect('restaurant:cart')
            
        except ValueError:
            messages.error(request, 'Noto\'g\'ri ma\'lumot!')
            return redirect('restaurant:cart')
    
    return redirect('restaurant:cart')

def remove_from_cart(request, product_id=None):
    """Savatdan mahsulot olib tashlash"""
    try:
        if not product_id and request.method == 'POST':
            product_id = int(request.POST.get('product_id'))
        
        # Session da savat
        cart = request.session.get('cart', [])
        
        # Mahsulotni olib tashlash
        new_cart = [item for item in cart if item['id'] != product_id]
        
        # Session ni yangilash
        request.session['cart'] = new_cart
        request.session.modified = True
        
        # Mahsulot nomini olish
        try:
            product = Product.objects.get(id=product_id)
            product_name = product.name
        except Product.DoesNotExist:
            product_name = 'Mahsulot'
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            cart_count = sum(item['quantity'] for item in new_cart)
            return JsonResponse({
                'success': True,
                'message': f'{product_name} savatdan olib tashlandi',
                'cart_count': cart_count
            })
        
        messages.success(request, f'{product_name} savatdan olib tashlandi')
        return redirect('restaurant:cart')
        
    except (ValueError, TypeError):
        messages.error(request, 'Noto\'g\'ri ma\'lumot!')
        return redirect('restaurant:cart')

def clear_cart(request):
    """Savatni tozalash"""
    request.session['cart'] = []
    request.session.modified = True
    
    messages.success(request, 'Savat tozalandi')
    return redirect('restaurant:cart')

# ==================== API FUNKSIYALARI ====================

def get_cart_count(request):
    """Savatdagi mahsulotlar sonini qaytarish (AJAX uchun)"""
    cart = request.session.get('cart', [])
    cart_count = sum(item['quantity'] for item in cart)
    
    return JsonResponse({
        'count': cart_count,
        'success': True
    })

def get_cart_items(request):
    """Savatdagi mahsulotlar ro'yxatini qaytarish (AJAX uchun)"""
    cart = request.session.get('cart', [])
    cart_items = []
    subtotal = 0
    
    for item in cart:
        try:
            product = Product.objects.get(id=item['id'])
            quantity = int(item['quantity'])
            item_total = product.price * quantity
            
            cart_items.append({
                'id': product.id,
                'name': product.name,
                'price': float(product.price),
                'quantity': quantity,
                'total': float(item_total),
                'image': product.image.url if product.image else ''
            })
            
            subtotal += item_total
            
        except (Product.DoesNotExist, ValueError):
            continue
    
    delivery_fee = 0 if subtotal > 50000 else 15000
    total = subtotal + delivery_fee
    
    return JsonResponse({
        'items': cart_items,
        'subtotal': float(subtotal),
        'delivery_fee': float(delivery_fee),
        'total': float(total),
        'success': True
    })

def get_table_info(request, table_id):
    """Stol ma'lumotlarini olish (AJAX uchun)"""
    try:
        table = Table.objects.get(id=table_id)
        
        return JsonResponse({
            'success': True,
            'table': {
                'id': table.id,
                'number': table.number,
                'capacity': table.capacity,
                'description': table.description,
                'is_available': table.is_available
            }
        })
        
    except Table.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Stol topilmadi'
        })

def check_table_availability(request):
    """Stol mavjudligini tekshirish (AJAX uchun)"""
    try:
        table_id = int(request.GET.get('table_id'))
        date = request.GET.get('date')
        time = request.GET.get('time')
        
        # Bu yerda stol bandligini tekshirish logikasi bo'ladi
        # Hozircha oddiy tekshirish
        table = Table.objects.get(id=table_id)
        
        # Agar stol mavjud bo'lsa
        if table.is_available:
            return JsonResponse({
                'success': True,
                'available': True,
                'message': 'Stol band qilinishi mumkin'
            })
        else:
            return JsonResponse({
                'success': True,
                'available': False,
                'message': 'Stol band qilingan'
            })
            
    except (Table.DoesNotExist, ValueError):
        return JsonResponse({
            'success': False,
            'message': 'Stol topilmadi'
        })

# ==================== TELEGRAM BOT FUNKSIYASI ====================

def test_telegram(request):
    """Telegram botni test qilish (faqat admin uchun)"""
    # Bu funksiya faqat test uchun
    from .telegram_bot import send_order_notification, send_reservation_notification
    
    # Test buyurtma
    test_order = {
        'id': 999,
        'customer_name': 'Test Mijoz',
        'phone': '901234567',
        'address': 'Test manzil',
        'total_price': 75000,
        'get_status_display': lambda: 'Kutilyapti',
        'created_at': datetime.now(),
        'estimated_time': 25
    }
    
    # Test bron
    test_reservation = {
        'id': 999,
        'customer_name': 'Test Mijoz',
        'phone': '901234567',
        'email': 'test@example.com',
        'table': type('obj', (object,), {'number': 5}),
        'date': '2024-01-01',
        'time': '18:00',
        'guests': 4,
        'special_requests': 'Test iltimos',
        'created_at': datetime.now()
    }
    
    try:
        # Test xabarlarni yuborish
        send_order_notification(test_order)
        send_reservation_notification(test_reservation)
        
        messages.success(request, 'Test xabarlar telegramga yuborildi!')
    except Exception as e:
        messages.error(request, f'Xatolik: {str(e)}')
    
    return redirect('restaurant:home')

# restaurant/views.py - oxiriga quyidagilarni qo'shing

def get_cart_count(request):
    """Savatdagi mahsulotlar sonini qaytarish (AJAX uchun)"""
    cart = request.session.get('cart', [])
    cart_count = sum(item.get('quantity', 0) for item in cart)
    
    return JsonResponse({
        'count': cart_count,
        'success': True
    })

def get_cart_items(request):
    """Savatdagi mahsulotlar ro'yxatini qaytarish (AJAX uchun)"""
    cart = request.session.get('cart', [])
    cart_items = []
    subtotal = 0
    
    for item in cart:
        try:
            product = Product.objects.get(id=item['id'])
            quantity = int(item.get('quantity', 1))
            item_total = product.price * quantity
            
            cart_items.append({
                'id': product.id,
                'name': product.name,
                'price': float(product.price),
                'quantity': quantity,
                'total': float(item_total),
                'image': product.image.url if product.image else ''
            })
            
            subtotal += item_total
            
        except (Product.DoesNotExist, ValueError, KeyError):
            continue
    
    delivery_fee = 0 if subtotal > 50000 else 15000
    total = subtotal + delivery_fee
    
    return JsonResponse({
        'items': cart_items,
        'subtotal': float(subtotal),
        'delivery_fee': float(delivery_fee),
        'total': float(total),
        'success': True
    })