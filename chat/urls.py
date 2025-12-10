from django.contrib import admin
from django.urls import path


from . import views

app_name = "chat"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    # path("thread", views.thread, name="thread"),
    path("thread/new", views.CreateThreadView.as_view(), name="thread_new"),
    path("thread/<int:pk>", views.ThreadDetailView.as_view(), name="thread_detail"),
    path("login", views.LoginView.as_view(), name="login"),
]
# path("<int:pk>/", views.DetailView.as_view(), name="detail"),
# path("<int:pk>/results/", views.ResultView.as_view(), name="results"),
# path("<int:question_id>/vote/", views.vote, name="vote"),
