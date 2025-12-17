from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.views import generic
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseNotAllowed,
    HttpResponseRedirect,
)

from django.urls import reverse


from django.db.models import Subquery, OuterRef
from django.template.response import TemplateResponse

from chat.models import Thread, Message, Project
from django.contrib.auth import get_user_model


def index(request: HttpRequest) -> HttpResponse:
    # Latest message fetcher
    newest_message = Message.objects.filter(thread_id=OuterRef("pk")).order_by(
        "-created_at"
    )

    thread_list = (
        Thread.objects.filter(is_deleted=False)
        .annotate(
            latest_message_author_name=Subquery(
                newest_message.select_related("author").values("author")[:1]
            )
        )
        .annotate(latest_message_body=Subquery(newest_message.values("body")[:1]))
        .order_by("is_resolved", "-updated_at")
    )
    return TemplateResponse(request, "chat/index.html", {"thread_list": thread_list})


def thread_handler(request: HttpRequest, thread_id=None) -> HttpResponse:
    match request.method:
        case "POST":
            return thread_post(request)
        case "GET":
            return thread_get(request, thread_id)
        # case "PUT":
        #     return thread_put(request, thread_id)
        case _:
            return HttpResponseNotAllowed(["GET", "POST"])


def thread_post(request: HttpRequest) -> HttpResponse:
    # NOTE: Manual form validation for practice
    # Can also use the 'Form' class
    form_errors = {}

    project = Project.objects.get(pk=1)
    thread_title = request.POST.get("thread_title")
    watchers = request.POST.get("watchers") or []
    body = request.POST.get("body") or ""

    # Check post data for valid form
    if not thread_title or thread_title.strip() == "":
        # If form is invalid, return 422 unprocessable content
        watchers = get_user_model().objects.exclude(id=request.user.id)
        return TemplateResponse(
            request,
            "chat/thread_form.html",
            {
                "is_new": True,
                "watchers": watchers,
                "error_message": "Title empty",  # TODO: Make proper translation string
            },
        )

    # Form is valid!
    new_thread = Thread(
        project_id=project,
        thread_title=thread_title,
        body=body,
        author=request.user,
    )
    # Save once to generate id (needed for watchers)
    new_thread.save()
    new_thread.watchers.set(watchers)
    # Save watchers
    new_thread.save()

    return HttpResponseRedirect(reverse("chat:thread_detail", args=(new_thread.pk,)))


def thread_get(request: HttpRequest, pk) -> HttpResponse:
    context = {"object": get_object_or_404(Thread, pk=pk)}
    return TemplateResponse(request, "chat/thread_detail.html", context)


def thread_put(request: HttpRequest) -> HttpResponse:
    pass


def thread_new(request: HttpRequest) -> HttpResponse:
    watchers = get_user_model().objects.exclude(id=request.user.id)
    return TemplateResponse(
        request,
        "chat/thread_form.html",
        {
            "is_new": True,
            "watchers": watchers,
        },
    )


class CreateThreadView(LoginRequiredMixin, generic.CreateView):
    model = Thread
    fields = ["thread_title", "watchers", "body"]
    template_name = "chat/create_thread.html"

    success_url = "/"

    def form_valid(self, form):
        # Set default project
        project = Project.objects.get(pk=1)
        form.instance.project_id = project

        form.instance.author = self.request.user
        # print(
        #     "[DEBUG]", "CreateThreadView", "form_valid", form.cleaned_data["watchers"]
        # )
        # form.save()
        # if not form.cleaned_data["watchers"].exists():
        #     print("[DEBUG]", "didn't provide any watchers")
        #     form.instance.watchers.set([self.request.user])

        return super().form_valid(form)


# def thread_new(request):
#      = get_object_or_404(Question, pk=question_id)
#     try:
#         selected_choice = question.choice_set.get(pk=request.POST["choice"])
#     except (KeyError, Choice.DoesNotExist):
#         # Rerender the form with an error
#         return render(
#             request,
#             "polls/details.html",
#             {
#                 "question": question,
#                 "error_message": "You didn't select a choice.",
#             },
#             # Not in tutorial, but you should return error status codes on an error!
#             status=HTTPStatus.Un,
#         )
#     else:
#         selected_choice.votes = F("votes") + 1
#         selected_choice.save()
#
#         # Always return an HttpResponseRedirect after successfully dealing
#         # with POST data. This prevents data from being posted twice if a
#         # user hits the Back button.
#         return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))

# def index(request):
#     newest_message = Message.objects.filter(thread_id=OuterRef("pk")).order_by(
#         "-created_at"
#     )
#     thread_list = (
#         Thread.objects.filter(is_deleted=False)
#         .annotate(
#             latest_message_author_name=Subquery(
#                 newest_message.select_related("author").values("author")[:1]
#             )
#         )
#         .annotate(latest_message_body=Subquery(newest_message.values("body")[:1]))
#         .order_by("is_resolved", "-updated_at")[:5]
#     )
#     context = {
#         "thread_list": thread_list,
#     }
#
#     return render(request, "chat/index.html", context)


# def create_thread(request):
#     context = {}
#     return render(request, "chat/create_thread.html", context)
