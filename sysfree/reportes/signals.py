from django.db.models.signals import post_save
from django.dispatch import receiver

# Las señales de auditoría están en core.signals

# Aquí se pueden agregar señales para generar reportes automáticamente
# cuando ocurran ciertos eventos en el sistema