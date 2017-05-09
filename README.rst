A git repository for PyCon Korea 2017

.. image:: https://travis-ci.org/pythonkr/pyconkr-2017.svg?branch=master
    :target: https://travis-ci.org/pythonkr/pyconkr-2017

Requiremensts
-------------
- Python 3.5

## Getting started

```
$ git clone git@github.com:pythonkr/pyconapac-2016.git
$ cd pyconapac-2016
$ pip install -r requirements.txt
$ python manage.py compilemessages
$ python manage.py makemigrations  # flatpages
$ python manage.py migrate
$ python manage.py loaddata ./pyconkr/fixtures/flatpages.json
$ bower install
$ python manage.py runserver
```