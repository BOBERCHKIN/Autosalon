from django.urls import path
from . import views

urlpatterns = [
    # Головна
    path('', views.index, name='index'),

    # Каталог авто
    path('cars/', views.car_list, name='car_list'),
    path('cars/<int:pk>/', views.car_detail, name='car_detail'),
    path('cars/category/<slug:slug>/', views.category_cars, name='category_cars'),

    # Управління авто (адмін)
    path('cars/new/', views.car_create, name='car_create'),
    path('cars/<int:pk>/edit/', views.car_edit, name='car_edit'),
    path('cars/<int:pk>/delete/', views.car_delete, name='car_delete'),

    # Замовлення
    path('order/<int:car_pk>/', views.order_create, name='order_create'),
    path('order/detail/<int:pk>/', views.order_detail, name='order_detail'),
    path('my-orders/', views.my_orders, name='my_orders'),

    # Авторизація
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Кастомна адмін-панель
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/order/<int:pk>/<str:action>/', views.admin_order_action, name='admin_order_action'),
]