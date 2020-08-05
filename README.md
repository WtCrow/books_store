#Simple books store on Django framework.

You can see result to this url: https://simple-books-store.herokuapp.com/

If you want start this project local:

1) Enter in terminal: `cd /project/path`
2) Enter in terminal: `pip install -r requirements.txt`
3) Define next env variables:
- SECRET_KEY
- DB_ENGINE
- DB_HOST
- DB_PORT
- DB_NAME
- DB_USER
- DB_PASSWORD
- EMAIL
- EMAIL_PASSWORD
4) Create migration: `python manage.py makemigrations store`
5) Applying migrations: `python manage.py migrate`
6) Parse information for store products: `python store/parser.py` (Parser can be not worked if site changed).
7) Create super user for django admin `django-admin createsuperuser`
8) Start `python manage.py runserver` or start by gunicorn `gunicorn books_store.wsgi --log-file -`
9) go to url localhost:8000
10) Profit!
