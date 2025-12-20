# Heroku Debug Commands for 500 Error

## 1. Check Recent Logs (to see the actual error)
```bash
heroku logs --tail --app your-app-name
```

## 2. Run Database Migrations (CRITICAL)
```bash
heroku run python manage.py migrate --app your-app-name
```

## 3. Collect Static Files
```bash
heroku run python manage.py collectstatic --noinput --app your-app-name
```

## 4. Create Superuser (if needed)
```bash
heroku run python manage.py createsuperuser --app your-app-name
```

## 5. Check Config Vars
```bash
heroku config --app your-app-name
```

## 6. Run Django Shell to Test
```bash
heroku run python manage.py shell --app your-app-name
```

Then in the shell:
```python
from django.contrib.auth.models import User
User.objects.all().count()  # Check if users exist
```

## 7. Restart the App
```bash
heroku restart --app your-app-name
```

