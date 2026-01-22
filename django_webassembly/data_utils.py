"""
Data utilities for Django WebAssembly.

Provides functions for exporting and importing data, useful for:
- Backing up user data
- Sharing poll data between instances
- Restoring data after cache clear
"""

import json
from datetime import datetime
from typing import Any

from django.contrib.auth.models import User
from django.core import serializers
from django.utils import timezone

from django_webassembly.polls.models import Choice, Question


def export_polls_data() -> dict[str, Any]:
    """
    Export all polls data as a JSON-serializable dictionary.

    Returns:
        dict containing questions and choices with metadata
    """
    questions = []
    for question in Question.objects.all():
        q_data = {
            "id": question.pk,
            "question_text": question.question_text,
            "pub_date": question.pub_date.isoformat(),
            "choices": [],
        }
        for choice in question.choice_set.all():
            q_data["choices"].append({
                "id": choice.pk,
                "choice_text": choice.choice_text,
                "votes": choice.votes,
            })
        questions.append(q_data)

    return {
        "version": "1.0",
        "exported_at": timezone.now().isoformat(),
        "app": "django_webassembly.polls",
        "data": {
            "questions": questions,
        },
    }


def export_polls_json() -> str:
    """
    Export all polls data as a JSON string.

    Returns:
        JSON string of polls data
    """
    return json.dumps(export_polls_data(), indent=2)


def import_polls_data(data: dict[str, Any], clear_existing: bool = False) -> dict[str, int]:
    """
    Import polls data from a dictionary.

    Args:
        data: Dictionary containing exported polls data
        clear_existing: If True, delete all existing polls before import

    Returns:
        dict with counts of imported items
    """
    if clear_existing:
        Question.objects.all().delete()

    imported = {"questions": 0, "choices": 0}

    questions_data = data.get("data", {}).get("questions", [])
    for q_data in questions_data:
        # Parse the date
        pub_date = datetime.fromisoformat(q_data["pub_date"])
        if timezone.is_naive(pub_date):
            pub_date = timezone.make_aware(pub_date)

        question = Question.objects.create(
            question_text=q_data["question_text"],
            pub_date=pub_date,
        )
        imported["questions"] += 1

        for c_data in q_data.get("choices", []):
            Choice.objects.create(
                question=question,
                choice_text=c_data["choice_text"],
                votes=c_data.get("votes", 0),
            )
            imported["choices"] += 1

    return imported


def import_polls_json(json_string: str, clear_existing: bool = False) -> dict[str, int]:
    """
    Import polls data from a JSON string.

    Args:
        json_string: JSON string containing exported polls data
        clear_existing: If True, delete all existing polls before import

    Returns:
        dict with counts of imported items
    """
    data = json.loads(json_string)
    return import_polls_data(data, clear_existing)


def get_database_stats() -> dict[str, Any]:
    """
    Get statistics about the current database.

    Returns:
        dict with database statistics
    """
    total_votes = sum(c.votes for c in Choice.objects.all())

    return {
        "users": User.objects.count(),
        "questions": Question.objects.count(),
        "choices": Choice.objects.count(),
        "total_votes": total_votes,
    }


def reset_votes() -> int:
    """
    Reset all vote counts to zero.

    Returns:
        Number of choices reset
    """
    count = Choice.objects.update(votes=0)
    return count


# Functions exposed for use from JavaScript via Pyodide
__all__ = [
    "export_polls_data",
    "export_polls_json",
    "import_polls_data",
    "import_polls_json",
    "get_database_stats",
    "reset_votes",
]
