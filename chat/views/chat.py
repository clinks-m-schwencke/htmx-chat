from django.shortcuts import render
from django.views import generic

from django.db.models import Subquery, OuterRef

from chat.models import Thread, Message


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
