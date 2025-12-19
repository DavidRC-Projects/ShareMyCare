# Heroku Deployment Guide for ShareMyCare

This guide will help you deploy ShareMyCare to Heroku.

## Prerequisites

1. A Heroku account (sign up at https://www.heroku.com)
2. Heroku CLI installed (https://devcenter.heroku.com/articles/heroku-cli)
3. Git installed and your project in a Git repository

## Step 1: Install Heroku CLI

If you haven't already, install the Heroku CLI:
```bash
# macOS
brew tap heroku/brew && brew install heroku

# Or download from https://devcenter.heroku.com/articles/heroku-cli
```

## Step 2: Login to Heroku

```bash
heroku login
```

## Step 3: Create a Heroku App

```bash
# Create a new app (replace 'your-app-name' with your desired name)
heroku create your-app-name

# Or let Heroku generate a random name
heroku create
```

## Step 4: Add PostgreSQL Database

```bash
# Add the free PostgreSQL addon
heroku addons:create heroku-postgresql:mini
```

## Step 5: Set Environment Variables

Set all required environment variables on Heroku:

```bash
# Generate a new secret key (run this in Python)
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Set environment variables
heroku config:set SECRET_KEY='your-generated-secret-key-here'
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com
heroku config:set HEROKU_APP_NAME=your-app-name

# Azure Document Intelligence (if you have credentials)
heroku config:set AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT='your-endpoint'
heroku config:set AZURE_DOCUMENT_INTELLIGENCE_KEY='your-key'

# Email Configuration (for production)
heroku config:set EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
heroku config:set EMAIL_HOST=smtp.gmail.com
heroku config:set EMAIL_PORT=587
heroku config:set EMAIL_USE_TLS=True
heroku config:set EMAIL_HOST_USER=your-email@gmail.com
heroku config:set EMAIL_HOST_PASSWORD=your-app-password
heroku config:set DEFAULT_FROM_EMAIL=noreply@sharemycare.com

# Security Settings (recommended for production)
heroku config:set SECURE_SSL_REDIRECT=True
heroku config:set SECURE_HSTS_SECONDS=31536000
heroku config:set SESSION_COOKIE_SECURE=True
heroku config:set CSRF_COOKIE_SECURE=True
heroku config:set RATE_LIMIT_ENABLED=True

# Site ID for django-allauth
heroku config:set SITE_ID=1
```

## Step 6: Deploy to Heroku

```bash
# Make sure all changes are committed
git add .
git commit -m "Prepare for Heroku deployment"

# Deploy to Heroku
git push heroku main

# Or if you're using master branch
git push heroku master
```

## Step 7: Run Migrations

```bash
# Run database migrations
heroku run python manage.py migrate

# Create a superuser (optional)
heroku run python manage.py createsuperuser

# Collect static files
heroku run python manage.py collectstatic --noinput
```

## Step 8: Open Your App

```bash
heroku open
```

## Step 9: Set Up Logging (Optional)

View logs:
```bash
heroku logs --tail
```

## Additional Configuration

### Custom Domain (Optional)

If you have a custom domain:

```bash
heroku domains:add www.yourdomain.com
heroku domains:add yourdomain.com
```

Then update DNS records as instructed by Heroku.

### Media Files Storage

For production, you'll want to use cloud storage (AWS S3, Cloudinary, etc.) for media files. The current setup stores media files locally, which is not persistent on Heroku.

### Scaling (Optional)

```bash
# Scale up web dynos
heroku ps:scale web=1

# View dyno usage
heroku ps
```

## Troubleshooting

### Database Issues

```bash
# Reset database (WARNING: This deletes all data)
heroku pg:reset DATABASE
heroku run python manage.py migrate
```

### Static Files Not Loading

```bash
# Recollect static files
heroku run python manage.py collectstatic --noinput
```

### Check Configuration

```bash
# View all config vars
heroku config

# View a specific config var
heroku config:get SECRET_KEY
```

## Maintenance Commands

```bash
# Run Django shell
heroku run python manage.py shell

# Run management commands
heroku run python manage.py <command>

# Restart the app
heroku restart

# View app info
heroku info
```

## Security Checklist

Before going live, ensure:

- [ ] `DEBUG=False` is set
- [ ] `SECRET_KEY` is set and secure
- [ ] `ALLOWED_HOSTS` includes your domain
- [ ] HTTPS is enforced (`SECURE_SSL_REDIRECT=True`)
- [ ] Secure cookies are enabled
- [ ] Email is configured for production
- [ ] All sensitive data is in environment variables
- [ ] Database backups are configured (Heroku Postgres includes automatic backups)

## Support

For Heroku-specific issues, check:
- [Heroku Dev Center](https://devcenter.heroku.com/)
- [Heroku Support](https://help.heroku.com/)

For Django deployment issues, check:
- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)

