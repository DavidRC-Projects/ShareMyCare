# Fix 500 Error on Heroku Login

## Most Common Causes:

1. **Database migrations not run** (MOST LIKELY)
2. **Missing UserProfile for existing users**
3. **Context processor errors**
4. **Login redirect URL issues**

## Step-by-Step Fix:

### 1. Check Heroku Logs (to see actual error)
```bash
heroku logs --tail --app your-app-name
```

### 2. Run Database Migrations (CRITICAL - Do this first!)
```bash
heroku run python manage.py migrate --app your-app-name
```

### 3. Ensure UserProfile exists for all users
```bash
heroku run python manage.py shell --app your-app-name
```

Then in shell:
```python
from django.contrib.auth.models import User
from accounts.models import UserProfile

# Create profiles for users that don't have one
for user in User.objects.all():
    if not hasattr(user, 'profile'):
        UserProfile.objects.create(user=user)
        print(f"Created profile for {user.username}")
```

### 4. Test login in shell
```python
from django.contrib.auth import authenticate
user = authenticate(username='clinician1', password='ShareMyCare2024!')
print("Authentication successful:", user is not None)
if user:
    print("Has profile:", hasattr(user, 'profile'))
    print("Has clinician_profile:", hasattr(user, 'clinician_profile'))
```

### 5. Restart app
```bash
heroku restart --app your-app-name
```

## Quick Fix Script

Run this one-liner to create missing profiles:
```bash
heroku run python manage.py shell --app your-app-name -c "from django.contrib.auth.models import User; from accounts.models import UserProfile; [UserProfile.objects.get_or_create(user=user) for user in User.objects.all()]"
```

