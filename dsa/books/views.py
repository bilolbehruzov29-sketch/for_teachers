from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg, Sum, Max, Min

from .models import Author, Category, Book, Review, Cart, Order, OrderItem
from .forms import AuthorForm, CategoryForm, BookForm, ReviewForm, BookReviewForm, RegisterForm


def book_list(request):
    books = Book.objects.select_related("author").prefetch_related("categories").annotate(
        avg_rating=Avg("reviews__rating"),
        reviews_count=Count("reviews", distinct=True),
    )

    q = request.GET.get("q", "")
    category = request.GET.get("category", "")
    author = request.GET.get("author", "")
    price_min = request.GET.get("price_min", "")
    price_max = request.GET.get("price_max", "")
    year = request.GET.get("year", "")
    in_stock = request.GET.get("in_stock", "")
    sort = request.GET.get("sort", "")

    if q:
        books = books.filter(Q(title__icontains=q) | Q(author__full_name__icontains=q))

    if category.isdigit():
        books = books.filter(categories__id=category)
    if author.isdigit():
        books = books.filter(author__id=author)
    if price_min.replace(".", "", 1).isdigit():
        books = books.filter(price__gte=price_min)
    if price_max.replace(".", "", 1).isdigit():
        books = books.filter(price__lte=price_max)
    if year.isdigit():
        books = books.filter(published_year=year)
    if in_stock:
        books = books.filter(in_stock=True)

    sort_fields = {
        "price": "price",
        "-price": "-price",
        "year": "published_year",
        "-year": "-published_year",
        "rating": "avg_rating",
        "-rating": "-avg_rating",
    }
    if sort in sort_fields:
        books = books.order_by(sort_fields[sort])

    filtered_stats = None
    if q or category or author or price_min or price_max or year or in_stock:
        filtered_stats = books.aggregate(count=Count("id", distinct=True), avg_price=Avg("price"))

    paginator = Paginator(books, 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    params = request.GET.copy()
    params.pop("page", None)

    context = {
        "page_obj": page_obj,
        "categories": Category.objects.all(),
        "authors": Author.objects.all(),
        "q": q,
        "category": category,
        "author": author,
        "price_min": price_min,
        "price_max": price_max,
        "year": year,
        "in_stock": in_stock,
        "sort": sort,
        "filtered_stats": filtered_stats,
        "params": params.urlencode(),
    }
    return render(request, "books/book_list.html", context)


def book_detail(request, pk):
    book = get_object_or_404(
        Book.objects.select_related("author").prefetch_related("categories", "reviews"), pk=pk
    )
    avg_rating = book.reviews.aggregate(avg=Avg("rating"))["avg"]

    if request.method == "POST":
        form = BookReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.book = book
            review.save()
            messages.success(request, "Отзыв добавлен!")
            return redirect("book_detail", pk=book.pk)
    else:
        form = BookReviewForm()

    return render(request, "books/book_detail.html", {"book": book, "avg_rating": avg_rating, "form": form})


@staff_member_required
def book_create(request):
    form = BookForm(request.POST or None)
    if form.is_valid():
        book = form.save()
        messages.success(request, "Книга успешно добавлена!")
        return redirect("book_detail", pk=book.pk)
    return render(request, "books/form.html", {"form": form, "title": "Добавить книгу"})


@staff_member_required
def book_update(request, pk):
    book = get_object_or_404(Book, pk=pk)
    form = BookForm(request.POST or None, instance=book)
    if form.is_valid():
        form.save()
        messages.success(request, "Книга изменена!")
        return redirect("book_detail", pk=book.pk)
    return render(request, "books/form.html", {"form": form, "title": "Изменить книгу"})


@staff_member_required
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == "POST":
        book.delete()
        messages.success(request, "Книга удалена!")
        return redirect("book_list")
    return render(request, "books/confirm_delete.html", {"object": book})


def author_list(request):
    authors = Author.objects.annotate(
        books_count=Count("books"),
        avg_price=Avg("books__price"),
    )
    q = request.GET.get("q", "")
    if q:
        authors = authors.filter(Q(full_name__icontains=q) | Q(country__icontains=q))
    return render(request, "books/author_list.html", {"authors": authors, "q": q})


def author_detail(request, pk):
    author = get_object_or_404(Author.objects.prefetch_related("books__categories"), pk=pk)
    return render(request, "books/author_detail.html", {"author": author})


@staff_member_required
def author_create(request):
    form = AuthorForm(request.POST or None)
    if form.is_valid():
        author = form.save()
        messages.success(request, "Автор добавлен!")
        return redirect("author_detail", pk=author.pk)
    return render(request, "books/form.html", {"form": form, "title": "Добавить автора"})


@staff_member_required
def author_update(request, pk):
    author = get_object_or_404(Author, pk=pk)
    form = AuthorForm(request.POST or None, instance=author)
    if form.is_valid():
        form.save()
        messages.success(request, "Автор изменён!")
        return redirect("author_detail", pk=author.pk)
    return render(request, "books/form.html", {"form": form, "title": "Изменить автора"})


@staff_member_required
def author_delete(request, pk):
    author = get_object_or_404(Author, pk=pk)
    if request.method == "POST":
        author.delete()
        messages.success(request, "Автор удалён!")
        return redirect("author_list")
    return render(request, "books/confirm_delete.html", {"object": author})


def category_list(request):
    categories = Category.objects.annotate(books_count=Count("books"))
    empty_categories = categories.filter(books_count=0)
    return render(request, "books/category_list.html", {
        "categories": categories,
        "empty_categories": empty_categories,
    })


def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    books = category.books.select_related("author")
    return render(request, "books/category_detail.html", {"category": category, "books": books})


@staff_member_required
def category_create(request):
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        category = form.save()
        messages.success(request, "Категория добавлена!")
        return redirect("category_detail", pk=category.pk)
    return render(request, "books/form.html", {"form": form, "title": "Добавить категорию"})


@staff_member_required
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=category)
    if form.is_valid():
        form.save()
        messages.success(request, "Категория изменена!")
        return redirect("category_detail", pk=category.pk)
    return render(request, "books/form.html", {"form": form, "title": "Изменить категорию"})


