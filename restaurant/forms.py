from django import forms
from .models import Reservation, Order
import datetime

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['customer_name', 'phone', 'email', 'table', 'date', 'time', 'guests', 'special_requests']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'min': datetime.date.today().strftime('%Y-%m-%d')
            }),
            'special_requests': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'customer_name': 'Ismingiz',
            'phone': 'Telefon raqamingiz',
            'email': 'Email',
            'table': 'Stol',
            'date': 'Sana',
            'time': 'Vaqt',
            'guests': 'Mehmonlar soni',
            'special_requests': 'Maxsus iltimoslar',
        }
    
    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date < datetime.date.today():
            raise forms.ValidationError("Sana o'tgan bo'lishi mumkin emas!")
        return date

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer_name', 'phone', 'address', 'table']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'customer_name': 'Ismingiz',
            'phone': 'Telefon raqamingiz',
            'address': 'Manzil (yetkazib berish uchun)',
            'table': 'Stol raqami (agar restoranda ovqatlansangiz)',
        }