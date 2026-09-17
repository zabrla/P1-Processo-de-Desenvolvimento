from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = "mensagens"

urlpatterns = [
    path('historico/', TemplateView.as_view(template_name='historico.html'), name='historico'),
    path('criptografar/', views.criptografar, name='criptografar'),
    path('criptografar/salvar/', views.salvar_arquivo, name='salvar_arquivo'),
    path('descriptografar/', views.descriptografar, name='descriptografar'),
]
