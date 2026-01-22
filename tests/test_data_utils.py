"""
Tests for data utilities and API endpoints.
"""

import json

import pytest
from django.urls import reverse
from django.utils import timezone

from django_webassembly.polls.models import Choice, Question


@pytest.mark.django_db
class TestDataUtilsModule:
    """Tests for the data_utils module."""

    def test_export_polls_data(self, sample_question_with_choices):
        """Test exporting polls data."""
        from django_webassembly import data_utils

        data = data_utils.export_polls_data()

        assert data["version"] == "1.0"
        assert "exported_at" in data
        assert "data" in data
        assert len(data["data"]["questions"]) == 1
        assert len(data["data"]["questions"][0]["choices"]) == 3

    def test_export_polls_json(self, sample_question_with_choices):
        """Test exporting polls data as JSON string."""
        from django_webassembly import data_utils

        json_str = data_utils.export_polls_json()
        data = json.loads(json_str)

        assert data["version"] == "1.0"
        assert len(data["data"]["questions"]) == 1

    def test_import_polls_data(self, db):
        """Test importing polls data."""
        from django_webassembly import data_utils

        import_data = {
            "version": "1.0",
            "data": {
                "questions": [
                    {
                        "question_text": "Imported question?",
                        "pub_date": timezone.now().isoformat(),
                        "choices": [
                            {"choice_text": "Option A", "votes": 5},
                            {"choice_text": "Option B", "votes": 3},
                        ],
                    }
                ]
            },
        }

        result = data_utils.import_polls_data(import_data)

        assert result["questions"] == 1
        assert result["choices"] == 2
        assert Question.objects.filter(question_text="Imported question?").exists()

    def test_import_clears_existing(self, sample_question_with_choices):
        """Test that import with clear_existing removes old data."""
        from django_webassembly import data_utils

        assert Question.objects.count() == 1

        import_data = {
            "version": "1.0",
            "data": {
                "questions": [
                    {
                        "question_text": "New question?",
                        "pub_date": timezone.now().isoformat(),
                        "choices": [],
                    }
                ]
            },
        }

        data_utils.import_polls_data(import_data, clear_existing=True)

        assert Question.objects.count() == 1
        assert Question.objects.first().question_text == "New question?"

    def test_get_database_stats(self, sample_question_with_choices):
        """Test getting database statistics."""
        from django_webassembly import data_utils

        stats = data_utils.get_database_stats()

        assert stats["questions"] == 1
        assert stats["choices"] == 3
        assert stats["total_votes"] == 8  # 0 + 5 + 3

    def test_reset_votes(self, sample_question_with_choices):
        """Test resetting all votes."""
        from django_webassembly import data_utils

        # Verify there are votes to reset
        assert Choice.objects.filter(votes__gt=0).exists()

        count = data_utils.reset_votes()

        assert count == 3
        assert all(c.votes == 0 for c in Choice.objects.all())


@pytest.mark.django_db
class TestDataAPIEndpoints:
    """Tests for the data API endpoints."""

    def test_stats_endpoint(self, client, sample_question_with_choices):
        """Test the stats API endpoint."""
        response = client.get(reverse("api_stats"))

        assert response.status_code == 200
        data = response.json()
        assert data["questions"] == 1
        assert data["choices"] == 3

    def test_export_endpoint(self, client, sample_question_with_choices):
        """Test the export API endpoint."""
        response = client.get(reverse("api_export"))

        assert response.status_code == 200
        assert response["Content-Type"] == "application/json"
        data = response.json()
        assert "version" in data
        assert "data" in data

    def test_import_endpoint(self, client, db):
        """Test the import API endpoint."""
        import_data = {
            "version": "1.0",
            "data": {
                "questions": [
                    {
                        "question_text": "API imported?",
                        "pub_date": timezone.now().isoformat(),
                        "choices": [{"choice_text": "Yes", "votes": 0}],
                    }
                ]
            },
        }

        response = client.post(
            reverse("api_import"),
            data=json.dumps(import_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["imported"]["questions"] == 1

    def test_import_invalid_json(self, client, db):
        """Test import endpoint with invalid JSON."""
        response = client.post(
            reverse("api_import"),
            data="not valid json",
            content_type="application/json",
        )

        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert "Invalid JSON" in data["error"]

    def test_reset_votes_endpoint(self, client, sample_question_with_choices):
        """Test the reset votes API endpoint."""
        response = client.post(reverse("api_reset_votes"))

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["reset_count"] == 3

    def test_tools_page(self, client, sample_question_with_choices):
        """Test the tools page renders."""
        response = client.get(reverse("tools"))

        assert response.status_code == 200
        assert b"Developer Tools" in response.content
        assert b"Database Statistics" in response.content
