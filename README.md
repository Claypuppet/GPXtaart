# GPXtaart

GPX raspberry pi thingy

## Create database

1. `sudo -u postgres psql`
1. `CREATE DATABASE gpx;`
1. `CREATE USER gpx_admin WITH PASSWORD 'my_password';`
1. `ALTER ROLE gpx_admin SET client_encoding TO 'utf8';`
1. `ALTER ROLE gpx_admin SET timezone TO 'UTC';`
1. `GRANT ALL PRIVILEGES ON DATABASE gpx TO gpx_admin;`

## Configure settings

### Copy local_settings.py.sample to local_settings.py

* `cp GPXtaart/local_settings.py.sample GPXtaart/local_settings.py`

### Edit local_settings.py with database configurations

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'gpx',
        'USER': 'gpx_admin',
        'PASSWORD': 'my_password',
        'HOST': 'localhost',
        'PORT': '',
    }
}
```

### Migrate database

`python manage.py migrate`

