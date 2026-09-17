from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class LoginForm(forms.Form):
    email = forms.EmailField(label="E-mail")
    senha = forms.CharField(label="Senha", widget=forms.PasswordInput)

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get("email", "").strip().lower()
        senha = cleaned.get("senha")

        if email and senha:
            user_obj = User.objects.filter(email__iexact=email).first()
            if user_obj:
                user = authenticate(username=user_obj.username, password=senha)
            else:
                user = None
            if user is None:
                raise ValidationError("E-mail ou senha inválidos.")
            cleaned["user"] = user
        return cleaned

class CadastroForm(forms.Form):

    nome = forms.CharField(
        label="Nome",
        max_length=150,
        error_messages={"required": "Informe seu nome."},
    )

    email = forms.EmailField(
        label="Email",
        error_messages={
            "required": "Informe seu email.",
            "invalid": "Informe um email valido."
        },
    )

    senha = forms.CharField(
        label="Senha",
        widget = forms.PasswordInput,
        min_length=8,
        error_messages={
            "required": "Crie uma senha.",
            "min_length": "A senha precisa ter pelo menos 8 caracteres.",
        },
    )

    confirmar_senha = forms.CharField(
        label = "Confirme sua senha",
        widget = forms.PasswordInput,
        error_messages={"required": "Confirme a senha."},
    )

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Já existe uma conta cadastrada com esse email.")
        return email

    def clean_senha(self):
        senha = self.cleaned_data.get("senha", "")
        if not any(char.isdigit() for char in senha):
            raise ValidationError("A senha precisa ter um número.")
        return senha

    def clean(self):
        cleaned = super().clean()
        senha = cleaned.get("senha")
        confirmar = cleaned.get("confirmar_senha")
        if senha and confirmar and senha != confirmar:
            self.add_error("confirmar_senha", "As senhas precisam ser iguais.")
        return cleaned

    def save(self) -> User:
        data = self.cleaned_data
        return User.objects.create_user(
            username = data["email"],
            email = data["email"],
            password = data["senha"],
            first_name = data["nome"],
        )