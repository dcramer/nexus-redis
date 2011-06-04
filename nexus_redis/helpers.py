from nexus_redis import conf

def get_net_loc(config):
    host = config.get('host', conf.DEFAULT_HOST)
    port = config.get('port', conf.DEFAULT_PORT)
    return '%s:%s' % (host, port)

