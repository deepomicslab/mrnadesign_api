conda activate phage
module load GCCcore/11.2.0 GCC/11.2.0 Python/3.9.6

```
pip install django
pip install psycopg2-binary
pip install djangorestframework
pip install django-filter
pip install biopython
pip install slurmpy
pip install django-crontab
```

python manage.py makemigrations

python manage.py migrate

python manage.py showmigrations

python manage.py shell
python manage.py dbshell

TRUNCATE TABLE phages,phage_hosts RESTART IDENTITY;

python manage.py runserver 8324

django-admin startapp appname

pg_dump -U postgres phage > phage_export.sql
psql -U postgres phage < phage_export.sql
DROP DATABASE phage;
create database phage;

/apps/software/Python/3.9.6-GCCcore-11.2.0/bin/python /home/platform/phage_db/phage_api/manage.py crontab run 231c4f91aac3f6ddc1b3ad004b2fa754
python manage.py crontab add
python manage.py crontab run