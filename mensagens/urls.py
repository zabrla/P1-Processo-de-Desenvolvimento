from django.urls import path
from . import views

urlpatterns = [
    path('criptografar/', views.criptografar, name='criptografar'),
    path('criptografar/salvar/', views.salvar_arquivo, name='salvar_arquivo'),
]