from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg, Sum, Max, Min

from .models import Category, Product, Review, Cart, Order, OrderItem
from .forms import CategoryForm, ProductForm, ReviewForm, ProductReviewForm, RegisterForm


def product_list(request):
    products = Product.objects.select_related("user", "category").annotate(
        avg_rating=Avg("reviews__rating"),
        reviews_count=Count("reviews", distinct=True),
    )

    q = request.GET.get("q", "")
    category = request.GET.get("category", "")
    user_id = request.GET.get("user", "")
    price_min = request.GET.get("price_min", "")
    price_max = request.GET.get("price_max", "")
    in_stock = request.GET.get("in_stock", "")
    sort = request.GET.get("sort", "")

    if q:
        products = products.filter(Q(name__icontains=q) | Q(description__icontains=q))

    if category.isdigit():
        products = products.filter(category__id=category)
    if user_id.isdigit():
        products = products.filter(user__id=user_id)
    if price_min.replace(".", "", 1).isdigit():
        products = products.filter(price__gte=price_min)
    if price_max.replace(".", "", 1).isdigit():
        products = products.filter(price__lte=price_max)
    if in_stock:
        products = products.filter(quantity__gt=0)

    sort_fields = {
        "price": "price",
        "-price": "-price",
        "quantity": "quantity",
        "-quantity": "-quantity",
        "rating": "avg_rating",
        "-rating": "-avg_rating",
        "id": "id",
    }
    if sort in sort_fields:
        products = products.order_by(sort_fields[sort])

    filtered_stats = None
    if q or category or user_id or price_min or price_max or in_stock:
        filtered_stats = products.aggregate(count=Count("id", distinct=True), avg_price=Avg("price"))

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get("page"))
    params = request.GET.copy()
    params.pop("page", None)

    context = {
        "page_obj": page_obj,
        "categories": Category.objects.all(),
        "users": User.objects.all(),
        "q": q,
        "category": category,
        "user_id": user_id,
        "price_min": price_min,
        "price_max": price_max,
        "in_stock": in_stock,
        "sort": sort,
        "filtered_stats": filtered_stats,
        "params": params.urlencode(),
        "title": "Каталог",
    }
    return render(request, "main/product_list.html", context)


@login_required
def my_products(request):
    products = Product.objects.filter(user=request.user).select_related("category").annotate(
        reviews_count=Count("reviews"),
    )
    return render(request, "main/my_products.html", {"products": products})


def product_detail(request, pk):
    product = get_object_or_404(
        Product.objects.select_related("user", "category").prefetch_related("reviews__user"), pk=pk
    )
    avg_rating = product.reviews.aggregate(avg=Avg("rating"))["avg"]

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("login")
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, "Отзыв добавлен!")
            return redirect("product_detail", pk=product.pk)
    else:
        form = ProductReviewForm()

    return render(request, "main/product_detail.html", {"product": product, "avg_rating": avg_rating, "form": form})


@login_required
def product_create(request):
    form = ProductForm(request.POST or None)
    if form.is_valid():
        product = form.save(commit=False)
        product.user = request.user
        product.save()
        messages.success(request, f"Продукт №{product.id} добавлен!")
        return redirect("product_detail", pk=product.pk)
    return render(request, "main/form.html", {"form": form, "title": "Добавить продукт"})


@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if product.user != request.user and not request.user.is_staff:
        messages.error(request, "Можно изменять только свои продукты")
        return redirect("product_detail", pk=pk)
    form = ProductForm(request.POST or None, instance=product)
    if form.is_valid():
        form.save()
        messages.success(request, "Продукт изменён!")
        return redirect("product_detail", pk=product.pk)
    return render(request, "main/form.html", {"form": form, "title": f"Изменить продукт №{product.id}"})


@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if product.user != request.user and not request.user.is_staff:
        messages.error(request, "Можно удалять только свои продукты")
        return redirect("product_detail", pk=pk)
    if request.method == "POST":
        product.delete()
        messages.success(request, "Продукт удалён!")
        return redirect("my_products")
    return render(request, "main/confirm_delete.html", {"object": product})


def category_list(request):
    categories = Category.objects.annotate(products_count=Count("products"))
    empty_categories = categories.filter(products_count=0)
    return render(request, "main/category_list.html", {
        "categories": categories,
        "empty_categories": empty_categories,
    })


def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    products = category.products.select_related("user")
    return render(request, "main/category_detail.html", {"category": category, "products": products})


@login_required
def category_create(request):
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        category = form.save()
        messages.success(request, f"Категория №{category.id} добавлена!")
        return redirect("category_detail", pk=category.pk)
    return render(request, "main/form.html", {"form": form, "title": "Добавить категорию"})


@staff_member_required
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=category)
    if form.is_valid():
        form.save()
        messages.success(request, "Категория изменена!")
        return redirect("category_detail", pk=category.pk)
    return render(request, "main/form.html", {"form": form, "title": "Изменить категорию"})


@staff_member_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        category.delete()
        messages.success(request, "Категория удалена!")
        return redirect("category_list")
    return render(request, "main/confirm_delete.html", {"object": category})


def review_list(request):
    reviews = Review.objects.select_related("product", "user")
    return render(request, "main/review_list.html", {"reviews": reviews})


def review_detail(request, pk):
    review = get_object_or_404(Review.objects.select_related("product", "user"), pk=pk)
    return render(request, "main/review_detail.html", {"review": review})


