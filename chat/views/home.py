from django.shortcuts import render
from django.views import generic

from django.db.models import Subquery, OuterRef

from chat.models import Thread, Message

# class IndexView(generic.ListView):
#     template_name = "polls/index.html"
#     context_object_name = "latest_question_list"
#
#     def get_queryset(self):
#         """Return the last 5 publised questions"""
#         return Question.objects.filter(pub_date__lte=timezone.now()).order_by(
#             "-pub_date"
#         )[:5]
#


# class IndexView(generic.ListView):
#     template_name = "chat/index.html"
#     context_object_name = "thread_list"
#
#     def get_queryset(self):
#         """Return the last 5 publised questions"""
#         return Thread.objects.order_by("-updated_at")[:5]


def index(request):
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
        .order_by("is_resolved", "-updated_at")[:5]
    )
    context = {
        "thread_list": thread_list,
    }

    return render(request, "chat/index.html", context)
