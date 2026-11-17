from django import forms
from django.contrib.auth.models import User
from .models import Author, Category, Book, Review


class RegisterForm(forms.Form):
    username = forms.CharField(label="Имя", max_length=150)
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Такое имя уже занято")
        return username


class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = "__all__"


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = "__all__"


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = "__all__"
        widgets = {
            "categories": forms.CheckboxSelectMultiple(),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["book", "reviewer_name", "rating", "comment"]

    def clean_rating(self):
        rating = self.cleaned_data["rating"]
        if rating < 1 or rating > 5:
            raise forms.ValidationError("Оценка должна быть от 1 до 5")
        return rating


class BookReviewForm(ReviewForm):
    class Meta:
        model = Review
        fields = ["reviewer_name", "rating", "comment"]
