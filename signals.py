# restaurant/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order, Reservation
import threading
from .telegram_bot import send_order_to_telegram, send_reservation_to_telegram

@receiver(post_save, sender=Order)
def order_created_handler(sender, instance, created, **kwargs):
    """Yangi buyurtma yaratilganda"""
    if created:  # Faqat yangi yaratilgan buyurtmalar uchun
        # Thread yordamida telegramga yuborish (asynchronous)
        thread = threading.Thread(
            target=send_order_to_telegram,
            args=(instance.id,)
        )
        thread.start()

@receiver(post_save, sender=Reservation)
def reservation_created_handler(sender, instance, created, **kwargs):
    """Yangi bron yaratilganda"""
    if created:  # Faqat yangi yaratilgan bronlar uchun
        # Thread yordamida telegramga yuborish (asynchronous)
        thread = threading.Thread(
            target=send_reservation_to_telegram,
            args=(instance.id,)
        )
        thread.start()