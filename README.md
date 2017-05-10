# A git repository for PyCon Korea 2017

![travis](https://travis-ci.org/pythonkr/pyconkr-2017.svg?branch=master)

## Requiremensts
- Python 3.5

## Getting started

```bash
$ git clone git@github.com:pythonkr/pyconkr-2017.git
$ cd pyconkr-2017
$ pip install -r requirements.txt
$ python manage.py compilemessages
$ python manage.py makemigrations  # flatpages
$ python manage.py migrate
$ python manage.py loaddata ./pyconkr/fixtures/flatpages.json
$ bower install
$ python manage.py runserver
```