@login_required
def review_create(request):
    form = ReviewForm(request.POST or None)
    if form.is_valid():
        review = form.save(commit=False)
        review.user = request.user
        review.save()
        messages.success(request, "Отзыв добавлен!")
        return redirect("review_detail", pk=review.pk)
    return render(request, "main/form.html", {"form": form, "title": "Добавить отзыв"})


@login_required
def review_update(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if review.user != request.user and not request.user.is_staff:
        messages.error(request, "Можно изменять только свои отзывы")
        return redirect("review_detail", pk=pk)
    form = ReviewForm(request.POST or None, instance=review)
    if form.is_valid():
        form.save()
        messages.success(request, "Отзыв изменён!")
        return redirect("review_detail", pk=review.pk)
    return render(request, "main/form.html", {"form": form, "title": "Изменить отзыв"})


@login_required
def review_delete(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if review.user != request.user and not request.user.is_staff:
        messages.error(request, "Можно удалять только свои отзывы")
        return redirect("review_detail", pk=pk)
    if request.method == "POST":
        review.delete()
        messages.success(request, "Отзыв удалён!")
        return redirect("review_list")
    return render(request, "main/confirm_delete.html", {"object": review})


def user_list(request):
    users = User.objects.annotate(
        products_count=Count("products"),
        avg_price=Avg("products__price"),
    )
    q = request.GET.get("q", "")
    if q:
        users = users.filter(username__icontains=q)
    return render(request, "main/user_list.html", {"users": users, "q": q})


def user_detail(request, pk):
    seller = get_object_or_404(User.objects.prefetch_related("products__category"), pk=pk)
    return render(request, "main/user_detail.html", {"seller": seller})


def statistics(request):
    stats = Product.objects.aggregate(
        total_products=Count("id"),
        avg_price=Avg("price"),
        max_price=Max("price"),
        min_price=Min("price"),
        total_price=Sum("price"),
        total_quantity=Sum("quantity"),
    )
    avg_rating = Review.objects.aggregate(avg=Avg("rating"))["avg"]
    in_stock = Product.objects.filter(quantity__gt=0).aggregate(count=Count("id"))["count"]

    top_users = User.objects.annotate(products_count=Count("products")).filter(
        products_count__gt=0
    ).order_by("-products_count")[:5]
    top_products = Product.objects.annotate(avg_rating=Avg("reviews__rating")).filter(
        avg_rating__isnull=False
    ).order_by("-avg_rating")[:5]
    good_products = Product.objects.annotate(avg_rating=Avg("reviews__rating")).filter(avg_rating__gt=4)
    last_reviews = Review.objects.select_related("product", "user")[:5]

    return render(request, "main/statistics.html", {
        "stats": stats,
        "avg_rating": avg_rating,
        "in_stock": in_stock,
        "top_users": top_users,
        "top_products": top_products,
        "good_products": good_products,
        "last_reviews": last_reviews,
    })


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            login(request, user)
            messages.success(request, f"Вы успешно зарегистрировались! Ваш ID: {user.id}")
            return redirect("product_list")
    else:
        form = RegisterForm()
    return render(request, "registration/register.html", {"form": form})


@login_required
def cart(request):
    items = Cart.objects.filter(user=request.user).select_related("product")
    total = 0
    for item in items:
        item.sum = item.product.price * item.quantity
        total += item.sum
    return render(request, "main/cart.html", {"items": items, "total": total})


@login_required
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    item = Cart.objects.filter(user=request.user, product=product).first()
    in_cart = item.quantity if item else 0

    if in_cart >= product.quantity:
        messages.error(request, "Больше этого продукта нет в наличии")
        return redirect("product_detail", pk=pk)

    if item:
        item.quantity += 1
        item.save()
    else:
        Cart.objects.create(user=request.user, product=product)
    messages.success(request, "Продукт добавлен в корзину!")
    return redirect("cart")


@login_required
def remove_from_cart(request, pk):
    item = get_object_or_404(Cart, pk=pk, user=request.user)
    item.delete()
    messages.success(request, "Продукт убран из корзины")
    return redirect("cart")


@login_required
def checkout(request):
    items = Cart.objects.filter(user=request.user).select_related("product")
    if not items:
        messages.error(request, "Корзина пустая")
        return redirect("cart")

    for item in items:
        if item.quantity > item.product.quantity:
            messages.error(request, f"«{item.product.name}» осталось только {item.product.quantity} шт.")
            return redirect("cart")

    order = Order.objects.create(user=request.user)
    total = 0
    for item in items:
        OrderItem.objects.create(order=order, product=item.product, price=item.product.price, quantity=item.quantity)
        total += item.product.price * item.quantity
        item.product.quantity -= item.quantity
        item.product.save()
    order.total = total
    order.save()
    items.delete()

    messages.success(request, f"Заказ №{order.id} оформлен! Теперь оплатите его.")
    return redirect("my_orders")


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).prefetch_related("items__product")
    return render(request, "main/my_orders.html", {"orders": orders})


@login_required
def pay_order(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    order.is_paid = True
    order.save()
    messages.success(request, "Заказ оплачен! Спасибо за покупку.")
    return redirect("my_orders")


@staff_member_required
def sales(request):
    items = OrderItem.objects.select_related("order", "order__user", "product").order_by("-order__created_at")
    total_money = Order.objects.filter(is_paid=True).aggregate(total=Sum("total"))["total"] or 0
    return render(request, "main/sales.html", {"items": items, "total_money": total_money})
