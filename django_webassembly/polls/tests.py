"""
Django TestCase-based tests for the polls app.

These tests can be run with `python manage.py test` as an alternative to pytest.
"""

import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Choice, Question


def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for past, positive for future).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionModelTests(TestCase):
    """Tests for the Question model."""

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        future_question = create_question("Future?", days=30)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        old_question = create_question("Old?", days=-2)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        recent_question = create_question("Recent?", days=0)
        self.assertIs(recent_question.was_published_recently(), True)

    def test_question_str(self):
        """Test string representation of Question."""
        question = Question(question_text="Test question?")
        self.assertEqual(str(question), "Test question?")


class ChoiceModelTests(TestCase):
    """Tests for the Choice model."""

    def test_choice_str(self):
        """Test string representation of Choice."""
        question = create_question("Test?", days=0)
        choice = Choice(question=question, choice_text="Test choice")
        self.assertEqual(str(choice), "Test choice")

    def test_choice_default_votes(self):
        """Test that votes default to 0."""
        question = create_question("Test?", days=0)
        choice = Choice.objects.create(question=question, choice_text="Test")
        self.assertEqual(choice.votes, 0)


class QuestionIndexViewTests(TestCase):
    """Tests for the polls index view."""

    def test_no_questions(self):
        """If no questions exist, an appropriate message is displayed."""
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_past_question(self):
        """Questions with a pub_date in the past are displayed."""
        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_two_past_questions(self):
        """The questions index page may display multiple questions."""
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question2, question1],
        )


class QuestionDetailViewTests(TestCase):
    """Tests for the polls detail view."""

    def test_nonexistent_question(self):
        """Detail view returns 404 for nonexistent question."""
        url = reverse("polls:detail", args=(99999,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_existing_question(self):
        """Detail view displays question text."""
        question = create_question(question_text="Test question?", days=-5)
        url = reverse("polls:detail", args=(question.id,))
        response = self.client.get(url)
        self.assertContains(response, question.question_text)


class VoteViewTests(TestCase):
    """Tests for the vote view."""

    def test_vote_increments_count(self):
        """Voting for a choice increments its vote count."""
        question = create_question("Test?", days=0)
        choice = Choice.objects.create(question=question, choice_text="Test", votes=0)

        url = reverse("polls:vote", args=(question.id,))
        self.client.post(url, {"choice": choice.id})

        choice.refresh_from_db()
        self.assertEqual(choice.votes, 1)

    def test_vote_redirects_to_results(self):
        """Voting redirects to the results page."""
        question = create_question("Test?", days=0)
        choice = Choice.objects.create(question=question, choice_text="Test", votes=0)

        url = reverse("polls:vote", args=(question.id,))
        response = self.client.post(url, {"choice": choice.id})

        self.assertRedirects(
            response,
            reverse("polls:results", args=(question.id,)),
        )
