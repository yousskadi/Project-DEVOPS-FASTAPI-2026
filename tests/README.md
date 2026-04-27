# Test Suite Documentation

## Table of Contents

1. [Overview](#overview)
2. [How to Run](#how-to-run)
3. [Architecture](#architecture)
4. [Fixture Reference](#fixture-reference)
5. [Fixture Scope — Why `function`?](#fixture-scope--why-function)
6. [Test Files](#test-files)
   - [test_root.py](#test_rootpy)
   - [test_users.py](#test_userspy)
   - [test_posts.py](#test_postspy)
   - [test_votes.py](#test_votespy)
7. [Full Test Coverage Table](#full-test-coverage-table)

---

## Overview

This test suite covers every HTTP endpoint of the FastAPI application using
**pytest** and **FastAPI's TestClient**. Tests run against a **dedicated test
database** (`fastapi_db_test`) that is fully isolated from the production
database. Every test starts with a clean database state — no data from one test
can affect another.

**Stack:**
- `pytest` — test runner
- `fastapi.testclient.TestClient` — sends real HTTP requests through the ASGI
  app without a live server
- `SQLAlchemy` — ORM, used to insert test data directly and to reset the DB
  between tests
- `python-jose` — JWT creation inside fixtures (via `app.oauth2`)

---

## How to Run

```bash
# Run the full suite
pytest tests/ -v

# Run a single file
pytest tests/test_posts.py -v

# Run a single test
pytest tests/test_posts.py::test_delete_other_user_post -v

# Show print() output (useful when debugging with print(res.json()))
pytest tests/ -v -s
```

---

## Architecture

### Dedicated test database

The test suite connects to a separate PostgreSQL database whose name is
`<DB_NAME>_test` (e.g., `fastapi_db_test`). `conftest.py` creates it
automatically on the first run if it does not exist.

```
Production → fastapi_db
Tests      → fastapi_db_test   ← never touched by production code
```

### Dependency injection override

FastAPI resolves `get_db` at runtime to open a production session. During tests,
`conftest.py` replaces `get_db` with a function that returns the **test
session** instead. This is the standard FastAPI testing pattern.

```python
app.dependency_overrides[get_db] = override_get_db   # inject test session
yield TestClient(app)
app.dependency_overrides.clear()                      # restore after test
```

### DB reset between tests

The `session` fixture runs `drop_all` + `create_all` before every single test.
This guarantees a completely empty database for every test function, regardless
of what the previous test did.

---

## Fixture Reference

All shared fixtures are defined in `conftest.py`. Local fixtures (used by a
single file) are defined at the top of their file.

### Dependency graph

```
session (DB)
 ├── client (TestClient)
 │    └── authorized_client  ←── token
 │
 ├── test_user (User object)
 │    └── token (JWT string)
 │         └── authorized_client
 │
 └── test_post (Post object)  ←── test_user
      └── test_vote (Votes object)  ←── test_user  [local to test_votes.py]

second_user_token  ←── session          [local to test_posts.py]
authorized_client2 ←── client + second_user_token
```

### `session` — conftest.py

Provides a SQLAlchemy session connected to the test database.

**Before each test:** drops all tables, recreates them empty.  
**After each test:** closes the connection.

```python
@pytest.fixture(scope="function")
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

### `client` — conftest.py

Provides a `TestClient` that uses the test database instead of production.

Overrides FastAPI's `get_db` dependency with a function returning the test
session. Clears all overrides after the test so the next test starts clean.

---

### `test_user` — conftest.py

Creates a `User` row directly in the test DB and returns the ORM object.

```
email    : test@test.com
password : password123  (hashed via bcrypt)
```

Used by both `token` and `test_post` so they share the same user instance
without extra DB queries.

---

### `token` — conftest.py

Generates a valid JWT for `test_user`. Returned as a plain string
(`"eyJ..."`) that `authorized_client` puts into the `Authorization` header.

---

### `authorized_client` — conftest.py

A `TestClient` with `Authorization: Bearer <token>` already set. Use this
fixture for every endpoint that requires authentication.

---

### `test_post` — conftest.py

Creates a `Post` row owned by `test_user`.

```
title   : "Test Post"
content : "Test content"
owner   : test@test.com
```

Shared across `test_posts.py` and `test_votes.py` (that is why it lives in
conftest instead of a local fixture).

---

### `second_user_token` — local to test_posts.py

Creates a second user (`other@test.com`) and returns their JWT. Used to test
that ownership checks (403 Forbidden) actually work — i.e., user B cannot
modify user A's post.

---

### `authorized_client2` — local to test_posts.py

Same as `authorized_client` but authenticated as `other@test.com`. Used
exclusively in 403-Forbidden tests.

---

### `test_vote` — local to test_votes.py

Inserts a `Votes` row for `test_user` on `test_post`. Used by tests that need
a pre-existing vote (duplicate vote, remove vote).

---

## Fixture Scope — Why `function`?

Pytest offers five scopes: `function < class < module < package < session`.

**The hard rule:** a fixture's scope cannot be *wider* than any of its
dependencies. If `session` is `function`, then `client` (which depends on
`session`) cannot be `module`.

### Why `session` (the DB fixture) must be `function`

The fixture calls `drop_all + create_all` to reset the database. If it were
`module`-scoped, all tests in a file would share the same database rows:

- `test_delete_own_post` deletes the post.
- `test_get_post_by_id` (later in the same module) would receive 404 because the
  post is gone — a false failure caused by test ordering, not a real bug.

`function` scope ensures every test gets a clean slate, making the suite
**order-independent** and **fully isolated**.

### Why every other fixture follows

Because `session` is `function`-scoped, the entire dependency chain is forced
to `function`:

| Fixture | Forced because it depends on |
|---|---|
| `test_user` | `session` |
| `token` | `test_user` → `session` |
| `client` | `session` |
| `authorized_client` | `client` + `token` |
| `test_post` | `session` + `test_user` |
| `test_vote` | `session` + `test_user` + `test_post` |

### When would wider scopes be appropriate?

Only if the suite grows large (500+ tests) and the `drop_all/create_all` cycle
becomes a bottleneck. The solution then is the *transaction rollback* pattern:
`session`-scope the DB engine, wrap each test in a transaction, rollback instead
of dropping tables. This is significantly more complex to set up. For ~33 tests
the overhead is negligible.

---

## Test Files

---

### test_root.py

Tests the public health-check endpoint.

| Test | Endpoint | Expected | Description |
|---|---|---|---|
| `test_read_root` | `GET /` | 200 | Returns `{"message": "Hello all the World"}` — verifies the app is up |

---

### test_users.py

Tests the user management endpoints. Both endpoints require a valid JWT.

**Fixtures used:** `authorized_client`, `client`, `session`

| Test | Endpoint | Expected | Description |
|---|---|---|---|
| `test_create_user` | `POST /users/` | 201 | Creates a new user; verifies email in response, verifies password is never returned |
| `test_create_user_duplicate_email` | `POST /users/` | 400 | Sending the same email twice must return 400 Bad Request |
| `test_get_user_by_id` | `GET /users/{id}` | 200 | Inserts a user directly in DB via `session`, then fetches it by id; verifies email matches |
| `test_get_user_not_found` | `GET /users/99999` | 404 | Requesting a non-existent id must return 404 Not Found |
| `test_get_user_unauthorized` | `GET /users/1` | 401 | Accessing a protected endpoint without a JWT must return 401 Unauthorized |

---

### test_posts.py

Tests all five post endpoints. All endpoints require authentication; delete and
update additionally require ownership of the post.

**Fixtures from conftest:** `authorized_client`, `client`, `session`, `test_post`  
**Local fixtures:** `second_user_token`, `authorized_client2`

#### GET /posts/ — list all posts

| Test | Expected | Description |
|---|---|---|
| `test_get_all_posts` | 200 | Returns a list; with `test_post` seeded, length must be 1 |
| `test_get_all_posts_empty` | 200 | No seed data → returns an empty list `[]` |
| `test_get_all_posts_unauthorized` | 401 | No JWT → access denied |

#### GET /posts/{id} — get one post

| Test | Expected | Description |
|---|---|---|
| `test_get_post_by_id` | 200 | Returns `{"Post": {...}, "votes": 0}` matching the seeded post |
| `test_get_post_not_found` | 404 | id 99999 does not exist |
| `test_get_post_by_id_unauthorized` | 401 | No JWT → access denied |

#### POST /posts/ — create a post

| Test | Expected | Description |
|---|---|---|
| `test_create_post` | 201 | All fields provided; verifies title, content, and published in response |
| `test_create_post_default_published` | 201 | `published` field omitted → defaults to `True` |
| `test_create_post_unauthorized` | 401 | No JWT → access denied |
| `test_create_post_missing_title` | 422 | Pydantic validation: `title` is required |
| `test_create_post_missing_content` | 422 | Pydantic validation: `content` is required |

#### DELETE /posts/{id} — delete a post

| Test | Expected | Description |
|---|---|---|
| `test_delete_own_post` | 204 | Owner deletes their own post; 204 No Content (no body) |
| `test_delete_post_not_found` | 404 | Trying to delete a non-existent post |
| `test_delete_post_unauthorized` | 401 | No JWT → access denied |
| `test_delete_other_user_post` | 403 | `authorized_client2` (other@test.com) tries to delete user 1's post → Forbidden |

#### PUT /posts/{id} — update a post

| Test | Expected | Description |
|---|---|---|
| `test_update_own_post` | 200 | Owner updates their post; verifies all three fields changed in response |
| `test_update_post_not_found` | 404 | Trying to update a non-existent post |
| `test_update_post_unauthorized` | 401 | No JWT → access denied |
| `test_update_other_user_post` | 403 | `authorized_client2` tries to update user 1's post → Forbidden |

---

### test_votes.py

Tests the single votes endpoint. One endpoint handles both voting and
un-voting, controlled by the `dir` field.

**Fixtures from conftest:** `authorized_client`, `client`, `test_user`, `test_post`  
**Local fixture:** `test_vote` (a pre-existing vote row in the DB)

**Business logic recap:**

```
POST /votes/  { "post_id": <id>, "dir": 1 }   → upvote
POST /votes/  { "post_id": <id>, "dir": 0 }   → remove vote
```

#### dir=1 : upvote

| Test | Expected | Description |
|---|---|---|
| `test_vote_upvote` | 201 | No previous vote exists → vote created; response `{"message": "successfully added vote"}` |
| `test_vote_upvote_unauthorized` | 401 | No JWT → access denied |
| `test_vote_on_nonexistent_post` | 404 | post_id 99999 does not exist → cannot vote |
| `test_vote_duplicate` | 409 | `test_vote` fixture pre-seeds a vote; sending `dir=1` again → 409 Conflict |

#### dir=0 : remove vote

| Test | Expected | Description |
|---|---|---|
| `test_remove_vote` | 201 | `test_vote` fixture pre-seeds a vote; `dir=0` removes it; response `{"message": "successfully deleted vote"}` |
| `test_remove_vote_nonexistent` | 404 | No vote exists for this post → nothing to remove |
| `test_remove_vote_unauthorized` | 401 | No JWT → access denied |

#### Schema validation

| Test | Expected | Description |
|---|---|---|
| `test_vote_invalid_dir` | 422 | `dir=2` is rejected by Pydantic's `Literal[0, 1]` constraint before the endpoint logic even runs |

---

## Full Test Coverage Table

| File | Tests | Endpoints covered |
|---|---|---|
| test_root.py | 1 | `GET /` |
| test_users.py | 5 | `POST /users/`, `GET /users/{id}` |
| test_posts.py | 19 | `GET /posts/`, `GET /posts/{id}`, `POST /posts/`, `DELETE /posts/{id}`, `PUT /posts/{id}` |
| test_votes.py | 8 | `POST /votes/` |
| **Total** | **33** | **8 endpoints** |

### Scenarios covered per endpoint

| Scenario type | Description |
|---|---|
| Happy path | The request succeeds with the expected data in the response |
| Unauthorized (401) | Request without a JWT token |
| Forbidden (403) | Authenticated user tries to act on another user's resource |
| Not found (404) | Resource id does not exist in the database |
| Conflict (409) | Action violates a uniqueness rule (duplicate vote) |
| Bad request (400) | Semantic error (duplicate email) |
| Validation error (422) | Payload is structurally invalid (missing field, wrong type) |
