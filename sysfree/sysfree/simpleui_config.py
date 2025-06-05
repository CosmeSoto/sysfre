# Configuración de SimpleUI para el panel de administración

# Logo del sistema
SIMPLEUI_LOGO = '/img/logo.png'

# Título del sistema
SIMPLEUI_TITLE = 'SysFree - Administración'

# Tema de SimpleUI
SIMPLEUI_DEFAULT_THEME = 'admin.lte.css'

SIMPLEUI_HOME_TITLE = 'Panel de SysFree'
SIMPLEUI_HOME_ICON = 'fas fa-store'  # Icono diferente para la pagina de inicio
SIMPLEUI_HOME_INFO = False  # Ocultar informacion rapida
SIMPLEUI_HOME_QUICK = True  # Mostrar acciones rapidas
SIMPLEUI_HOME_ACTION = True  # Permitir acciones en la pagina de inicio
SIMPLEUI_ANALYSIS = False  # Deshabilitar analisis (mejora la privacidad)

# Configuración del menú
SIMPLEUI_CONFIG = {
    'system_keep': False,
    'menu_display': ['Core', 'Inventario', 'Ventas', 'Clientes', 'Reparaciones', 'Fiscal', 'Reportes', 'Autenticación y Autorización'],
    'dynamic': True,
    'menus': [
        {
            'name': 'Core',
            'icon': 'fas fa-cogs',
            'models': [
                {
                    'name': 'Usuarios',
                    'icon': 'fas fa-users',
                    'url': 'core/usuario/'
                },
                {
                    'name': 'Configuraciones',
                    'icon': 'fas fa-sliders-h',
                    'url': 'ConfiguracionSistema/'
                },
                {
                    'name': 'Empresas',
                    'icon': 'fas fa-building',
                    'url': 'core/empresa/'
                },
                {
                    'name': 'Sucursales',
                    'icon': 'fas fa-store',
                    'url': 'core/sucursal/'
                },
                {
                    'name': 'Logs de Actividad',
                    'icon': 'fas fa-history',
                    'url': 'core/logactividad/'
                }
            ]
        },
        {
            'name': 'Autenticación y Autorización',
            'icon': 'fas fa-shield-alt',
            'models': [
                {
                    'name': 'Grupos',
                    'icon': 'fas fa-users-cog',
                    'url': 'auth/group/'
                },
                {
                    'name': 'Permisos',
                    'icon': 'fas fa-key',
                    'url': 'auth/permission/'
                }
            ]
        }
    ]
}

# Análisis rápido
SIMPLEUI_ANALYSIS = False

# Ocultar botón de ayuda
SIMPLEUI_HELP_URL = False

# Configuración de iconos
SIMPLEUI_ICON = {
    'core.Usuario': 'fas fa-user',
    'core.Configuracion': 'fas fa-cog',
    'core.Empresa': 'fas fa-building',
    'core.Sucursal': 'fas fa-store',
    'core.LogActividad': 'fas fa-history',
}