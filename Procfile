web:gunicorn greatkart.wsgi --log-file - 
web: pyhton manage.py migrate && gunicorn greatkart.wsgi

web: gunicorn greatkart.wsgi:application --bind 0.0.0.0:$PORT
