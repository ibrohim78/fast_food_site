from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order, Reservation
import threading
from .telegram_bot import send_order_notification, send_reservation_notification
from django.db import transaction

@receiver(post_save, sender=Order)
def order_created_handler(sender, instance, created, **kwargs):
    """Yangi buyurtma yaratilganda"""
    if created:
        # OrderItemlar bazaga yozilishi uchun biroz kutib, keyin yuborish
        def send():
            threading.Thread(target=send_order_notification, args=(instance,)).start()
        transaction.on_commit(send)

@receiver(post_save, sender=Reservation)
def reservation_created_handler(sender, instance, created, **kwargs):
    """Yangi bron yaratilganda"""
    if created:  # Faqat yangi yaratilgan bronlar uchun
        # Ma'lumotlar saqlangach, Telegramga yuborish
        def send():
            threading.Thread(target=send_reservation_notification, args=(instance,)).start()
        transaction.on_commit(send)