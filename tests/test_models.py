"""
Tests for Django WebAssembly models.
"""

import datetime

import pytest
from django.utils import timezone

from django_webassembly.polls.models import Choice, Question


@pytest.mark.django_db
class TestQuestionModel:
    """Tests for the Question model."""

    def test_create_question(self):
        """Test creating a question."""
        question = Question.objects.create(
            question_text="What is your favorite color?",
            pub_date=timezone.now(),
        )
        assert question.pk is not None
        assert question.question_text == "What is your favorite color?"

    def test_question_str(self):
        """Test question string representation."""
        question = Question(question_text="Test question?")
        assert str(question) == "Test question?"

    def test_was_published_recently_with_recent_question(self):
        """was_published_recently() returns True for recent questions."""
        recent_time = timezone.now() - datetime.timedelta(hours=23)
        recent_question = Question(pub_date=recent_time)
        assert recent_question.was_published_recently() is True

    def test_was_published_recently_with_old_question(self):
        """was_published_recently() returns False for old questions."""
        old_time = timezone.now() - datetime.timedelta(days=2)
        old_question = Question(pub_date=old_time)
        assert old_question.was_published_recently() is False

    def test_was_published_recently_with_future_question(self):
        """was_published_recently() returns False for future questions."""
        future_time = timezone.now() + datetime.timedelta(days=1)
        future_question = Question(pub_date=future_time)
        assert future_question.was_published_recently() is False


@pytest.mark.django_db
class TestChoiceModel:
    """Tests for the Choice model."""

    def test_create_choice(self, sample_question):
        """Test creating a choice."""
        choice = Choice.objects.create(
            question=sample_question,
            choice_text="Test choice",
            votes=0,
        )
        assert choice.pk is not None
        assert choice.choice_text == "Test choice"
        assert choice.votes == 0

    def test_choice_str(self, sample_question):
        """Test choice string representation."""
        choice = Choice(question=sample_question, choice_text="Test choice")
        assert str(choice) == "Test choice"

    def test_choice_question_relationship(self, sample_question):
        """Test choice-question foreign key relationship."""
        choice = Choice.objects.create(
            question=sample_question,
            choice_text="Related choice",
            votes=0,
        )
        assert choice.question == sample_question
        assert choice in sample_question.choice_set.all()

    def test_choice_default_votes(self, sample_question):
        """Test that choice votes default to 0."""
        choice = Choice.objects.create(
            question=sample_question,
            choice_text="No votes specified",
        )
        assert choice.votes == 0

    def test_increment_votes(self, sample_question):
        """Test incrementing choice votes."""
        choice = Choice.objects.create(
            question=sample_question,
            choice_text="Popular choice",
            votes=0,
        )
        choice.votes += 1
        choice.save()

        choice.refresh_from_db()
        assert choice.votes == 1


@pytest.mark.django_db
class TestModelRelationships:
    """Tests for model relationships."""

    def test_question_choices_cascade_delete(self, sample_question_with_choices):
        """Test that deleting a question deletes its choices."""
        question_pk = sample_question_with_choices.pk
        choice_count = Choice.objects.filter(question_id=question_pk).count()
        assert choice_count == 3

        sample_question_with_choices.delete()

        assert Choice.objects.filter(question_id=question_pk).count() == 0

    def test_multiple_questions_independent(self):
        """Test that multiple questions have independent choices."""
        q1 = Question.objects.create(
            question_text="Question 1?",
            pub_date=timezone.now(),
        )
        q2 = Question.objects.create(
            question_text="Question 2?",
            pub_date=timezone.now(),
        )

        Choice.objects.create(question=q1, choice_text="Q1 Choice")
        Choice.objects.create(question=q2, choice_text="Q2 Choice A")
        Choice.objects.create(question=q2, choice_text="Q2 Choice B")

        assert q1.choice_set.count() == 1
        assert q2.choice_set.count() == 2
