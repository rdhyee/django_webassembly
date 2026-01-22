"""
Django WebAssembly Initialization Script

This script runs in the browser via Pyodide to initialize the Django application.
It performs the following steps:
1. Configure Django settings
2. Run database migrations
3. Create a demo superuser
4. Populate sample data
5. Set up the WSGI application for handling requests

Note: This runs entirely in the browser - there is no server involved.
"""

import os
from datetime import datetime

import django

# Configure Django settings before importing any models
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_webassembly.settings")

# Required for database operations in async context (Pyodide runs in async environment)
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

# Initialize Django
django.setup()

# Now we can import Django components
from django.contrib.auth.models import User
from django.contrib.staticfiles.handlers import StaticFilesHandler
from django.core.management.commands.migrate import Command as MigrateCommand
from django.core.wsgi import get_wsgi_application
from django.utils import timezone

from webtest import TestApp

# Run database migrations
print("Running database migrations...")
MigrateCommand().handle(
    database="default",
    skip_checks=False,
    verbosity=1,
    interactive=False,
    app_label=None,
    migration_name=None,
    noinput=True,
    fake=False,
    fake_initial=False,
    plan=False,
    run_syncdb=False,
    check=False,
    prune=False,
    check_unapplied=False,
)

# Create a demo superuser for accessing the admin
# SECURITY NOTE: This is intentional for demonstration purposes.
# In browser-only mode, each user has their own isolated database.
print("Creating demo user...")
DEMO_USERNAME = "demo"
DEMO_PASSWORD = "demo"

if not User.objects.filter(username=DEMO_USERNAME).exists():
    user = User(username=DEMO_USERNAME, is_staff=True, is_superuser=True, email="demo@example.com")
    user.set_password(DEMO_PASSWORD)
    user.save()
    print(f"Created superuser: {DEMO_USERNAME}")

# Populate sample data for the polls app
print("Populating sample data...")
from django_webassembly.polls.models import Choice, Question

if not Question.objects.exists():
    # Create sample questions
    q1 = Question.objects.create(
        question_text="What's your favorite programming language?",
        pub_date=timezone.now(),
    )
    Choice.objects.create(question=q1, choice_text="Python", votes=0)
    Choice.objects.create(question=q1, choice_text="JavaScript", votes=0)
    Choice.objects.create(question=q1, choice_text="Rust", votes=0)
    Choice.objects.create(question=q1, choice_text="Go", votes=0)

    q2 = Question.objects.create(
        question_text="Which web framework do you prefer?",
        pub_date=timezone.now(),
    )
    Choice.objects.create(question=q2, choice_text="Django", votes=0)
    Choice.objects.create(question=q2, choice_text="Flask", votes=0)
    Choice.objects.create(question=q2, choice_text="FastAPI", votes=0)
    Choice.objects.create(question=q2, choice_text="Express.js", votes=0)

    q3 = Question.objects.create(
        question_text="Is running Django in the browser cool?",
        pub_date=timezone.now(),
    )
    Choice.objects.create(question=q3, choice_text="Yes!", votes=0)
    Choice.objects.create(question=q3, choice_text="Absolutely!", votes=0)
    Choice.objects.create(question=q3, choice_text="Mind-blowing!", votes=0)

    print(f"Created {Question.objects.count()} sample questions")

# Set up the WSGI application with static file handling
# We use WebTest's TestApp to provide a WSGI interface that can be called from JavaScript
print("Setting up WSGI application...")
wsgi_application = StaticFilesHandler(get_wsgi_application())
app = TestApp(wsgi_application)

print("Django WebAssembly initialized successfully!")
print(f"  - Django version: {django.VERSION}")
print(f"  - Demo login: {DEMO_USERNAME} / {DEMO_PASSWORD}")
print("  - Visit /admin to access the admin interface")
print("  - Visit /polls to try the example polls app")
