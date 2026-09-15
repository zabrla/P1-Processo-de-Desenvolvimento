from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import CadastroForm

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
    return render(request, "core/login.html", {"form": None})        