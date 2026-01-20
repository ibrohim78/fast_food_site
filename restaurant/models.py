from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Kategoriya nomi")
    description = models.TextField(verbose_name="Tavsif")
    image = models.ImageField(upload_to='categories/', verbose_name="Rasm")
    
    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"
    
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Mahsulot nomi")
    description = models.TextField(verbose_name="Tavsif")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Narxi")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Kategoriya")
    image = models.ImageField(upload_to='products/', verbose_name="Rasm")
    is_available = models.BooleanField(default=True, verbose_name="Mavjudmi")
    cooking_time = models.IntegerField(verbose_name="Tayyorlanish vaqti (daqiqa)", default=20)
    
    class Meta:
        verbose_name = "Mahsulot"
        verbose_name_plural = "Mahsulotlar"
    
    def __str__(self):
        return self.name

class Table(models.Model):
    TABLE_TYPES = [
        ('2', '2 kishilik'),
        ('4', '4 kishilik'),
        ('6', '6 kishilik'),
        ('8', '8 kishilik'),
    ]
    
    number = models.IntegerField(unique=True, verbose_name="Stol raqami")
    capacity = models.CharField(max_length=1, choices=TABLE_TYPES, verbose_name="Sig'imi")
    description = models.TextField(verbose_name="Tavsif", blank=True)
    is_available = models.BooleanField(default=True, verbose_name="Mavjudmi")
    
    class Meta:
        verbose_name = "Stol"
        verbose_name_plural = "Stollar"
    
    def __str__(self):
        return f"Stol {self.number} ({self.get_capacity_display()})"

class Reservation(models.Model):
    TIME_SLOTS = [
        ('10:00', '10:00'),
        ('12:00', '12:00'),
        ('14:00', '14:00'),
        ('16:00', '16:00'),
        ('18:00', '18:00'),
        ('20:00', '20:00'),
        ('22:00', '22:00'),
    ]
    
    customer_name = models.CharField(max_length=200, verbose_name="Mijoz ismi")
    phone = models.CharField(max_length=20, verbose_name="Telefon raqami")
    email = models.EmailField(verbose_name="Email", blank=True)
    table = models.ForeignKey(Table, on_delete=models.CASCADE, verbose_name="Stol")
    date = models.DateField(verbose_name="Sana")
    time = models.CharField(max_length=5, choices=TIME_SLOTS, verbose_name="Vaqt")
    guests = models.IntegerField(verbose_name="Mehmonlar soni", validators=[MinValueValidator(1), MaxValueValidator(20)])
    special_requests = models.TextField(verbose_name="Maxsus iltimoslar", blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqt")
    is_confirmed = models.BooleanField(default=False, verbose_name="Tasdiqlandimi")
    
    class Meta:
        verbose_name = "Bron"
        verbose_name_plural = "Bronlar"
        ordering = ['-date', '-time']
    
    def __str__(self):
        return f"{self.customer_name} - {self.date} {self.time}"

class Order(models.Model):
    ORDER_STATUS = [
        ('pending', "Kutilyapti"),
        ('preparing', "Tayyorlanmoqda"),
        ('ready', "Tayyor"),
        ('delivered', "Yetkazib berildi"),
        ('cancelled', "Bekor qilindi"),
    ]
    
    customer_name = models.CharField(max_length=200, verbose_name="Mijoz ismi")
    phone = models.CharField(max_length=20, verbose_name="Telefon raqami")
    address = models.TextField(verbose_name="Manzil", blank=True)
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Stol")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Jami narx", default=0)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending', verbose_name="Holati")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqt")
    estimated_time = models.IntegerField(verbose_name="Taxminiy tayyorlanish vaqti (daqiqa)", default=30)
    is_paid = models.BooleanField(default=False, verbose_name="To'langanmi")
    
    class Meta:
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"#{self.id} - {self.customer_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name="Buyurtma")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Mahsulot")
    quantity = models.IntegerField(verbose_name="Miqdori", default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Narxi")
    
    class Meta:
        verbose_name = "Buyurtma elementi"
        verbose_name_plural = "Buyurtma elementlari"
    
    def __str__(self):
        return f"{self.product.name} x{self.quantity}"