@staff_member_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        category.delete()
        messages.success(request, "Категория удалена!")
        return redirect("category_list")
    return render(request, "books/confirm_delete.html", {"object": category})


def review_list(request):
    reviews = Review.objects.select_related("book", "book__author")
    return render(request, "books/review_list.html", {"reviews": reviews})


def review_detail(request, pk):
    review = get_object_or_404(Review.objects.select_related("book"), pk=pk)
    return render(request, "books/review_detail.html", {"review": review})


def review_create(request):
    form = ReviewForm(request.POST or None)
    if form.is_valid():
        review = form.save()
        messages.success(request, "Отзыв добавлен!")
        return redirect("review_detail", pk=review.pk)
    return render(request, "books/form.html", {"form": form, "title": "Добавить отзыв"})


@staff_member_required
def review_update(request, pk):
    review = get_object_or_404(Review, pk=pk)
    form = ReviewForm(request.POST or None, instance=review)
    if form.is_valid():
        form.save()
        messages.success(request, "Отзыв изменён!")
        return redirect("review_detail", pk=review.pk)
    return render(request, "books/form.html", {"form": form, "title": "Изменить отзыв"})


@staff_member_required
def review_delete(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.method == "POST":
        review.delete()
        messages.success(request, "Отзыв удалён!")
        return redirect("review_list")
    return render(request, "books/confirm_delete.html", {"object": review})


def statistics(request):
    stats = Book.objects.aggregate(
        total_books=Count("id"),
        avg_price=Avg("price"),
        max_price=Max("price"),
        min_price=Min("price"),
        total_price=Sum("price"),
        total_pages=Sum("pages"),
    )
    avg_rating = Review.objects.aggregate(avg=Avg("rating"))["avg"]
    in_stock = Book.objects.filter(in_stock=True).aggregate(count=Count("id"))["count"]

    top_authors = Author.objects.annotate(books_count=Count("books")).order_by("-books_count")[:5]
    top_books = Book.objects.annotate(avg_rating=Avg("reviews__rating")).filter(
        avg_rating__isnull=False
    ).order_by("-avg_rating")[:5]
    good_books = Book.objects.annotate(avg_rating=Avg("reviews__rating")).filter(avg_rating__gt=4)
    last_reviews = Review.objects.select_related("book", "book__author")[:5]

    return render(request, "books/statistics.html", {
        "stats": stats,
        "avg_rating": avg_rating,
        "in_stock": in_stock,
        "top_authors": top_authors,
        "top_books": top_books,
        "good_books": good_books,
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
            messages.success(request, "Вы успешно зарегистрировались!")
            return redirect("book_list")
    else:
        form = RegisterForm()
    return render(request, "registration/register.html", {"form": form})


@login_required
def cart(request):
    items = Cart.objects.filter(user=request.user).select_related("book")
    total = 0
    for item in items:
        item.sum = item.book.price * item.quantity
        total += item.sum
    return render(request, "books/cart.html", {"items": items, "total": total})


@login_required
def add_to_cart(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if not book.in_stock:
        messages.error(request, "Этой книги нет в наличии")
        return redirect("book_detail", pk=pk)

    item = Cart.objects.filter(user=request.user, book=book).first()
    if item:
        item.quantity += 1
        item.save()
    else:
        Cart.objects.create(user=request.user, book=book)
    messages.success(request, "Книга добавлена в корзину!")
    return redirect("cart")


@login_required
def remove_from_cart(request, pk):
    item = get_object_or_404(Cart, pk=pk, user=request.user)
    item.delete()
    messages.success(request, "Книга убрана из корзины")
    return redirect("cart")


@login_required
def checkout(request):
    items = Cart.objects.filter(user=request.user).select_related("book")
    if not items:
        messages.error(request, "Корзина пустая")
        return redirect("cart")

    order = Order.objects.create(user=request.user)
    total = 0
    for item in items:
        OrderItem.objects.create(order=order, book=item.book, price=item.book.price, quantity=item.quantity)
        total += item.book.price * item.quantity
    order.total = total
    order.save()
    items.delete()

    messages.success(request, "Заказ оформлен! Теперь оплатите его.")
    return redirect("my_orders")


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).prefetch_related("items__book")
    return render(request, "books/my_orders.html", {"orders": orders})


@login_required
def pay_order(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    order.is_paid = True
    order.save()
    messages.success(request, "Заказ оплачен! Спасибо за покупку.")
    return redirect("my_orders")


@staff_member_required
def sales(request):
    items = OrderItem.objects.select_related("order", "order__user", "book").order_by("-order__created_at")
    total_money = Order.objects.filter(is_paid=True).aggregate(total=Sum("total"))["total"] or 0
    return render(request, "books/sales.html", {"items": items, "total_money": total_money})
