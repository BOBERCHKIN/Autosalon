from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# ──────────────────────────────────────────────
# Модель 1: Категорія автомобіля
# ──────────────────────────────────────────────
class CarCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name='Назва категорії')
    slug = models.SlugField(unique=True, verbose_name='Slug')
    description = models.TextField(blank=True, verbose_name='Опис')
    icon = models.CharField(max_length=50, blank=True, verbose_name='Іконка (CSS клас)')

    class Meta:
        verbose_name = 'Категорія'
        verbose_name_plural = 'Категорії'
        ordering = ['name']  # сортування за назвою A–Z

    def __str__(self):
        return self.name


# ──────────────────────────────────────────────
# Модель 2: Автомобіль
# ──────────────────────────────────────────────
class Car(models.Model):
    TRANSMISSION_CHOICES = [
        ('manual', 'Механіка'),
        ('automatic', 'Автомат'),
        ('robot', 'Робот'),
        ('variator', 'Варіатор'),
    ]
    FUEL_CHOICES = [
        ('petrol', 'Бензин'),
        ('diesel', 'Дизель'),
        ('electric', 'Електро'),
        ('hybrid', 'Гібрид'),
        ('gas', 'Газ'),
    ]
    DRIVE_CHOICES = [
        ('fwd', 'Передній'),
        ('rwd', 'Задній'),
        ('awd', 'Повний'),
    ]

    category = models.ForeignKey(
        CarCategory, on_delete=models.SET_NULL, null=True,
        related_name='cars', verbose_name='Категорія'
    )
    brand = models.CharField(max_length=100, verbose_name='Марка')
    model = models.CharField(max_length=100, verbose_name='Модель')
    year = models.PositiveIntegerField(verbose_name='Рік випуску')
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Ціна (грн)')
    mileage = models.PositiveIntegerField(default=0, verbose_name='Пробіг (км)')
    engine_volume = models.DecimalField(
        max_digits=3, decimal_places=1, verbose_name='Об\'єм двигуна (л)'
    )
    engine_power = models.PositiveIntegerField(verbose_name='Потужність (к.с.)')
    transmission = models.CharField(
        max_length=20, choices=TRANSMISSION_CHOICES, verbose_name='КПП'
    )
    fuel_type = models.CharField(
        max_length=20, choices=FUEL_CHOICES, verbose_name='Паливо'
    )
    drive_type = models.CharField(
        max_length=10, choices=DRIVE_CHOICES, verbose_name='Привід'
    )
    color = models.CharField(max_length=50, verbose_name='Колір')
    description = models.TextField(blank=True, verbose_name='Опис')
    image = models.ImageField(
        upload_to='cars/', blank=True, null=True, verbose_name='Фото'
    )
    is_available = models.BooleanField(default=True, verbose_name='Доступний')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Додано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Оновлено')

    class Meta:
        verbose_name = 'Автомобіль'
        verbose_name_plural = 'Автомобілі'
        ordering = ['-created_at', 'brand', 'model']  # нові — першими, потім A–Z

    def __str__(self):
        return f'{self.brand} {self.model} ({self.year})'

    def get_full_name(self):
        return f'{self.brand} {self.model} {self.year}'


# ──────────────────────────────────────────────
# Модель 3: Замовлення (купівля)
# ──────────────────────────────────────────────
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Очікує підтвердження'),
        ('confirmed', 'Підтверджено'),
        ('cancelled', 'Скасовано'),
        ('completed', 'Завершено'),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='orders', verbose_name='Користувач'
    )
    car = models.ForeignKey(
        Car, on_delete=models.CASCADE, related_name='orders', verbose_name='Автомобіль'
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус'
    )
    full_name = models.CharField(max_length=200, verbose_name='Повне ім\'я')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    comment = models.TextField(blank=True, verbose_name='Коментар')
    final_price = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name='Фінальна ціна (грн)'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата замовлення')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Оновлено')
    confirmed_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата підтвердження')

    class Meta:
        verbose_name = 'Замовлення'
        verbose_name_plural = 'Замовлення'
        ordering = ['-created_at']  # найновіші замовлення — першими

    def __str__(self):
        return f'Замовлення #{self.pk} — {self.car} ({self.get_status_display()})'

    def confirm(self):
        self.status = 'confirmed'
        self.confirmed_at = timezone.now()
        self.save()

    def cancel(self):
        self.status = 'cancelled'
        self.save()


# ──────────────────────────────────────────────
# Модель 4: Профіль користувача
# ──────────────────────────────────────────────
class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile', verbose_name='Користувач'
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    avatar = models.ImageField(
        upload_to='avatars/', blank=True, null=True, verbose_name='Аватар'
    )
    city = models.CharField(max_length=100, blank=True, verbose_name='Місто')
    bio = models.TextField(blank=True, verbose_name='Про себе')
    email_confirmed = models.BooleanField(default=False, verbose_name='Email підтверджено')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата реєстрації')

    class Meta:
        verbose_name = 'Профіль'
        verbose_name_plural = 'Профілі'
        ordering = ['-created_at']  # нові профілі — першими

    def __str__(self):
        return f'Профіль: {self.user.username}'


# ──────────────────────────────────────────────
# Модель 5: Відгук про автомобіль
# ──────────────────────────────────────────────
class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    car = models.ForeignKey(
        Car, on_delete=models.CASCADE, related_name='reviews', verbose_name='Автомобіль'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews', verbose_name='Користувач'
    )
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, verbose_name='Оцінка')
    text = models.TextField(verbose_name='Текст відгуку')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата')

    class Meta:
        verbose_name = 'Відгук'
        verbose_name_plural = 'Відгуки'
        ordering = ['-created_at']          # нові відгуки — першими
        unique_together = ['car', 'user']   # один відгук від одного юзера

    def __str__(self):
        return f'{self.user.username} → {self.car} ({self.rating}★)'