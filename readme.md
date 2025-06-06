# Instalar Python

python --version
sudo pacman -S python

# Instalar PIP

pip --version
sudo pacman -S python-pip

# borrar la carpeta de virtualenv

rm -rf env/

# Crear virtualenv

python3 -m venv env

# Activar virtual

source env/bin/activate

# abrir el proyecto con vs

code .

# Instalar requerimientos

pip install -r requirements.txt

# Instalar requerimientos de desarrollo

pip freeze > requirements.txt

# instalar ~ nvm -v 0.39.7 ~ node -v v20.19.2 ~ npm -v 10.8.2

cd /home/djcos/Descargas/freecom/sysfree/theme/static_src
npm install

cd /home/djcos/Descargas/freecom/sysfree
python manage.py tailwind build

python manage.py tailwind start

python manage.py collectstatic

chmod +x setup.sh
./setup.sh

# Generar y aplicar migraciones

python manage.py check
python manage.py makemigrations
python manage.py migrate

python manage.py showmigrations

# Crear superusuario (si es necesario)

python manage.py createsuperuser

# Iniciar servidor local

python manage.py runserver

# Borrar migraciones

find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

find . -name "__pycache__" -type d -exec rm -rf {} +

python manage.py clear_cache

rm -rf staticfiles/*
rm -rf media/*
python manage.py collectstatic --noinput

# Elimina todos los datos (cuidado, esto borra todo)

python manage.py showmigrations
python manage.py flush

# Borrar migraciones de una aplicacion

rm -rf core/migrations/

# Crear base de datos con postgresql

psql -U postgres -c "DROP DATABASE sysfree;"
psql -U postgres -c "CREATE DATABASE sysfree;"

python manage.py migrate --fake

# Crear migraciones de una aplicacion

python manage.py makemigrations --all
python manage.py makemigrations core
python manage.py migrate

# poblar datos:

python manage.py poblar_datos

# testear aplicacion

python manage.py test core

# shell de django

python manage.py shell

# Backup básico:

python backup_media.py

# Mantener solo 3 backups:

bashpython backup_media.py --max-backups 3

# Máxi# ma compresión:

python backup_media.py --compress-level 9

# Directorio personalizado:

python backup_media.py --backup-dir /ruta/a/mis/backups

# Generar traducciones:

python manage.py makemessages -l es

# Compilar traducciones:

python manage.py compilemessages

# Crea un directorio de mensajes para traducciones:

mkdir -p inventario/locale/es/LC_MESSAGES

# Crea un archivo de mensajes para cada idioma:

python manage.py makemessages -l es -d django -i "venv/\*" --locale-path inventario/locale

# Revisa los errores:

python manage.py check

# Test 

coverage run manage.py test
coverage report

coverage run manage.py test inventario
coverage run manage.py test clientes
coverage run manage.py test ventas
coverage run manage.py test reparaciones
coverage run manage.py test fiscal
coverage run manage.py test ecommerce
coverage run manage.py test reportes

