import socket
from redis import Redis

import nexus

from nexus_redis import conf
from nexus_redis.helpers import get_net_loc

class RedisModule(nexus.NexusModule):
    home_url = 'index'
    name = 'redis'
    
    def get_caches(self):
        caches = {}
        for config in conf.CONNECTIONS:
            netloc = get_net_loc(config)
            if netloc in caches:
                continue
            try:
                caches[netloc] = Redis(
                    host=config.get('host'),
                    port=config.get('port'),
                    password=config.get('password'),
                    db=config.get('db'),
                    )
            except Exception, e:
                self.logger.exception(e)
        return caches
    
    def get_stats(self, timeout=5):
        default_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(timeout)

        results = {}
        for netloc, conn in self.get_caches().iteritems():
            try:
                stats = conn.info()
            except Exception, e:
                stats = {'online': 0}
            else:
                stats['online'] = 1
                stats['db_size'] = conn.dbsize()
            results[netloc] = stats

        socket.setdefaulttimeout(default_timeout)

        return results
    
    def get_title(self):
        return 'Redis'
    
    def get_urls(self):
        from django.conf.urls.defaults import patterns, url

        urlpatterns = patterns('',
            url(r'^$', self.as_view(self.index), name='index'),
            url(r'^by-server/$', self.as_view(self.by_server), name='by-server'),
        )
        
        return urlpatterns
    
    def render_on_dashboard(self, request):
        cache_stats = self.get_stats()
         
        global_stats = {
            'expired_keys': 0,
            'total_commands_processed': 0,
            'used_memory': 0,
            'connected_clients': 0,
            'connected_slaves': 0,
            'online': 0,
            'keyspace_misses': 0,
            'keyspace_hits': 0,
            'total': 0
        }

        for netloc, stats in cache_stats.iteritems():
            for k in global_stats.iterkeys():
                global_stats[k] += float(stats.get(k, 0))
            global_stats['keyspace_commands'] = global_stats['keyspace_hits'] + global_stats['keyspace_misses']
            global_stats['total'] += 1

        return self.render_to_string('nexus/redis/dashboard.html', {
            'global_stats': global_stats,
        })
    
    def index(self, request):
        return self.render_to_response("nexus/redis/index.html", {
            'cache_stats': self.get_stats(),
        }, request)

    def by_server(self, request):
        global_stats = {
            'expired_keys': 0,
            'total_commands_processed': 0,
            'used_memory': 0,
            'connected_clients': 0,
            'connected_slaves': 0,
            'keyspace_misses': 0,
            'keyspace_hits': 0,
            'online': 0,
            'total': 0,
        }
        server_stats = {}
        for netloc, stats in self.get_stats().iteritems():
            hostname = netloc.split(':', 1)[0]
            if hostname not in server_stats:
                server_stats[hostname] = global_stats.copy()
                server_stats[hostname]['servers'] = set()
                server_stats[hostname]['keyspace_commands'] = server_stats[hostname]['keyspace_hits'] + server_stats[hostname]['keyspace_misses']

            host_info = (netloc, stats['online'])
            
            if host_info in server_stats[hostname]['servers']:
                continue
            
            for k in global_stats.iterkeys():
                server_stats[hostname][k] += float(stats.get(k, 0))

            server_stats[hostname]['servers'].add(host_info)

            server_stats[hostname]['total'] = len(server_stats[hostname]['servers'])

        return self.render_to_response("nexus/redis/by_server.html", {
            'cache_stats': server_stats,
        }, request)

nexus.site.register(RedisModule, 'redis', category='cache')