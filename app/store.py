"""
Why this file exists:
This is our FAKE database — plain Python dictionaries, living
only in memory (they reset every time the server restarts).

We deliberately isolated all "storage" behind this one file.
Every route imports `db` from here and calls things like
`db.users.get(id)`. In Task 3, when we add a REAL database
(PostgreSQL/MongoDB), we only need to rewrite THIS file —
routes.py files won't need to change, because they don't know
or care HOW data is stored, only that `db.users`, `db.projects`,
and `db.tasks` exist and behave like dictionaries.

This pattern is called a "repository" or "data access layer",
and it's standard practice in real backend engineering.
"""

import itertools

# Each dict is keyed by a numeric ID, e.g. {1: {...}, 2: {...}}
users = {}
projects = {}
tasks = {}

# itertools.count() gives us 1, 2, 3, 4... forever — a simple
# way to generate unique, ever-increasing IDs.
_user_id_counter = itertools.count(1)
_project_id_counter = itertools.count(1)
_task_id_counter = itertools.count(1)


def next_user_id():
    return next(_user_id_counter)


def next_project_id():
    return next(_project_id_counter)


def next_task_id():
    return next(_task_id_counter)


def reset():
    """Wipes all data. Useful for automated tests."""
    users.clear()
    projects.clear()
    tasks.clear()
