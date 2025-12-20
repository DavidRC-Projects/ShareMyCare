# Heroku Deployment Checklist

## ✅ Pre-Deployment Checks

### 1. Configuration Files
- [x] **Procfile** - ✅ Present and correct (`web: gunicorn sharemycare.wsgi --log-file -`)
- [x] **requirements.txt** - ✅ All dependencies listed
- [x] **runtime.txt** - ⚠️ Python 3.13.0 (check Heroku support - may need 3.12.x)
- [x] **.gitignore** - ✅ Media and staticfiles excluded

### 2. Settings Configuration
- [x] **DEBUG** - ✅ Set to `False` by default (can override with env var)
- [x] **ALLOWED_HOSTS** - ✅ Configured for Heroku (auto-detects DYNO)
- [x] **SECRET_KEY** - ⚠️ Uses env var (must set on Heroku)
- [x] **Database** - ✅ Uses `dj_database_url` (auto-configures with Heroku Postgres)
- [x] **Static Files** - ✅ WhiteNoise configured
- [x] **Media Files** - ⚠️ Local storage (will be lost on dyno restart - OK for testing)

### 3. Dependencies
- [x] **gunicorn** - ✅ In requirements.txt
- [x] **whitenoise** - ✅ In requirements.txt
- [x] **psycopg2-binary** - ✅ In requirements.txt
- [x] **dj-database-url** - ✅ In requirements.txt
- [x] **python-dotenv** - ✅ In requirements.txt

## 📋 Required Heroku Config Vars

Set these before deploying:

```bash
# Critical - MUST SET
heroku config:set SECRET_KEY='<generate-new-secret-key>'
heroku config:set DEBUG=False
heroku config:set HEROKU_APP_NAME='your-app-name'

# Optional but Recommended
heroku config:set ALLOWED_HOSTS='your-app-name.herokuapp.com'
heroku config:set SITE_ID=1

# Security (Recommended for Production)
heroku config:set SECURE_SSL_REDIRECT=True
heroku config:set SECURE_HSTS_SECONDS=31536000
heroku config:set SESSION_COOKIE_SECURE=True
heroku config:set CSRF_COOKIE_SECURE=True

# Azure Document Intelligence (if using)
heroku config:set AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT='your-endpoint'
heroku config:set AZURE_DOCUMENT_INTELLIGENCE_KEY='your-key'

# Email (if needed)
heroku config:set EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
heroku config:set EMAIL_HOST=smtp.gmail.com
heroku config:set EMAIL_PORT=587
heroku config:set EMAIL_USE_TLS=True
heroku config:set EMAIL_HOST_USER=your-email@gmail.com
heroku config:set EMAIL_HOST_PASSWORD=your-app-password
```

## 🚀 Deployment Steps

1. **Generate Secret Key:**
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

2. **Create Heroku App:**
   ```bash
   heroku create your-app-name
   ```

3. **Add PostgreSQL:**
   ```bash
   heroku addons:create heroku-postgresql:mini
   ```

4. **Set Config Vars** (see above)

5. **Deploy:**
   ```bash
   git push heroku main
   ```

6. **Run Migrations:**
   ```bash
   heroku run python manage.py migrate
   ```

7. **Create Superuser:**
   ```bash
   heroku run python manage.py createsuperuser
   ```

8. **Collect Static Files:**
   ```bash
   heroku run python manage.py collectstatic --noinput
   ```

9. **Open App:**
   ```bash
   heroku open
   ```

## ⚠️ Known Issues & Notes

1. **Python Version:** runtime.txt specifies 3.13.0, but Heroku may not support it yet. If deployment fails, change to `python-3.12.7` or `python-3.11.9`

2. **Media Files:** Currently using local storage. Files will be lost on dyno restart. This is OK for testing, but you'll need cloud storage (AWS S3/Cloudinary) for production.

3. **Security Warnings:** The deployment check will show security warnings. These are expected and should be configured via Heroku config vars (see above).

4. **Static Files:** WhiteNoise is configured and will serve static files automatically. No additional configuration needed.

## 🔍 Post-Deployment Verification

1. Check logs: `heroku logs --tail`
2. Verify static files load correctly
3. Test user registration/login
4. Test file uploads (remember: files won't persist)
5. Check database connection
6. Verify HTTPS redirect (if configured)

## 📝 Quick Commands Reference

```bash
# View logs
heroku logs --tail

# Run Django shell
heroku run python manage.py shell

# Run management command
heroku run python manage.py <command>

# Restart app
heroku restart

# View config vars
heroku config

# Scale dynos
heroku ps:scale web=1
```

