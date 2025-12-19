# Security Features and Configuration

## Overview
This document outlines the security features implemented in ShareMyCare and how to configure them for production.

## Security Features Implemented

### 1. HTTPS and SSL Security
- **SECURE_SSL_REDIRECT**: Redirects all HTTP traffic to HTTPS
- **SECURE_PROXY_SSL_HEADER**: For use behind reverse proxies (nginx, Apache)
- **HSTS (HTTP Strict Transport Security)**: Prevents protocol downgrade attacks
- **Secure Cookies**: Cookies only sent over HTTPS

### 2. Session Security
- **SESSION_COOKIE_SECURE**: Cookies only sent over HTTPS
- **SESSION_COOKIE_HTTPONLY**: Prevents JavaScript access (XSS protection)
- **SESSION_COOKIE_SAMESITE**: CSRF protection
- **SESSION_EXPIRE_AT_BROWSER_CLOSE**: Sessions expire when browser closes
- **SESSION_SAVE_EVERY_REQUEST**: Resets session expiry on each request

### 3. CSRF Protection
- **CSRF_COOKIE_SECURE**: CSRF cookies only sent over HTTPS
- **CSRF_COOKIE_HTTPONLY**: Prevents JavaScript access
- **CSRF_COOKIE_SAMESITE**: Additional CSRF protection
- Django's CSRF middleware enabled by default

### 4. File Upload Security
- **File Size Limits**: Maximum 50MB per file
- **File Type Validation**: Only allowed image types (jpg, jpeg, png, gif, pdf)
- **MIME Type Validation**: Validates content type
- **Upload Path Sanitization**: Files stored in organized directories

### 5. Password Security
- **Minimum Length**: 8 characters
- **Password Validators**: 
  - User attribute similarity check
  - Common password check
  - Numeric-only password prevention

### 6. Rate Limiting
- **Login Attempts**: 5 attempts per 5 minutes
- **Email Sending**: 10 emails per hour
- Configurable via environment variables

### 7. Security Headers
- **Content Security Policy (CSP)**: Prevents XSS attacks
- **X-Frame-Options**: Prevents clickjacking (DENY)
- **X-Content-Type-Options**: Prevents MIME type sniffing
- **Referrer-Policy**: Controls referrer information
- **Permissions-Policy**: Restricts browser features

### 8. Security Logging
- **Security Events**: Logged to `logs/security.log`
- **Failed Login Attempts**: Logged with IP address
- **Rate Limit Violations**: Logged with details
- **Admin Email Alerts**: Errors sent to admins in production

### 9. Input Validation
- **Email Validation**: All email inputs validated
- **File Upload Validation**: Size, type, and content validation
- **Form Validation**: Django forms with server-side validation

### 10. Authentication & Authorization
- **Login Required**: Protected views require authentication
- **Role-Based Access**: Clinicians vs. patients have different access
- **Data Ownership**: Users can only access their own data

## Production Configuration

### Environment Variables

Create a `.env` file with the following settings:

```bash
# Django Core Settings
SECRET_KEY=your-secret-key-here-generate-with-django-admin-generate-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Security Settings
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Rate Limiting
RATE_LIMIT_ENABLED=True

# Admin URL (change from default)
ADMIN_URL=admin-secure-url-change-this/

# Email Settings
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

### Generate Secret Key

```bash
python manage.py shell
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### Additional Production Recommendations

1. **Use a Production Database**: Replace SQLite with PostgreSQL or MySQL
2. **Use Redis for Caching**: For rate limiting and session storage
3. **Set up Monitoring**: Use tools like Sentry for error tracking
4. **Regular Backups**: Automated database backups
5. **Keep Dependencies Updated**: Regularly update Django and packages
6. **Use a WAF**: Web Application Firewall (Cloudflare, AWS WAF)
7. **Enable 2FA**: Consider adding two-factor authentication
8. **Regular Security Audits**: Conduct penetration testing

## Security Checklist

- [x] HTTPS enabled
- [x] Secure cookies configured
- [x] CSRF protection enabled
- [x] XSS protection (CSP headers)
- [x] Clickjacking protection
- [x] File upload validation
- [x] Password strength requirements
- [x] Rate limiting
- [x] Security logging
- [x] Input validation
- [x] Authentication required for protected views
- [x] Authorization checks (users can only access their data)
- [ ] Two-factor authentication (recommended)
- [ ] Regular security audits (recommended)
- [ ] Penetration testing (recommended)

## Monitoring

Security events are logged to:
- `logs/security.log` - Security-related events
- `logs/django.log` - General application logs

Monitor these logs regularly for:
- Failed login attempts
- Rate limit violations
- Unusual access patterns
- File upload errors
- Authentication failures

## Reporting Security Issues

If you discover a security vulnerability, please report it responsibly:
1. Do not create a public issue
2. Contact the maintainers privately
3. Provide detailed information about the vulnerability
4. Allow time for the issue to be fixed before public disclosure

