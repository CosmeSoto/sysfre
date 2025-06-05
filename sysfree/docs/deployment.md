# Guía de Despliegue - SysFree

Esta guía describe los pasos necesarios para desplegar el sistema SysFree en un entorno de producción.

## Requisitos

- Python 3.9+
- PostgreSQL 13+
- Node.js 16+
- Nginx
- Supervisor o systemd
- Dominio configurado (opcional)
- Certificado SSL (recomendado)

## 1. Preparación del Servidor

### Actualizar el sistema

```bash
sudo apt update
sudo apt upgrade -y
```

### Instalar dependencias

```bash
sudo apt install -y python3-pip python3-dev libpq-dev postgresql postgresql-contrib nginx curl
```

### Instalar Node.js

```bash
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt install -y nodejs
```

## 2. Configuración de la Base de Datos

### Crear usuario y base de datos

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE sysfree;
CREATE USER sysfreeuser WITH PASSWORD 'password';
ALTER ROLE sysfreeuser SET client_encoding TO 'utf8';
ALTER ROLE sysfreeuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE sysfreeuser SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE sysfree TO sysfreeuser;
\q
```

## 3. Configuración del Proyecto

### Clonar el repositorio

```bash
git clone https://github.com/tuusuario/sysfree.git
cd sysfree
```

### Crear entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

### Instalar dependencias de Python

```bash
pip install -r requirements.txt
pip install gunicorn
```

### Configurar variables de entorno

Crear archivo `.env` en la raíz del proyecto:

```
DEBUG=False
SECRET_KEY=tu_clave_secreta_muy_segura
ALLOWED_HOSTS=tudominio.com,www.tudominio.com,IP_DEL_SERVIDOR
DATABASE_URL=postgres://sysfreeuser:password@localhost:5432/sysfree
STATIC_ROOT=/var/www/sysfree/static/
MEDIA_ROOT=/var/www/sysfree/media/
```

### Aplicar migraciones y recolectar archivos estáticos

```bash
python manage.py migrate
python manage.py collectstatic --no-input
python manage.py createsuperuser
```

## 4. Configuración de Gunicorn

### Crear archivo de servicio systemd

Crear archivo `/etc/systemd/system/sysfree.service`:

```ini
[Unit]
Description=SysFree Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/ruta/al/proyecto/sysfree
ExecStart=/ruta/al/proyecto/sysfree/venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/ruta/al/proyecto/sysfree/sysfree.sock sysfree.wsgi:application
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

### Iniciar y habilitar el servicio

```bash
sudo systemctl start sysfree
sudo systemctl enable sysfree
```

## 5. Configuración de Nginx

### Crear configuración de sitio

Crear archivo `/etc/nginx/sites-available/sysfree`:

```nginx
server {
    listen 80;
    server_name tudominio.com www.tudominio.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /var/www/sysfree;
    }
    
    location /media/ {
        root /var/www/sysfree;
    }
    
    location / {
        include proxy_params;
        proxy_pass http://unix:/ruta/al/proyecto/sysfree/sysfree.sock;
    }
}
```

### Habilitar el sitio

```bash
sudo ln -s /etc/nginx/sites-available/sysfree /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

## 6. Configuración de SSL con Certbot

### Instalar Certbot

```bash
sudo apt install -y certbot python3-certbot-nginx
```

### Obtener certificado SSL

```bash
sudo certbot --nginx -d tudominio.com -d www.tudominio.com
```

## 7. Despliegue del Frontend

### Construir la aplicación frontend

```bash
cd frontend
npm install
npm run build
```

### Configurar Nginx para servir el frontend

Modificar archivo `/etc/nginx/sites-available/sysfree`:

```nginx
server {
    listen 80;
    server_name tudominio.com www.tudominio.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name tudominio.com www.tudominio.com;
    
    ssl_certificate /etc/letsencrypt/live/tudominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tudominio.com/privkey.pem;
    
    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /var/www/sysfree;
    }
    
    location /media/ {
        root /var/www/sysfree;
    }
    
    location /api/ {
        include proxy_params;
        proxy_pass http://unix:/ruta/al/proyecto/sysfree/sysfree.sock;
    }
    
    location /admin/ {
        include proxy_params;
        proxy_pass http://unix:/ruta/al/proyecto/sysfree/sysfree.sock;
    }
    
    location / {
        root /ruta/al/proyecto/sysfree/frontend/build;
        try_files $uri $uri/ /index.html;
    }
}
```

### Reiniciar Nginx

```bash
sudo nginx -t
sudo systemctl restart nginx
```

## 8. Mantenimiento

### Actualizar el sistema

```bash
cd /ruta/al/proyecto/sysfree
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --no-input
sudo systemctl restart sysfree
```

### Monitoreo de logs

```bash
sudo journalctl -u sysfree
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

## 9. Respaldo

### Respaldo de la base de datos

```bash
pg_dump -U sysfreeuser -d sysfree > sysfree_backup_$(date +%Y%m%d).sql
```

### Automatizar respaldos

Crear script `/etc/cron.daily/sysfree-backup`:

```bash
#!/bin/bash
BACKUP_DIR="/ruta/a/respaldos"
FILENAME="sysfree_backup_$(date +%Y%m%d).sql"
pg_dump -U sysfreeuser -d sysfree > $BACKUP_DIR/$FILENAME
gzip $BACKUP_DIR/$FILENAME
find $BACKUP_DIR -name "sysfree_backup_*.sql.gz" -mtime +30 -delete
```

Dar permisos de ejecución:

```bash
sudo chmod +x /etc/cron.daily/sysfree-backup
```