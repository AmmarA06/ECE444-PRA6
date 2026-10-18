# ECE444 PRA6 - Flaskr TDD

Flaskr blog app built with TDD, following https://github.com/shuruizUofT/flaskr-tdd.

Live: https://flaskr-tdd.vercel.app (login: admin / admin)

Deployed on Vercel with a Neon Postgres database (`DATABASE_URL`). Locally it falls back to sqlite.

## Run locally

```sh
python -m venv env
env\Scripts\activate
pip install -r requirements.txt
python create_db.py
FLASK_APP=project/app.py python -m flask run -p 5001
```

## Tests

```sh
python -m pytest
```
