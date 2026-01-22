"""
Pytest configuration for Django WebAssembly tests.

pytest-django handles Django setup automatically via the DJANGO_SETTINGS_MODULE
in pyproject.toml. This file only contains fixtures.
"""

import pytest


@pytest.fixture
def sample_question(db):
    """Create a sample question for testing."""
    from django.utils import timezone

    from django_webassembly.polls.models import Question

    return Question.objects.create(
        question_text="Test question?",
        pub_date=timezone.now(),
    )


@pytest.fixture
def sample_question_with_choices(sample_question):
    """Create a sample question with choices for testing."""
    from django_webassembly.polls.models import Choice

    Choice.objects.create(question=sample_question, choice_text="Choice 1", votes=0)
    Choice.objects.create(question=sample_question, choice_text="Choice 2", votes=5)
    Choice.objects.create(question=sample_question, choice_text="Choice 3", votes=3)
    return sample_question


@pytest.fixture
def admin_user(db):
    """Create an admin user for testing."""
    from django.contrib.auth.models import User

    return User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="adminpass123",
    )


@pytest.fixture
def client():
    """Return Django test client."""
    from django.test import Client

    return Client()


@pytest.fixture
def authenticated_client(client, admin_user):
    """Return authenticated Django test client."""
    client.login(username="admin", password="adminpass123")
    return client
