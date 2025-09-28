# 🔒 Security Guide - Shrimpwatch

## 🛡️ Keamanan Source Code

### 1. File yang Dilindungi
File-file berikut mengandung informasi sensitif dan TIDAK boleh di-commit ke repository publik:

```
# Database credentials
.env
.env.local
.env.production

# Model AI (jika proprietary)
best.pt
*.pth
*.h5

# Log files
*.log
logs/

# Cache dan temporary files
__pycache__/
*.pyc
.streamlit/
```

### 2. Environment Variables
Selalu gunakan environment variables untuk data sensitif:

```python
# ❌ JANGAN lakukan ini
DATABASE_PASSWORD = "password123"

# ✅ LAKUKAN ini
import os
DATABASE_PASSWORD = os.getenv('DB_PASSWORD')
```

### 3. Database Security
- ✅ Gunakan password yang kuat
- ✅ Batasi akses database
- ✅ Gunakan SSL connection
- ✅ Backup database secara berkala

## 🔐 Code Protection

### Opsi 1: Source Code Obfuscation (Advanced)
Jika ingin melindungi source code lebih lanjut:

```python
# install pyobfuscate
pip install pyobfuscate

# obfuscate code
pyobfuscate app.py > app_obfuscated.py
```

### Opsi 2: Compiled Python (Recommended)
Compile Python ke bytecode:

```bash
# Compile to .pyc
python -m compileall .

# Remove .py files (keep .pyc only)
find . -name "*.py" -not -name "__init__.py" -delete
```

### Opsi 3: Docker Container (Best Practice)
Buat Docker image untuk deployment:

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "app.py"]
```

## 🚀 Deployment Security

### 1. Production Environment
```bash
# Set production environment
export FLASK_ENV=production
export DEBUG=False
export SECRET_KEY=your-secret-key-here
```

### 2. HTTPS Configuration
```python
# streamlit_config.toml
[server]
port = 8501
enableCORS = false
enableXsrfProtection = true
```

### 3. Firewall Rules
```bash
# Allow only localhost access
ufw allow from 127.0.0.1 to any port 8501
```

## 🔍 Security Audit

### 1. Dependency Check
```bash
# Check for vulnerable packages
pip install safety
safety check

# Update dependencies
pip install --upgrade -r requirements.txt
```

### 2. Code Analysis
```bash
# Install security linter
pip install bandit

# Run security check
bandit -r .
```

### 3. Database Security
```sql
-- Check database permissions
SELECT * FROM pg_user;

-- Revoke unnecessary permissions
REVOKE ALL ON DATABASE shrimpwatch_db FROM public;
```

## 📋 Security Checklist

### Pre-deployment:
- [ ] Environment variables configured
- [ ] Database credentials secured
- [ ] Model files protected (if proprietary)
- [ ] Dependencies updated
- [ ] Security scan completed
- [ ] HTTPS enabled (production)
- [ ] Firewall configured

### Post-deployment:
- [ ] Monitor logs for suspicious activity
- [ ] Regular security updates
- [ ] Database backups
- [ ] Access logs review
- [ ] Performance monitoring

## 🚨 Incident Response

### Jika terjadi security breach:
1. **Immediate Response**:
   - Stop application
   - Change all passwords
   - Review access logs

2. **Investigation**:
   - Identify attack vector
   - Assess damage
   - Document findings

3. **Recovery**:
   - Patch vulnerabilities
   - Restore from backup
   - Update security measures

## 📞 Security Support

Jika menemukan vulnerability:
1. **DO NOT** create public issue
2. Email security report ke: fianpraniza@gmail.com
3. Include:
   - Description of vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix

## 🔐 Best Practices

### Development:
- ✅ Use version control
- ✅ Regular backups
- ✅ Code reviews
- ✅ Security testing

### Production:
- ✅ Monitor logs
- ✅ Update dependencies
- ✅ Secure configuration
- ✅ Access control

---

**Security First! 🛡️**

*Melindungi source code dan data pengguna adalah prioritas utama*
