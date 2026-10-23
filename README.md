# EduPlatform

A Django REST Framework project for an educational platform.

## Requirements

- Python 3.14
- pip

## Setup

Create and activate a virtual environment:

    python3 -m venv .venv
    source .venv/bin/activate

Install dependencies:

    python -m pip install -r requirements.txt

Apply database migrations:

    python manage.py migrate

Start the development server:

    python manage.py runserver

## Project Features

- Courses and enrollment
- Authentication and permissions
- Payment processing and webhook handling
- Background jobs and scheduled tasks
- Automated testing
