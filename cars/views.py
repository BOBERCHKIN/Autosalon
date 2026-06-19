from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q, Avg

from .models import Car, CarCategory, Order, Review, UserProfile
from .forms import RegisterForm, CarFilterForm, OrderForm, ReviewForm, CarForm


def is_admin(user):
    return user.is_staff or user.is_superuser


# ──────────────────────────────────────────────
# Головна сторінка
# ──────────────────────────────────────────────
def index(request):
    # Сортування: нові авто першими, потім за ціною
    featured_cars = Car.objects.filter(is_available=True).order_by('-created_at')[:6]
    categories = CarCategory.objects.all().order_by('name')
    return render(request, 'cars/index.html', {
        'featured_cars': featured_cars,
        'categories': categories,
    })


# ──────────────────────────────────────────────
# Каталог авто з фільтрацією та сортуванням
# ──────────────────────────────────────────────
def car_list(request):
    form = CarFilterForm(request.GET)
    cars = Car.objects.filter(is_available=True)

    if form.is_valid():
        data = form.cleaned_data

        # Текстовий пошук
        if data.get('search'):
            q = data['search']
            cars = cars.filter(
                Q(brand__icontains=q) | Q(model__icontains=q) | Q(description__icontains=q)
            )

        # Фільтр за категорією
        if data.get('category'):
            cars = cars.filter(category__slug=data['category'])

        # Фільтр за ціною
        if data.get('min_price'):
            cars = cars.filter(price__gte=data['min_price'])
        if data.get('max_price'):
            cars = cars.filter(price__lte=data['max_price'])

        # Фільтр за паливом і КПП
        if data.get('fuel_type'):
            cars = cars.filter(fuel_type=data['fuel_type'])
        if data.get('transmission'):
            cars = cars.filter(transmission=data['transmission'])

        # Фільтр за роком
        if data.get('min_year'):
            cars = cars.filter(year__gte=data['min_year'])
        if data.get('max_year'):
            cars = cars.filter(year__lte=data['max_year'])

        # Сортування
        sort = data.get('sort') or '-created_at'
        cars = cars.order_by(sort)
    else:
        cars = cars.order_by('-created_at')

    categories = CarCategory.objects.all().order_by('name')
    return render(request, 'cars/car_list.html', {
        'cars': cars,
        'form': form,
        'categories': categories,
        'total': cars.count(),
    })


# ──────────────────────────────────────────────
# Деталі авто
# ──────────────────────────────────────────────
def car_detail(request, pk):
    car = get_object_or_404(Car, pk=pk)
    reviews = car.reviews.all().order_by('-created_at')  # нові відгуки першими
    avg_rating = reviews.aggregate(avg=Avg('rating'))['avg']
    review_form = ReviewForm()
    user_review = None

    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()

    if request.method == 'POST' and request.user.is_authenticated:
        if 'review_submit' in request.POST and not user_review:
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                r = review_form.save(commit=False)
                r.car = car
                r.user = request.user
                r.save()
                messages.success(request, 'Відгук додано!')
                return redirect('car_detail', pk=pk)

    return render(request, 'cars/car_detail.html', {
        'car': car,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'review_form': review_form,
        'user_review': user_review,
    })


# ──────────────────────────────────────────────
# Замовлення
# ──────────────────────────────────────────────
@login_required
def order_create(request, car_pk):
    car = get_object_or_404(Car, pk=car_pk, is_available=True)

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.car = car
            order.final_price = car.price
            order.save()

            # Відправити email підтвердження
            send_mail(
                subject=f'Замовлення #{order.pk} отримано — Автосалон',
                message=(
                    f'Вітаємо, {order.full_name}!\n\n'
                    f'Ваше замовлення на автомобіль {car.get_full_name()} '
                    f'на суму {car.price:,.0f} грн отримано.\n'
                    f'Ми зв\'яжемось з вами найближчим часом.\n\n'
                    f'Номер замовлення: #{order.pk}'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@autosalon.ua',
                recipient_list=[request.user.email],
                fail_silently=True,
            )

            messages.success(request, f'Замовлення #{order.pk} успішно оформлено! Підтвердження надіслано на email.')
            return redirect('order_detail', pk=order.pk)
    else:
        initial = {}
        if request.user.first_name:
            initial['full_name'] = f'{request.user.first_name} {request.user.last_name}'.strip()
        try:
            initial['phone'] = request.user.profile.phone
        except Exception:
            pass
        form = OrderForm(initial=initial)

    return render(request, 'cars/order_form.html', {'car': car, 'form': form})


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, 'cars/order_detail.html', {'order': order})


