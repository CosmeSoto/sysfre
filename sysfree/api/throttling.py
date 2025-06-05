from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class BurstRateUserThrottle(UserRateThrottle):
    """
    Limitador de tasa para ráfagas de peticiones de usuarios autenticados.
    Limita a 60 peticiones por minuto.
    """
    scope = 'burst_user'
    rate = '60/min'


class SustainedRateUserThrottle(UserRateThrottle):
    """
    Limitador de tasa sostenida para usuarios autenticados.
    Limita a 1000 peticiones por día.
    """
    scope = 'sustained_user'
    rate = '1000/day'


class BurstRateAnonThrottle(AnonRateThrottle):
    """
    Limitador de tasa para ráfagas de peticiones de usuarios anónimos.
    Limita a 20 peticiones por minuto.
    """
    scope = 'burst_anon'
    rate = '20/min'


class SustainedRateAnonThrottle(AnonRateThrottle):
    """
    Limitador de tasa sostenida para usuarios anónimos.
    Limita a 100 peticiones por día.
    """
    scope = 'sustained_anon'
    rate = '100/day'