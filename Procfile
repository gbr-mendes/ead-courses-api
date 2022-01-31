release: cd app && python3 manage.py migrate
web: sh -c 'cd ./app/ && gunicorn app.wsgi' --preload --log-file –