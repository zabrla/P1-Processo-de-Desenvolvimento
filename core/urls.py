from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.login_view, name="login"),
    path("cadastro/", views.cadastro_view, name="cadastro"),
]