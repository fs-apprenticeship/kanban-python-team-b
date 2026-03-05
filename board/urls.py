from django.urls import path

from . import views

app_name = "board"

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("tasks/<uuid:task_id>/modal/", views.task_modal, name="task-modal"),
]
