from django import forms
from django.contrib.auth.models import User
from .models import Category, Product, Review


class RegisterForm(forms.Form):
    username = forms.CharField(label="Имя", max_length=150)
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)
    confirm_password = forms.CharField(label="Повторите пароль", widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Такое имя уже занято")
        return username

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password") != cleaned_data.get("confirm_password"):
            raise forms.ValidationError("Пароли не совпадают")
        return cleaned_data


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = "__all__"


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "category", "quantity", "price", "description"]

    def clean_price(self):
        price = self.cleaned_data["price"]
        if price < 0:
            raise forms.ValidationError("Цена не может быть меньше 0")
        return price


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["product", "rating", "comment"]

    def clean_rating(self):
        rating = self.cleaned_data["rating"]
        if rating < 1 or rating > 5:
            raise forms.ValidationError("Оценка должна быть от 1 до 5")
        return rating


class ProductReviewForm(ReviewForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]
