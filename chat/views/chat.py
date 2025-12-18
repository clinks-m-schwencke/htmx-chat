from django.shortcuts import render
from django.views import generic

from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseNotAllowed,
    HttpResponseRedirect,
)

from django.db.models import Subquery, OuterRef
from django.shortcuts import get_object_or_404, render
from django.template.response import TemplateResponse

from chat.models import Thread, Message


def chat_handler(request, thread_id):
    match request.method:
        case "POST":
            return chat_post(request, thread_id)
        case "PUT":
            return chat_put(request, thread_id)
        # case "PUT":
        #     return thread_put(request, thread_id)
        case _:
            return HttpResponseNotAllowed(["GET", "POST"])


def chat_post(request, thread_id):
    thread = get_object_or_404(Thread, pk=thread_id)
    message = request.POST.get("message")

    if not message or message.strip() == "":
        response = HttpResponse()
        response.status_code = 422  # Unprocessable entity
        return response

    obj = Message(body=message, author=request.user, thread_id=thread)
    obj.save()
    return TemplateResponse(request, "chat/thread_detail.html#message_form", {})


def chat_put(request, thread_id):
    pass


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
