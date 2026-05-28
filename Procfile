web: python manage.py migrate && python manage.py collectstatic --noinput && python manage.py create_admin educfarm@admin.com educfarm@2026 --name "EducFarm" && gunicorn config.wsgi:application
