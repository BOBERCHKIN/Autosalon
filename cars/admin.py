from django.contrib import admin
from .models import Car, CarCategory, Order, Review, UserProfile


@admin.register(CarCategory)
class CarCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ['brand', 'model', 'year', 'price', 'fuel_type', 'transmission', 'is_available', 'created_at']
    list_filter = ['category', 'fuel_type', 'transmission', 'drive_type', 'is_available']
    search_fields = ['brand', 'model', 'color']
    list_editable = ['is_available', 'price']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'car', 'status', 'final_price', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'car__brand', 'car__model', 'full_name', 'phone']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'confirmed_at']
    actions = ['confirm_orders', 'cancel_orders']

    def confirm_orders(self, request, queryset):
        for order in queryset.filter(status='pending'):
            order.confirm()
        self.message_user(request, 'Замовлення підтверджено.')
    confirm_orders.short_description = 'Підтвердити вибрані замовлення'

    def cancel_orders(self, request, queryset):
        for order in queryset:
            order.cancel()
        self.message_user(request, 'Замовлення скасовано.')
    cancel_orders.short_description = 'Скасувати вибрані замовлення'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'car', 'rating', 'created_at']
    list_filter = ['rating']
    ordering = ['-created_at']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'city', 'email_confirmed', 'created_at']
    ordering = ['-created_at']