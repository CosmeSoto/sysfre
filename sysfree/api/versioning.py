from rest_framework.versioning import URLPathVersioning


class ApiVersioning(URLPathVersioning):
    """
    Clase para manejar el versionado de la API.
    """
    default_version = 'v1'
    allowed_versions = ['v1', 'v2']
    version_param = 'version'