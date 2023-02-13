from django import forms
from .models import Articles, Comments
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.forms import Textarea


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Articles
        # вместо fields = '__all__' доступны поля 'name', 'text'
        # имя автора заполняется автоматически по авторизованному пользователю
        fields = ('name', 'text')

    # форме добавлен атрибут class и значение form-control
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control mb-2'


class AuthUserForm(AuthenticationForm, forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'password')
    # форме добавлен атрибут class и значение form-control

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control mb-2'


class RegisterUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'password')

    # форме добавлен атрибут class и значение form-control
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control mb-2'

    # переопределен метод создания пользователя, шифрования пароля
    # код django на github - django/django/contrib/auth/forms.py
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ('text', )

    # форме добавлен атрибут class и значение form-control
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control mb-2'
        # задано кол-во строк поля для комментария
        self.fields['text'].widget = Textarea(attrs={'rows': 5})

