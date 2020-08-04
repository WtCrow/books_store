from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.models import User
from django import forms


class UserRegistrationForm(forms.ModelForm):
    """Registration form

    Use default user from django.auth.
    fields:
    login, email, password, repeat password and checkbox for license

    Create new user or return errors form

    """

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
    is_license = forms.BooleanField(label='Я принимаю')

    def clean_password(self):
        password = self.cleaned_data.get('password', '')

        if not 6 < len(password) < 32:
            raise ValidationError('Пароль должен содержать от 6 до 32 символов.')

        return password

    def clean_repeat_password(self):
        password = self.cleaned_data.get('password', '')
        repeat_password = self.cleaned_data.get('repeat_password', '')

        if repeat_password != password:
            raise ValidationError('Введенные пароли не совпадают.')

        return repeat_password

    def clean_email(self):
        email = self.cleaned_data.get('email', '')
        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError('Введен некорректный e-mail.')

        if User.objects.filter(email=email):
            raise ValidationError('Данный email занят, введите другой или воспользуйтесь сбросом пароля.')

        return email

    def clean_username(self):
        username = self.cleaned_data.get('username', '')

        username_len = len(username)
        if username_len < 4 or username_len > 150:
            raise ValidationError('Логин должен содержать от 4 до 150 символов.')

        if User.objects.filter(username=username):
            raise ValidationError('Данный логин занят, введите другой.')

        return username

    def clean_is_license(self):
        is_license = self.cleaned_data.get('is_license', '')

        if not is_license:
            raise ValidationError('Примите лицензионное соглашение.')

        return is_license

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UserEditForm(forms.ModelForm):
    """Form for edit email and/or password. For edit information, need write current password."""

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
        # change required for model field
        self.fields['email'].required = False
        self.user = user

    def clean_password(self):
        password = self.cleaned_data.get('password', '')

        if not self.user.check_password(password):
            raise ValidationError('Старый пароль не верен.')

        return password

    def clean_email(self):
        email = self.cleaned_data.get('email', '')

        if not email:
            return email

        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError('Введен некорректный e-mail.')

        if User.objects.filter(email=email):
            raise ValidationError('Данный email занят, введите другой или воспользуйтесь сбросом пароля.')

        return email

    def clean_new_password(self):
        new_password = self.cleaned_data.get('new_password', '')
        repeat_new_password = self.cleaned_data.get('repeat_new_password', '')

        if not (new_password and repeat_new_password):
            return new_password

        if (not new_password and repeat_new_password) or (new_password and not repeat_new_password):
            raise ValidationError('Повторите новый пароль.')

        if not 6 < len(new_password) < 32:
            raise ValidationError('Пароль должен содержать от 6 до 32 символов.')

        return new_password

    def clean_repeat_new_password(self):
        repeat_new_password = self.cleaned_data.get('repeat_new_password', '')
        new_password = self.cleaned_data.get('new_password', '')

        if new_password != repeat_new_password:
            raise ValidationError('Новые пароли не совпадают')

        return repeat_new_password

    def save(self, commit=True):
        if self.cleaned_data["new_password"]:
            self.user.set_password(self.cleaned_data["new_password"])
        if self.cleaned_data["email"]:
            self.user.email = self.cleaned_data["email"]

        if commit:
            self.user.save()
        return self.user
