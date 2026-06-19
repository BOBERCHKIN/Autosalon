from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Car, Order, Review, UserProfile, CarCategory


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Електронна пошта')
    first_name = forms.CharField(max_length=100, required=True, label='Ім\'я')
    last_name = forms.CharField(max_length=100, required=True, label='Прізвище')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            UserProfile.objects.create(user=user)
        return user


class CarFilterForm(forms.Form):
    SORT_CHOICES = [
        ('-created_at', 'Новіші першими'),
        ('price', 'Ціна: від дешевих'),
        ('-price', 'Ціна: від дорогих'),
        ('year', 'Рік: від старих'),
        ('-year', 'Рік: від нових'),
        ('mileage', 'Пробіг: від меншого'),
        ('brand', 'Марка (А–Я)'),
    ]

    search = forms.CharField(required=False, label='Пошук')
    category = forms.ChoiceField(required=False, label='Категорія')
    min_price = forms.DecimalField(required=False, min_value=0, label='Ціна від')
    max_price = forms.DecimalField(required=False, min_value=0, label='Ціна до')
    fuel_type = forms.ChoiceField(required=False, label='Паливо')
    transmission = forms.ChoiceField(required=False, label='КПП')
    min_year = forms.IntegerField(required=False, label='Рік від')
    max_year = forms.IntegerField(required=False, label='Рік до')
    sort = forms.ChoiceField(choices=SORT_CHOICES, required=False, label='Сортування')

    def __init__(self, *args, **kwargs):
        from .models import CarCategory, Car
        super().__init__(*args, **kwargs)
        categories = [('', 'Всі категорії')] + [
            (c.slug, c.name) for c in CarCategory.objects.all().order_by('name')
        ]
        self.fields['category'].choices = categories

        fuel_choices = [('', 'Всі')] + list(Car.FUEL_CHOICES)
        self.fields['fuel_type'].choices = fuel_choices

        trans_choices = [('', 'Всі')] + list(Car.TRANSMISSION_CHOICES)
        self.fields['transmission'].choices = trans_choices


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['full_name', 'phone', 'comment']
        labels = {
            'full_name': 'Ваше повне ім\'я',
            'phone': 'Контактний телефон',
            'comment': 'Коментар до замовлення',
        }
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3}),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'text']
        labels = {
            'rating': 'Оцінка',
            'text': 'Відгук',
        }
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4}),
        }


class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        exclude = ['created_at', 'updated_at']
        labels = {
            'category': 'Категорія',
            'brand': 'Марка',
            'model': 'Модель',
            'year': 'Рік',
            'price': 'Ціна (грн)',
            'mileage': 'Пробіг (км)',
            'engine_volume': 'Об\'єм двигуна (л)',
            'engine_power': 'Потужність (к.с.)',
            'transmission': 'КПП',
            'fuel_type': 'Паливо',
            'drive_type': 'Привід',
            'color': 'Колір',
            'description': 'Опис',
            'image': 'Фото',
            'is_available': 'Доступний',
        }