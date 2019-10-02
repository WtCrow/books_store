Simple books store at Django framework.

You can see result to this url: https://simple-books-store.herokuapp.com/

If you want start this project local then...

1) `git clone https://github.com/WtCrow/books_store.git`

2) `cd /project/path`

3) `pip install -r requirements.txt`

4) define next env variables ('`export var=val`' for linux, '`set var=val`' for windows):
SECRET_KEY, DB_ENGINE, DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, EMAIL, EMAIL_PASSWORD

5) Create migration: `python manage.py makemigrations store`

6) Applying migrations: `python manage.py migrate`

7) Parse information for store products: `python store/parser.py`

8) Create super user for django admin `django-admin createsuperuser`

9) Start `python manage.py runserver`

10) go to url localhost:8000

11) Profit!
