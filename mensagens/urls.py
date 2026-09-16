from django.urls import path
from . import views

app_name = "mensagens"

urlpatterns = [
    path('criptografar/', views.criptografar, name='criptografar'),
    path('criptografar/salvar/', views.salvar_arquivo, name='salvar_arquivo'),
]