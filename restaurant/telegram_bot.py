# restaurant/telegram_bot.py

import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def send_telegram_message(message):
    """Telegramga xabar yuborish"""
    try:
        # Bot tokenini settings dan olish
        bot_token = getattr(settings, '8319724115:AAHAM-Ekbwq1Sh-bolR6kLYBOlfuHIUBEiU', '')
        admin_id = getattr(settings, 'TELEGRAM_ADMIN_ID', '6959926310')
        
        if not bot_token:
            logger.warning("TELEGRAM_BOT_TOKEN sozlanmagan")
            return False
        
        url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
        
        data = {
            'chat_id': admin_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, data=data, timeout=10)
        
        if response.status_code == 200:
            logger.info("Xabar telegramga muvaffaqiyatli yuborildi")
            return True
        else:
            logger.error(f"Telegram API xatosi: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Xabar yuborishda xato: {str(e)}")
        return False

def send_order_notification(order):
    """Buyurtma haqida xabar yuborish"""
    try:
        message = f"""
<b>🛒 YANGI BUYURTMA #{order.id if hasattr(order, 'id') else 'TEST'}</b>

👤 <b>Mijoz:</b> {order.customer_name}
📞 <b>Telefon:</b> {order.phone}
📍 <b>Manzil:</b> {getattr(order, 'address', 'Restoranda') or 'Restoranda'}
🪑 <b>Stol:</b> {f'Stol {order.table.number}' if hasattr(order, 'table') and order.table else 'Yo\'q'}

💰 <b>Jami narx:</b> {getattr(order, 'total_price', 0):,} so'm
📊 <b>Holat:</b> {order.get_status_display() if hasattr(order, 'get_status_display') else 'Kutilyapti'}

⏰ <b>Vaqt:</b> {order.created_at.strftime('%d.%m.%Y %H:%M') if hasattr(order, 'created_at') else 'Hozir'}
⏳ <b>Taxminiy vaqt:</b> {getattr(order, 'estimated_time', 30)} daqiqa

🆔 <b>Buyurtma ID:</b> {order.id if hasattr(order, 'id') else 'TEST'}
"""
        
        return send_telegram_message(message)
        
    except Exception as e:
        logger.error(f"Buyurtma xabarini yuborishda xato: {str(e)}")
        return False

def send_reservation_notification(reservation):
    """Bron haqida xabar yuborish"""
    try:
        message = f"""
<b>📅 YANGI BRON #{reservation.id if hasattr(reservation, 'id') else 'TEST'}</b>

👤 <b>Mijoz:</b> {reservation.customer_name}
📞 <b>Telefon:</b> {reservation.phone}
📧 <b>Email:</b> {getattr(reservation, 'email', 'Yo\'q') or 'Yo\'q'}

🪑 <b>Stol:</b> Stol {reservation.table.number if hasattr(reservation, 'table') else 'N'}
📅 <b>Sana:</b> {getattr(reservation, 'date', 'Hozir')}
⏰ <b>Vaqt:</b> {getattr(reservation, 'time', 'Hozir')}
👥 <b>Mehmonlar:</b> {getattr(reservation, 'guests', 2)} kishi

📝 <b>Maxsus iltimoslar:</b>
{getattr(reservation, 'special_requests', 'Yo\'q') or 'Yo\'q'}

⏰ <b>Bron vaqti:</b> {reservation.created_at.strftime('%d.%m.%Y %H:%M') if hasattr(reservation, 'created_at') else 'Hozir'}

🆔 <b>Bron ID:</b> {reservation.id if hasattr(reservation, 'id') else 'TEST'}
"""
        
        return send_telegram_message(message)
        
    except Exception as e:
        logger.error(f"Bron xabarini yuborishda xato: {str(e)}")
        return False