@login_required
def my_orders(request):
    # Сортування: нові замовлення першими
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'cars/my_orders.html', {'orders': orders})


# ──────────────────────────────────────────────
# Реєстрація та авторизація
# ──────────────────────────────────────────────
def register(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Реєстрація успішна! Ласкаво просимо!')
            return redirect('index')
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'З поверненням, {user.first_name or user.username}!')
            return redirect(request.GET.get('next', 'index'))
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Ви вийшли з системи.')
    return redirect('index')


# ──────────────────────────────────────────────
# Адмін-панель (кастомна)
# ──────────────────────────────────────────────
@user_passes_test(is_admin)
def admin_dashboard(request):
    # Сортування замовлень: нові першими, потім за статусом
    orders = Order.objects.all().order_by('-created_at').select_related('user', 'car')
    pending = orders.filter(status='pending').order_by('-created_at')
    confirmed = orders.filter(status='confirmed').order_by('-confirmed_at')
    cars = Car.objects.all().order_by('-created_at').select_related('category')

    return render(request, 'cars/admin_dashboard.html', {
        'orders': orders,
        'pending': pending,
        'confirmed': confirmed,
        'cars': cars,
        'total_orders': orders.count(),
        'pending_count': pending.count(),
        'total_cars': cars.count(),
        'available_cars': cars.filter(is_available=True).count(),
    })


@user_passes_test(is_admin)
def admin_order_action(request, pk, action):
    order = get_object_or_404(Order, pk=pk)

    if action == 'confirm':
        order.confirm()
        # Позначити авто як недоступний
        order.car.is_available = False
        order.car.save()
        # Надіслати email
        send_mail(
            subject=f'Замовлення #{order.pk} підтверджено — Автосалон',
            message=(
                f'Вітаємо, {order.full_name}!\n\n'
                f'Ваше замовлення на {order.car.get_full_name()} підтверджено.\n'
                f'Ціна: {order.final_price:,.0f} грн\n\n'
                f'Дякуємо за вибір нашого автосалону!'
            ),
            from_email='noreply@autosalon.ua',
            recipient_list=[order.user.email],
            fail_silently=True,
        )
        messages.success(request, f'Замовлення #{pk} підтверджено. Авто прибрано з каталогу.')
    elif action == 'cancel':
        order.cancel()
        # Повернути авто в каталог
        order.car.is_available = True
        order.car.save()
        messages.warning(request, f'Замовлення #{pk} скасовано. Авто повернено в каталог.')

    return redirect('admin_dashboard')


@user_passes_test(is_admin)
def car_create(request):
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES)
        if form.is_valid():
            car = form.save()
            messages.success(request, f'Автомобіль «{car}» додано.')
            return redirect('car_detail', pk=car.pk)
    else:
        form = CarForm()

    return render(request, 'cars/car_form.html', {'form': form, 'title': 'Додати автомобіль'})


@user_passes_test(is_admin)
def car_edit(request, pk):
    car = get_object_or_404(Car, pk=pk)

    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES, instance=car)
        if form.is_valid():
            form.save()
            messages.success(request, f'Автомобіль «{car}» оновлено.')
            return redirect('car_detail', pk=car.pk)
    else:
        form = CarForm(instance=car)

    return render(request, 'cars/car_form.html', {'form': form, 'car': car, 'title': 'Редагувати автомобіль'})


@user_passes_test(is_admin)
def car_delete(request, pk):
    car = get_object_or_404(Car, pk=pk)

    if request.method == 'POST':
        name = str(car)
        car.delete()
        messages.success(request, f'Автомобіль «{name}» видалено.')
        return redirect('car_list')

    return render(request, 'cars/car_confirm_delete.html', {'car': car})


# ──────────────────────────────────────────────
# Категорії (публічна сторінка)
# ──────────────────────────────────────────────
def category_cars(request, slug):
    category = get_object_or_404(CarCategory, slug=slug)
    # Сортування всередині категорії: за ціною за замовчуванням
    sort = request.GET.get('sort', 'price')
    cars = Car.objects.filter(category=category, is_available=True).order_by(sort)
    return render(request, 'cars/category_cars.html', {
        'category': category,
        'cars': cars,
        'sort': sort,
    })