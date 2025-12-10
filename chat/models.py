from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    """Abstract base class that adds `created_at` and `updated_at` fields to models."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# Create your models here.
class Project(TimeStampedModel):
    """A grouping of members (users) and threads"""

    project_name = models.CharField(max_length=50)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL)

    def __str__(self):
        return str(self.project_name)


class Thread(TimeStampedModel):
    """A thread within a project"""

    project_id = models.ForeignKey(Project, on_delete=models.CASCADE)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="thread_author",
    )
    watchers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="user_watches_thread",
        blank=True,
    )
    thread_title = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)
    resolved_suggesters = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="user_suggests_resolve_for_thread",
        blank=True,
    )

    def __str__(self):
        return str(self.thread_title)


class Message(TimeStampedModel):
    """An individual message within a thread"""

    thread_id = models.ForeignKey(
        Thread, on_delete=models.CASCADE, related_name="thread_messages"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="message_author",
    )
    body = models.TextField()
    is_edited = models.BooleanField()
    is_deleted = models.BooleanField()

    def __str__(self):
        return str(self.body)
