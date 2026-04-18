import logging
import asyncio
from telegram import Bot
from telegram.error import TelegramError
import django
import os
import sys

# Django settings
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'website.settings')
django.setup()

from restaurant.models import Order, Reservation

# Telegram bot token
TELEGRAM_TOKEN = '8215513833:AAG8cVBULt0zCiyLUZuhXHYBK3x1TLcwsN8'  # BotFather dan oling
ADMIN_CHAT_ID = '7750527012'  # Admin telegram ID

# Botni ishga tushirish
bot = Bot(token=TELEGRAM_TOKEN)

def send_order_to_telegram(order_id):
    """Buyurtmani telegramga yuborish"""
    try:
        order = Order.objects.get(id=order_id)
        
        message = f"""
📦 *YANGI BUYURTMA* #{order.id}

👤 *Mijoz:* {order.customer_name}
📞 *Telefon:* {order.phone}
📍 *Manzil:* {order.address if order.address else 'Restoranda'}
🪑 *Stol:* {order.table.number if order.table else 'Yo\'q'}

💰 *Jami narx:* {order.total_price} so'm
📊 *Holat:* {order.get_status_display()}

⏰ *Vaqt:* {order.created_at.strftime('%Y-%m-%d %H:%M')}
⏳ *Taxminiy vaqt:* {order.estimated_time} daqiqa
💳 *To\'langan:* {'✅ Ha' if order.is_paid else '❌ Yo\'q'}

📋 *Taomlar:*
"""
        
        # Taomlar ro'yxati
        items = order.orderitem_set.all()
        for item in items:
            message += f"  • {item.product.name} x{item.quantity} - {item.price * item.quantity} so'm\n"
        
        message += f"\n🆔 *Buyurtma ID:* {order.id}"
        
        # Telegramga yuborish
        asyncio.run(send_telegram_message(message))
        return True
        
    except Order.DoesNotExist:
        logging.error(f"Order {order_id} not found")
        return False
    except Exception as e:
        logging.error(f"Error sending order to telegram: {e}")
        return False

def send_reservation_to_telegram(reservation_id):
    """Bronni telegramga yuborish"""
    try:
        reservation = Reservation.objects.get(id=reservation_id)
        
        message = f"""
📅 *YANGI BRON* #{reservation.id}

👤 *Mijoz:* {reservation.customer_name}
📞 *Telefon:* {reservation.phone}
📧 *Email:* {reservation.email if reservation.email else 'Yo\'q'}

🪑 *Stol:* {reservation.table.number} ({reservation.table.get_capacity_display()})
👥 *Mehmonlar:* {reservation.guests} kishi
📅 *Sana:* {reservation.date}
⏰ *Vaqt:* {reservation.time}

📝 *Maxsus iltimoslar:*
{reservation.special_requests if reservation.special_requests else 'Yo\'q'}

⏰ *Bron vaqti:* {reservation.created_at.strftime('%Y-%m-%d %H:%M')}
✅ *Tasdiqlandi:* {'✅ Ha' if reservation.is_confirmed else '❌ Yo\'q'}

🆔 *Bron ID:* {reservation.id}
"""
        
        # Telegramga yuborish
        asyncio.run(send_telegram_message(message))
        return True
        
    except Reservation.DoesNotExist:
        logging.error(f"Reservation {reservation_id} not found")
        return False
    except Exception as e:
        logging.error(f"Error sending reservation to telegram: {e}")
        return False

async def send_telegram_message(message_text):
    """Telegramga xabar yuborish"""
    try:
        await bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=message_text,
            parse_mode='Markdown'
        )
        logging.info("Xabar telegramga muvaffaqiyatli yuborildi")
        return True
    except TelegramError as e:
        logging.error(f"Telegram xatosi: {e}")
        return False

# Test uchun
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Telegram bot ishga tushdi...")
    
    # Test xabar
    test_message = "✅ Fast Food bot ishga tushdi! Admin: @6959926310"
    asyncio.run(send_telegram_message(test_message))