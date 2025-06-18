"""
Comando para verificar productos con stock bajo.
"""
from django.core.management.base import BaseCommand
from inventario.services.stock_notification_service import StockNotificationService

class Command(BaseCommand):
    help = 'Verifica productos con stock bajo y notifica a los administradores'
    
    def handle(self, *args, **options):
        self.stdout.write('Verificando productos con stock bajo...')
        
        # Verificar productos con stock bajo
        StockNotificationService.verificar_productos_stock_bajo()
        
        self.stdout.write(self.style.SUCCESS('Verificación completada'))