from django.urls import path
from . import views

app_name = "mensagens"

urlpatterns = [
    path('criptografar/', views.criptografar, name='criptografar'),
    path('criptografar/salvar/', views.salvar_arquivo, name='salvar_arquivo'),
    path('descriptografar/', views.descriptografar, name='descriptografar'),
    path('logs/', views.historico_logs, name='historico_logs'),
]