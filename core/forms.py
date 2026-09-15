from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

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

    def limpa_email(self):
        email = self.cleaned_data["email"].strp().lower()
        if User.objects.filter(email__iexact = email).exists():
            raise ValidationError("Já existe uma conta cadastrada com esse email.")
        return email

    def limpa_senha(self):
        senha = self.cleaned_data.get("senha", "")
        if not any(char.isdigit() for char in senha):
            raise ValidationError("A senha precisa ter um numero.")

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