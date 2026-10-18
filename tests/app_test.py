import json
import os
import pytest
from pathlib import Path

TEST_DB = "test.db"
BASE_DIR = Path(__file__).resolve().parent.parent

# point the app at the test db before it gets imported
os.environ["DATABASE_URL"] = f"sqlite:///{BASE_DIR.joinpath(TEST_DB)}"

from project.app import app, db


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.app_context():
        db.create_all()  # setup
        yield app.test_client()  # tests run here
        db.drop_all()  # teardown


def login(client, username, password):
    """Login helper function"""
    return client.post(
        "/login",
        data=dict(username=username, password=password),
        follow_redirects=True,
    )


def logout(client):
    """Logout helper function"""
    return client.get("/logout", follow_redirects=True)


def test_index(client):
    response = client.get("/", content_type="html/text")
    assert response.status_code == 200


def test_database(client):
    """initial test. ensure that the database exists"""
    tester = Path("test.db").is_file()
    assert tester


def test_empty_db(client):
    """Ensure database is blank"""
    rv = client.get("/")
    assert b"No entries yet. Add some!" in rv.data


def test_login_logout(client):
    """Test login and logout using helper functions"""
    rv = login(client, app.config["USERNAME"], app.config["PASSWORD"])
    assert b"You were logged in" in rv.data
    rv = logout(client)
    assert b"You were logged out" in rv.data
    rv = login(client, app.config["USERNAME"] + "x", app.config["PASSWORD"])
    assert b"Invalid username" in rv.data
    rv = login(client, app.config["USERNAME"], app.config["PASSWORD"] + "x")
    assert b"Invalid password" in rv.data


def test_messages(client):
    """Ensure that user can post messages"""
    login(client, app.config["USERNAME"], app.config["PASSWORD"])
    rv = client.post(
        "/add",
        data=dict(title="<Hello>", text="<strong>HTML</strong> allowed here"),
        follow_redirects=True,
    )
    assert b"No entries here so far" not in rv.data
    assert b"&lt;Hello&gt;" in rv.data
    assert b"<strong>HTML</strong> allowed here" in rv.data


def test_delete_message(client):
    """Ensure the messages are being deleted"""
    rv = client.get("/delete/1")
    data = json.loads(rv.data)
    assert data["status"] == 0
    login(client, app.config["USERNAME"], app.config["PASSWORD"])
    rv = client.get("/delete/1")
    data = json.loads(rv.data)
    assert data["status"] == 1


def test_delete_requires_login(client):
    """Logged out users get a 401 and the post is kept"""
    login(client, app.config["USERNAME"], app.config["PASSWORD"])
    client.post("/add", data=dict(title="Keep me", text="still here"))
    logout(client)
    rv = client.get("/delete/1")
    assert rv.status_code == 401
    assert json.loads(rv.data)["message"] == "Please log in."
    rv = client.get("/")
    assert b"Keep me" in rv.data


def test_delete_removes_post(client):
    """Logged in users can delete a post and it disappears from the index"""
    login(client, app.config["USERNAME"], app.config["PASSWORD"])
    client.post("/add", data=dict(title="Delete me", text="bye"))
    rv = client.get("/delete/1")
    assert rv.status_code == 200
    rv = client.get("/")
    assert b"Delete me" not in rv.data
    assert b"No entries yet. Add some!" in rv.data


def test_add_requires_login(client):
    """Posting without logging in is rejected"""
    rv = client.post("/add", data=dict(title="Nope", text="nope"))
    assert rv.status_code == 401


def test_search_page(client):
    """Search page loads and is linked from the index"""
    rv = client.get("/search/")
    assert rv.status_code == 200
    assert b"Search:" in rv.data
    rv = client.get("/")
    assert b'href="/search/"' in rv.data


def test_search_results(client):
    """Search only returns posts matching the query, ignoring case"""
    login(client, app.config["USERNAME"], app.config["PASSWORD"])
    client.post("/add", data=dict(title="Flask tips", text="use blueprints"))
    client.post("/add", data=dict(title="Groceries", text="eggs and milk"))
    rv = client.get("/search/?query=FLASK")
    assert b"Flask tips" in rv.data
    assert b"Groceries" not in rv.data
    rv = client.get("/search/?query=milk")
    assert b"Groceries" in rv.data
    assert b"Flask tips" not in rv.data


def test_delete_button_only_when_logged_in(client):
    """Delete icon shows next to posts only for logged in users"""
    login(client, app.config["USERNAME"], app.config["PASSWORD"])
    client.post("/add", data=dict(title="Hello", text="world"))
    rv = client.get("/")
    assert b'class="btn-close delete-entry" data-id="1"' in rv.data
    rv = client.get("/search/?query=hello")
    assert b'class="btn-close delete-entry" data-id="1"' in rv.data
    logout(client)
    rv = client.get("/")
    assert b"delete-entry" not in rv.data
