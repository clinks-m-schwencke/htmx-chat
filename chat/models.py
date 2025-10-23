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

    name = models.CharField(max_length=50)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL)


class Thread(TimeStampedModel):
    """A thread within a project"""

    project_id = models.ForeignKey(Project, on_delete=models.CASCADE)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="author",
    )
    watchers = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="user_watches_thread"
    )
    body = models.TextField()
    is_edited = models.BooleanField()
    is_deleted = models.BooleanField()


class Message(TimeStampedModel):
    """An individual message within a thread"""

    thread_id = models.ForeignKey(Thread, on_delete=models.CASCADE)
    body = models.TextField()
    is_edited = models.BooleanField()
    is_deleted = models.BooleanField()
