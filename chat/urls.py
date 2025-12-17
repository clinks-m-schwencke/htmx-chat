from django.contrib import admin
from django.urls import path


from . import views

app_name = "chat"
urlpatterns = [
    path("", views.index, name="index"),
    path("thread", views.thread_handler, name="thread"),
    path("thread/new", views.thread_new, name="thread_new"),
    path("thread/create", views.CreateThreadView.as_view(), name="thread_create"),
    path("thread/<int:pk>", views.thread_get, name="thread_detail"),
    # path("thread/<int:pk>", views.thread_get, name="thread_detail"),
    path("login", views.LoginView.as_view(), name="login"),
]
# path("<int:pk>/", views.DetailView.as_view(), name="detail"),
# path("<int:pk>/results/", views.ResultView.as_view(), name="results"),
# path("<int:question_id>/vote/", views.vote, name="vote"),
