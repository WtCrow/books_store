#Simple books store on Django framework.

You can see result to this url: https://simple-books-store.herokuapp.com/

If you want start this project local:

1) Enter in terminal: `cd /project/path`
2) Enter in terminal: `pip install -r requirements.txt`
3) Create empty database
4) Define next env variables:
- SECRET_KEY
- DB_ENGINE
- DB_HOST
- DB_PORT
- DB_NAME
- DB_USER
- DB_PASSWORD
- EMAIL_HOST
- EMAIL_PORT
- EMAIL
- EMAIL_PASSWORD
5) Create migration: `python manage.py makemigrations store`
6) Applying migrations: `python manage.py migrate`
7) Parse information for store products: `python store/parser.py` (Parser can be not worked if site changed).
8) (Optional) Create super user for django admin `django-admin createsuperuser`
9) Start `python manage.py runserver` or start by gunicorn `gunicorn books_store.wsgi`
10) go to url http://localhost:8000/
11) Profit!
