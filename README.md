# Магазин продуктов (Django)

Проект на Django (MVT). Таблицы: Category, Product, Review, Cart, Order, OrderItem.
Каждый пользователь может добавлять свои продукты. У продукта есть ID, ID пользователя, который его добавил,
название, категория, количество, цена и описание. ID показываются на всех страницах.
Ещё есть регистрация, вход, корзина, заказы и оплата. Админ видит, кто что купил.

## Запуск

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations main
python manage.py migrate
python manage.py shell < create_admin.py
python manage.py runserver
```

Админ: логин `admin`, пароль `907840505`

## Страницы

- `/products/` - продукты (поиск, фильтры, сортировка, пагинация)
- `/products/my/` - мои продукты
- `/categories/` - категории
- `/users/` - продавцы
- `/reviews/` - отзывы
- `/statistics/` - статистика
- `/register/`, `/login/` - регистрация (имя, пароль, повтор пароля) и вход (имя, пароль)
- `/cart/` - корзина
- `/orders/` - мои заказы
- `/sales/` - продажи (только админ)
- `/admin/` - админка

## Права

- Добавлять продукты и категории может любой зарегистрированный пользователь.
- Изменять и удалять продукт может только тот, кто его добавил (или админ).
- Изменять и удалять категории может только админ.

## Сравнение запросов

Запуск: `python manage.py shell < check_queries.py`
