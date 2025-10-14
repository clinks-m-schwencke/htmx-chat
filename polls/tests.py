import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question

# Create your tests here.


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date is 1 day in the past.
        """
        time = timezone.now() + datetime.timedelta(hours=-23)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date is more than 1 day in the past.
        """
        time = timezone.now() + datetime.timedelta(days=-2)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)


def create_questions(question_text, days):
    """
    Create a question with the given `question text` and published the given number of `days`
    offset to now (negative for past, positive for future).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed
        """
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_past_question(self):
        """
        Questions with a pub date in the past are displayed on the index page.
        """
        question = create_questions("Past question.", -30)
        response = self.client.get(reverse("polls:index"))

        self.assertQuerySetEqual(response.context["latest_question_list"], [question])

    def test_future_question(self):
        """
        Questions with a pub date in the future are not displayed on the index page.
        """
        create_questions("Future question.", 1)
        response = self.client.get(reverse("polls:index"))

        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_future_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions are displayed
        """
        create_questions("Future question.", 1)
        question = create_questions("Past question.", -30)
        response = self.client.get(reverse("polls:index"))

        self.assertQuerySetEqual(response.context["latest_question_list"], [question])

    def test_two_past_questions(self):
        """
        Multiple past questions can be displayed
        """
        question1 = create_questions("Old question", -30)
        question2 = create_questions("recent question.", -1)
        response = self.client.get(reverse("polls:index"))

        self.assertQuerySetEqual(
            response.context["latest_question_list"], [question2, question1]
        )
