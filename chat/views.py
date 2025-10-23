from django.shortcuts import render
from django.views import generic
from django.contrib.auth import views as auth_views


# Create your views here.
class LoginView(auth_views.LoginView):
    template_name = "chat/login.html"
    pass


# class IndexView(generic.ListView):
#     template_name = "chat/index.html"
#     # context_object_name = "latest_question_list"
#     #
#     # def get_queryset(self):
#     #     """Return the last 5 publised questions"""
#     #     return Question.objects.filter(pub_date__lte=timezone.now()).order_by(
#     #         "-pub_date"
#     #     )[:5]


# class IndexView(generic.View):
#     template_name = "chat/index.html"


def index(request):
    context = {}

    return render(request, "chat/index.html", context)
