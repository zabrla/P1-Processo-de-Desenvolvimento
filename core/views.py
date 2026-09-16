from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from .forms import CadastroForm
from .forms import LoginForm

def cadastro_view(request):
    if request.user.is_authenticated:
        return redirect("core:login")

    if request.method == "POST":
        form = CadastroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("core:login")
    else:
        form = CadastroForm()

    return render(request, "core/cadastro.html", {"form": form})


def login_view(request):
    '''if request.user.is_authenticated:
        return redirect("mensagens:criptografar")'''

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            auth_login(request, form.cleaned_data["user"])
            return redirect("mensagens:criptografar")
    else:
        form = LoginForm()

    return render(request, "core/login.html", {"form": form})

def logout_view(request):
    auth_logout(request)
    return redirect("core:login")     