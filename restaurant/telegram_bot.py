# restaurant/telegram_bot.py

import requests
import logging
from django.conf import settings
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)

def send_telegram_message(message_text):
    """Telegramga xabar yuborish"""
    try:
        # Bot tokenini settings dan olish
        bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
        admin_id = getattr(settings, 'TELEGRAM_ADMIN_ID', '')
        
        # Agar token sozlanmagan bo'lsa, terminalga chiqaramiz
        if not bot_token or bot_token == 'YOUR_BOT_TOKEN_HERE':
            print("⚠️  Telegram bot tokeni sozlanmagan!")
            print(f"📝 Xabar matni: {message_text[:200]}...")
            return True
        
        # Telegram API URL
        url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
        
        # Xabar ma'lumotlari
        data = {
            'chat_id': admin_id,
            'text': message_text,
            'parse_mode': 'HTML'
        }
        
        # Xabarni yuborish
        response = requests.post(url, data=data, timeout=10)
        
        if response.status_code == 200:
            print("✅ Xabar telegramga muvaffaqiyatli yuborildi!")
            return True
        else:
            error_msg = f"❌ Telegram xatosi: {response.status_code}"
            print(error_msg)
            logger.error(error_msg)
            return False
            
    except Exception as e:
        error_msg = f"❌ Xabar yuborishda xato: {str(e)}"
        print(error_msg)
        logger.error(error_msg)
        return True  # Telegram xatosiz davom etish uchun

def send_order_notification(order):
    """Buyurtma haqida xabar yuborish"""
    try:
        message = f"""
<b>🛒 YANGI BUYURTMA #{order.id}</b>
<pre>------------------------</pre>
👤 <b>Mijoz:</b> {strip_tags(order.customer_name)}
📞 <b>Telefon:</b> {order.phone}
📍 <b>Manzil:</b> {order.address or 'Restoranda'}
🪑 <b>Stol:</b> {f'Stol {order.table.number}' if order.table else "Yo'q"}

💰 <b>Jami narx:</b> {order.total_price:,} so'm
📊 <b>Holat:</b> {order.get_status_display()}

⏰ <b>Vaqt:</b> {order.created_at.strftime('%d.%m.%Y %H:%M')}
⏳ <b>Taxminiy vaqt:</b> {getattr(order, 'estimated_time', 30)} daqiqa
💳 <b>To'langan:</b> {'✅ Ha' if order.is_paid else '❌ Yo\'q'}

📋 <b>Taomlar:</b>
"""
        
        # OrderItem lar mavjud bo'lsa
        items = order.orderitem_set.all()
        if items:
            for item in items:
                message += f"• {strip_tags(item.product.name)} x{item.quantity}\n"
        else:
            message += "<i>Mahsulotlar yuklanmadi</i>\n"
        
        message += f"\n🆔 <b>Buyurtma ID:</b> {order.id}"
        
        return send_telegram_message(message)
        
    except Exception as e:
        error_msg = f"❌ Buyurtma xabarini yuborishda xato: {str(e)}"
        print(error_msg)
        logger.error(error_msg)
        return True

def send_reservation_notification(reservation):
    """Bron haqida xabar yuborish"""
    try:
        message = f"""
<b>📅 YANGI BRON #{reservation.id}</b>
<pre>------------------------</pre>
👤 <b>Mijoz:</b> {strip_tags(reservation.customer_name)}
📞 <b>Telefon:</b> {reservation.phone}
📧 <b>Email:</b> {reservation.email or "Yo'q"}

🪑 <b>Stol:</b> Stol {reservation.table.number} ({reservation.table.get_capacity_display()})
📅 <b>Sana:</b> {reservation.date}
⏰ <b>Vaqt:</b> {reservation.time}
👥 <b>Mehmonlar:</b> {reservation.guests} kishi

📝 <b>Maxsus iltimoslar:</b>
{reservation.special_requests or "Yo'q"}

⏰ <b>Bron vaqti:</b> {reservation.created_at.strftime('%d.%m.%Y %H:%M')}
✅ <b>Tasdiqlandi:</b> {'✅ Ha' if reservation.is_confirmed else '❌ Yo\'q'}

🆔 <b>Bron ID:</b> {reservation.id}
"""
        
        return send_telegram_message(message)
        
    except Exception as e:
        error_msg = f"❌ Bron xabarini yuborishda xato: {str(e)}"
        print(error_msg)
        logger.error(error_msg)
        return True