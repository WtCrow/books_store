Simple books store at Django framework.

You can see result to this url: https://simple-books-store.herokuapp.com/

If you want start this project local then...

1) git clone https://github.com/WtCrow/books_store.git

2) cd /project/path

3) define next env variables ('export var=val' for linux, 'set var=val' for windows):
SECRET_KEY, DB_ENGINE, DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, EMAIL, EMAIL_PASSWORD

4) python manage.py makemigrations store

5) python manage.py migrate

6) python store/parser.py

7) python manage.py runserver

8) django-admin createsuperuser

9) go to url localhost:8000

10) Profit!
