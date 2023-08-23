# CRM DRF API
---
> Django Drf API for CRM

## Тестирование
---
### Mypy
```bash
mypy {django_project}
```
   
### Test coverage
```bash
coverage run -m pytest
coverage html
start htmlcov/index.html
```

### Pytest
```bash
pytest
pytest -s
pytest {django_project}/{some_path}
```

## Celery
---
- Возможно тестирование вне докера / Проверка работы с докером

## Weasyprint
---
- Для локальной разработки на Windows - использовать версию 52.5, она работает медленнее.
- Докер использует версию 59.0, c установленными библиотеками под linux

## Email Server
---
- Для локальной разработки в докер доступен mailhog, вне докера django-email-backend
- Mailhog работает на порту:  http://localhost:8025/

## Docker
---
### Полезные команды
```bash
# containers status
docker-compose -f production.yml ps

# containers logs
docker-compose -f production.yml logs

# remove unused(dangling) images
docker image prune

# django shell run
docker-compose -f production.yml run --rm django python manage.py shell

# django dump db data
docker-compose -f production.yml run --rm django bash

python -Xutf8 manage.py dumpdata {app}.{Model -o data.json
  # Открыть вторую консоль, сохраняя сессию в старой
  docker cp 5f5cecd3798e:/app/data.json ./data.json

# If you want to scale application
# ❗ Don’t try to scale postgres, celerybeat, or traefik
docker-compose -f production.yml up --scale django=4
docker-compose -f production.yml up --scale celeryworker=2
```
