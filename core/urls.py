from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.cadastro_view, name="index"),
    path("login/", views.login_view, name="login"),
    path("cadastro/", views.cadastro_view, name="cadastro"),
    path("logout/", views.logout_view, name="logout"),
]