from django.conf import settings

CONNECTIONS = getattr(settings, 'NEXUS_REDIS_CONNECTIONS', {
    # group: [
    #     {'host': '127.0.0.1', 'port': 8930, 'db': 0},
    # ]
})
