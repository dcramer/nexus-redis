from django.conf import settings

CONNECTIONS = getattr(settings, 'NEXUS_REDIS_CONNECTIONS', [
    # {'host': '127.0.0.1', 'port': 8930},
])

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 6379
