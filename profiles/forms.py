from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email


class UserRegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

        labels = {
            "username": "Логин",
            "email": "Электронная почта",
            "password": "Пароль",
        }

        widgets = {
            'username': forms.TextInput(),
            'email': forms.EmailInput(),
            'password': forms.PasswordInput(),
        }

    repeat_password = forms.CharField(max_length=32, widget=forms.PasswordInput(), label='Повторите пароль')

    def clean_password(self):
        password = self.cleaned_data.get('password', '')
        repeat_password = self.cleaned_data.get('password', '')

        pass_len = len(password)
        if pass_len < 6 or pass_len > 32:
            raise ValidationError('Пароль должен содержать от 6 до 32 символов.')
        elif password != repeat_password:
            raise ValidationError('Введенные пароли не совпадают.')

        return password

    def clean_email(self):
        email = self.cleaned_data.get('email', '')
        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError('Введен некорректный e-mail.')

        user = User.objects.filter(email=email)
        if user:
            raise ValidationError('Данный email занят, введите другой или воспользуйтесь сбросом пароля')

        return email

    def clean_username(self):
        username = self.cleaned_data.get('username', '')

        username_len = len(username)
        if username_len < 4 or username_len > 150:
            raise ValidationError('Логин должен содержать от 4 до 150 символов.')

        user = User.objects.filter(username=username)
        if user:
            raise ValidationError('Данный логин занят, введите другой')

        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['password', 'email']

        labels = {
            "password": "Текущий пароль",
            "email": "Электронная почта",
        }

        widgets = {
            'password': forms.PasswordInput(),
            'email': forms.EmailInput(),
        }

    new_password = forms.CharField(max_length=32, required=False, widget=forms.PasswordInput(), label='Новый пароль')
    repeat_new_password = forms.CharField(max_length=32, required=False, widget=forms.PasswordInput(),
                                          label='Повторите новый пароль')

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = False
        self.user = user

    def clean_password(self):
        password = self.cleaned_data.get('password', '')

        if not self.user.check_password(password):
            raise ValidationError('Старый пароль не верен')

        return password

    def clean_email(self):
        email = self.cleaned_data.get('email', '')

        if not email:
            return email

        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError('Введен некорректный e-mail.')

        user = User.objects.filter(email=email)
        if user:
            raise ValidationError('Данный email занят, введите другой или воспользуйтесь сбросом пароля')

        return email

    def clean_new_password(self):
        new_password = self.cleaned_data.get('new_password', '')

        if not new_password:
            return new_password

        new_password_len = len(new_password)
        if new_password_len < 6 or new_password_len > 32:
            raise ValidationError('Пароль должен содержать от 6 до 32 символов.')

        return new_password

    def clean_repeat_new_password(self):
        repeat_new_password = self.cleaned_data.get('repeat_new_password', '')
        new_password = self.cleaned_data.get('new_password', '')

        if new_password != repeat_new_password:
            raise ValidationError(f'Новые пароли не совпадают {new_password} != {repeat_new_password}')

        return repeat_new_password

    def save(self, commit=True):
        if self.cleaned_data["new_password"]:
            self.user.set_password(self.cleaned_data["new_password"])
        if self.cleaned_data["email"]:
            self.user.email = self.cleaned_data["email"]

        if commit:
            self.user.save()
        return self.user
