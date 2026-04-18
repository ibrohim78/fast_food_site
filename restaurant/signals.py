from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order, Reservation

@receiver(post_save, sender=Order)
def order_created_handler(sender, instance, created, **kwargs):
    """Yangi buyurtma yaratilganda"""
    pass

@receiver(post_save, sender=Reservation)
def reservation_created_handler(sender, instance, created, **kwargs):
    """Yangi bron yaratilganda"""
    pass