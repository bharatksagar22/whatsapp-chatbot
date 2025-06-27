# WhatsApp Chatbot Deployment Guide

## 🚀 Production Deployment

### Prerequisites
- Ubuntu/CentOS server with root access
- Domain name with SSL certificate
- WhatsApp Business API account
- PostgreSQL database (recommended)

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3.11 python3.11-venv python3-pip nodejs npm nginx postgresql postgresql-contrib

# Install PM2 for process management
sudo npm install -g pm2

# Create application user
sudo useradd -m -s /bin/bash whatsapp
sudo usermod -aG sudo whatsapp
```

### 2. Database Setup

```bash
# Setup PostgreSQL
sudo -u postgres createuser --interactive whatsapp
sudo -u postgres createdb whatsapp_chatbot -O whatsapp

# Set password for database user
sudo -u postgres psql
ALTER USER whatsapp PASSWORD 'your_secure_password';
\q
```

### 3. Application Deployment

```bash
# Switch to application user
sudo su - whatsapp

# Clone or upload your application
mkdir -p /home/whatsapp/apps
cd /home/whatsapp/apps

# Upload your application files here
# whatsapp-backend/
# whatsapp-chatbot-dashboard/

# Setup backend
cd whatsapp-backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

# Setup frontend
cd ../whatsapp-chatbot-dashboard
npm install
npm run build
```

### 4. Environment Configuration

```bash
# Create environment file
cat > /home/whatsapp/apps/whatsapp-backend/.env << EOF
FLASK_ENV=production
DATABASE_URL=postgresql://whatsapp:your_secure_password@localhost/whatsapp_chatbot
WHATSAPP_API_TOKEN=your_whatsapp_api_token
WHATSAPP_WEBHOOK_SECRET=your_webhook_secret
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
SECRET_KEY=your_flask_secret_key
EOF
```

### 5. Process Management with PM2

```bash
# Create PM2 ecosystem file
cat > /home/whatsapp/apps/ecosystem.config.js << EOF
module.exports = {
  apps: [
    {
      name: 'whatsapp-backend',
      cwd: '/home/whatsapp/apps/whatsapp-backend',
      script: 'venv/bin/gunicorn',
      args: '-w 4 -b 127.0.0.1:5000 src.main:app',
      env: {
        FLASK_ENV: 'production'
      },
      error_file: '/home/whatsapp/logs/backend-error.log',
      out_file: '/home/whatsapp/logs/backend-out.log',
      log_file: '/home/whatsapp/logs/backend.log',
      time: true
    }
  ]
};
EOF

# Create logs directory
mkdir -p /home/whatsapp/logs

# Start application with PM2
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

### 6. Nginx Configuration

```bash
# Create Nginx configuration
sudo tee /etc/nginx/sites-available/whatsapp-chatbot << EOF
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;

    # Frontend
    location / {
        root /home/whatsapp/apps/whatsapp-chatbot-dashboard/dist;
        try_files \$uri \$uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # WebSocket support (if needed)
    location /socket.io/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/whatsapp-chatbot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 7. SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 8. WhatsApp Business API Setup

```bash
# Configure webhook URL
curl -X POST "https://graph.facebook.com/v17.0/YOUR_PHONE_NUMBER_ID/webhooks" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "messaging_product": "whatsapp",
    "entry": [{
      "id": "YOUR_PHONE_NUMBER_ID",
      "changes": [{
        "value": {
          "messaging_product": "whatsapp",
          "metadata": {
            "display_phone_number": "YOUR_DISPLAY_PHONE_NUMBER",
            "phone_number_id": "YOUR_PHONE_NUMBER_ID"
          },
          "contacts": [],
          "messages": []
        },
        "field": "messages"
      }]
    }]
  }'
```

### 9. Database Migration

```bash
# Initialize database
cd /home/whatsapp/apps/whatsapp-backend
source venv/bin/activate
python -c "
from src.models.user import db
from src.main import app
with app.app_context():
    db.create_all()
    print('Database initialized successfully')
"
```

### 10. Monitoring Setup

```bash
# Install monitoring tools
sudo apt install -y htop iotop nethogs

# Setup log rotation
sudo tee /etc/logrotate.d/whatsapp-chatbot << EOF
/home/whatsapp/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
}
EOF
```

## 🔧 Configuration Files

### Backend Configuration (`src/config.py`)
```python
import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///whatsapp.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # WhatsApp API Configuration
    WHATSAPP_API_TOKEN = os.environ.get('WHATSAPP_API_TOKEN')
    WHATSAPP_WEBHOOK_SECRET = os.environ.get('WHATSAPP_WEBHOOK_SECRET')
    WHATSAPP_PHONE_NUMBER_ID = os.environ.get('WHATSAPP_PHONE_NUMBER_ID')
    
    # AI Configuration
    AI_RESPONSE_DELAY = 2  # seconds
    MAX_RETRY_ATTEMPTS = 3
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = 'redis://localhost:6379'
```

### Frontend Configuration (`src/config.js`)
```javascript
const config = {
  API_BASE_URL: process.env.NODE_ENV === 'production' 
    ? 'https://your-domain.com/api' 
    : 'http://localhost:5000/api',
  
  WEBSOCKET_URL: process.env.NODE_ENV === 'production'
    ? 'wss://your-domain.com'
    : 'ws://localhost:5000',
    
  REFRESH_INTERVAL: 30000, // 30 seconds
  MAX_MESSAGE_LENGTH: 4096
};

export default config;
```

## 🔒 Security Checklist

- [ ] SSL certificate installed and configured
- [ ] Database credentials secured
- [ ] API tokens stored in environment variables
- [ ] Firewall configured (only ports 80, 443, 22 open)
- [ ] Regular security updates scheduled
- [ ] Backup strategy implemented
- [ ] Log monitoring configured
- [ ] Rate limiting enabled
- [ ] Input validation implemented
- [ ] CORS properly configured

## 📊 Monitoring & Maintenance

### Health Check Endpoints
- Backend: `https://your-domain.com/api/health`
- Database: Monitor connection pool
- WhatsApp API: Check webhook status
- AI Agents: Monitor performance metrics

### Backup Strategy
```bash
# Database backup script
#!/bin/bash
BACKUP_DIR="/home/whatsapp/backups"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump whatsapp_chatbot > "$BACKUP_DIR/db_backup_$DATE.sql"
find "$BACKUP_DIR" -name "db_backup_*.sql" -mtime +7 -delete
```

### Log Monitoring
```bash
# Monitor application logs
tail -f /home/whatsapp/logs/backend.log

# Monitor system resources
htop
iotop
df -h
```

## 🚨 Troubleshooting

### Common Issues
1. **502 Bad Gateway**: Check if backend is running (`pm2 status`)
2. **Database Connection Error**: Verify PostgreSQL service and credentials
3. **WhatsApp Webhook Fails**: Check webhook URL and SSL certificate
4. **High Memory Usage**: Monitor AI agents and restart if needed
5. **Slow Response**: Check database queries and add indexes

### Emergency Procedures
```bash
# Restart all services
pm2 restart all
sudo systemctl restart nginx
sudo systemctl restart postgresql

# Check service status
pm2 status
sudo systemctl status nginx
sudo systemctl status postgresql

# View recent logs
pm2 logs --lines 100
sudo tail -f /var/log/nginx/error.log
```

## 📞 Support

For deployment issues:
1. Check logs first
2. Verify configuration files
3. Test individual components
4. Contact technical support with error details

---

**Deployment completed successfully! Your WhatsApp Chatbot is now live and ready to handle conversations.**

