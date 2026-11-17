# Электронная библиотека (Django)

Проект на Django (MVT). 4 таблицы: Author, Category, Book, Review. Для всех есть CRUD.
Ещё есть регистрация, вход, корзина, заказы и оплата. Админ видит, кто какую книгу купил.

## Запуск

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations books
python manage.py migrate
python manage.py shell < create_admin.py
python manage.py runserver
```

Если `<` не работает (PowerShell):
```
Get-Content create_admin.py | python manage.py shell
```

Админ: логин `admin`, пароль `907840505`

## Страницы

- `/books/` - книги (поиск, фильтры, сортировка, пагинация)
- `/authors/` - авторы
- `/categories/` - категории
- `/reviews/` - отзывы
- `/statistics/` - статистика
- `/register/`, `/login/` - регистрация и вход
- `/cart/` - корзина
- `/orders/` - мои заказы
- `/sales/` - продажи (только админ)
- `/admin/` - админка

## Сравнение запросов

Запуск: `python manage.py shell < check_queries.py`

| Страница | Без оптимизации | С оптимизацией |
|---|---|---|
| Список книг | ... | 2 |
| Список отзывов | ... | 1 |
| Авторы с книгами | ... | 3 |
