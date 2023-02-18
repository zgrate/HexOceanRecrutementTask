export DJANGO_SUPERUSER_EMAIL=test@test.com
export DJANGO_SUPERUSER_PASSWORD=admin
export DJANGO_SUPERUSER_USERNAME=admin
python manage.py createsuperuser --noinput
python manage.py loaddata ./tiers/seed/0001_Initial_Seed.json
