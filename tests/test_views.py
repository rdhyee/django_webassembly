"""
Tests for Django WebAssembly views.
"""

import pytest
from django.urls import reverse
from django.utils import timezone

from django_webassembly.polls.models import Choice, Question


@pytest.mark.django_db
class TestIndexView:
    """Tests for the main index view."""

    def test_index_view_status(self, client):
        """Test that index view returns 200."""
        response = client.get(reverse("index"))
        assert response.status_code == 200

    def test_index_view_template(self, client):
        """Test that index view uses correct template."""
        response = client.get(reverse("index"))
        assert "django_webassembly/index.html" in [t.name for t in response.templates]

    def test_index_view_contains_links(self, client):
        """Test that index view contains expected links."""
        response = client.get(reverse("index"))
        content = response.content.decode()
        assert "/polls" in content
        assert "/admin" in content


@pytest.mark.django_db
class TestPollsIndexView:
    """Tests for the polls index view."""

    def test_polls_index_no_questions(self, client):
        """Test polls index with no questions."""
        response = client.get(reverse("polls:index"))
        assert response.status_code == 200
        assert "No polls are available." in response.content.decode()

    def test_polls_index_with_questions(self, client, sample_question):
        """Test polls index with questions."""
        response = client.get(reverse("polls:index"))
        assert response.status_code == 200
        assert sample_question.question_text in response.content.decode()

    def test_polls_index_shows_latest_five(self, client):
        """Test that polls index shows only latest 5 questions."""
        for i in range(7):
            Question.objects.create(
                question_text=f"Question {i}?",
                pub_date=timezone.now(),
            )

        response = client.get(reverse("polls:index"))
        # Should show 5 questions
        assert len(response.context["latest_question_list"]) == 5


@pytest.mark.django_db
class TestPollsDetailView:
    """Tests for the polls detail view."""

    def test_detail_view_exists(self, client, sample_question):
        """Test that detail view exists for valid question."""
        url = reverse("polls:detail", args=[sample_question.pk])
        response = client.get(url)
        assert response.status_code == 200

    def test_detail_view_shows_question(self, client, sample_question):
        """Test that detail view shows question text."""
        url = reverse("polls:detail", args=[sample_question.pk])
        response = client.get(url)
        assert sample_question.question_text in response.content.decode()

    def test_detail_view_shows_choices(self, client, sample_question_with_choices):
        """Test that detail view shows all choices."""
        url = reverse("polls:detail", args=[sample_question_with_choices.pk])
        response = client.get(url)
        content = response.content.decode()

        for choice in sample_question_with_choices.choice_set.all():
            assert choice.choice_text in content

    def test_detail_view_404_for_nonexistent(self, client):
        """Test that detail view returns 404 for nonexistent question."""
        url = reverse("polls:detail", args=[99999])
        response = client.get(url)
        assert response.status_code == 404


@pytest.mark.django_db
class TestPollsResultsView:
    """Tests for the polls results view."""

    def test_results_view_exists(self, client, sample_question):
        """Test that results view exists for valid question."""
        url = reverse("polls:results", args=[sample_question.pk])
        response = client.get(url)
        assert response.status_code == 200

    def test_results_view_shows_votes(self, client, sample_question_with_choices):
        """Test that results view shows vote counts."""
        url = reverse("polls:results", args=[sample_question_with_choices.pk])
        response = client.get(url)
        content = response.content.decode()

        # Check that votes are displayed
        assert "5" in content  # Choice 2 has 5 votes
        assert "3" in content  # Choice 3 has 3 votes


@pytest.mark.django_db
class TestVoteView:
    """Tests for the vote view."""

    def test_vote_increments_count(self, client, sample_question_with_choices):
        """Test that voting increments the choice count."""
        choice = sample_question_with_choices.choice_set.first()
        initial_votes = choice.votes

        url = reverse("polls:vote", args=[sample_question_with_choices.pk])
        response = client.post(url, {"choice": choice.pk})

        choice.refresh_from_db()
        assert choice.votes == initial_votes + 1

    def test_vote_redirects_to_results(self, client, sample_question_with_choices):
        """Test that voting redirects to results page."""
        choice = sample_question_with_choices.choice_set.first()

        url = reverse("polls:vote", args=[sample_question_with_choices.pk])
        response = client.post(url, {"choice": choice.pk})

        assert response.status_code == 302
        assert f"/polls/{sample_question_with_choices.pk}/results/" in response.url

    def test_vote_without_choice_shows_error(self, client, sample_question_with_choices):
        """Test that voting without a choice shows an error."""
        url = reverse("polls:vote", args=[sample_question_with_choices.pk])
        response = client.post(url, {})

        assert response.status_code == 200
        assert "You didn" in response.content.decode()  # Error message


@pytest.mark.django_db
class TestFaviconView:
    """Tests for the favicon redirect."""

    def test_favicon_redirect(self, client):
        """Test that favicon redirects to static file."""
        response = client.get("/favicon.ico")
        assert response.status_code == 301
        assert "static" in response.url


@pytest.mark.django_db
class TestAdminAccess:
    """Tests for admin access."""

    def test_admin_login_page(self, client):
        """Test that admin login page is accessible."""
        response = client.get("/admin/login/")
        assert response.status_code == 200

    def test_admin_requires_login(self, client):
        """Test that admin requires authentication."""
        response = client.get("/admin/")
        assert response.status_code == 302  # Redirects to login

    def test_admin_accessible_when_logged_in(self, authenticated_client):
        """Test that admin is accessible when logged in."""
        response = authenticated_client.get("/admin/")
        assert response.status_code == 200
