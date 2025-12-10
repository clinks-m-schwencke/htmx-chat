from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.views import generic

from django.db.models import Subquery, OuterRef

from chat.models import Thread, Message, Project


class IndexView(generic.ListView):
    template_name = "chat/index.html"
    context_object_name = "thread_list"

    def get_queryset(self):
        """Return threads"""
        newest_message = Message.objects.filter(thread_id=OuterRef("pk")).order_by(
            "-created_at"
        )
        return (
            Thread.objects.filter(is_deleted=False)
            .annotate(
                latest_message_author_name=Subquery(
                    newest_message.select_related("author").values("author")[:1]
                )
            )
            .annotate(latest_message_body=Subquery(newest_message.values("body")[:1]))
            .order_by("is_resolved", "-updated_at")[:5]
        )


class ThreadView(generic.View):
    def post(self, request, *args, **kwargs):
        return CreateThreadView.as_view()(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return ThreadDetailView.as_view()(request, *args, **kwargs)


class ThreadDetailView(generic.DetailView):
    model = Thread
    # fields = ["thread_title", "watchers", "body"]
    template_name = "chat/thread_detail.html"


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
