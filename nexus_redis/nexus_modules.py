import socket
from redis import Redis

import nexus

from nexus_redis import conf

class RedisModule(nexus.NexusModule):
    home_url = 'index'
    name = 'redis'
    
    def get_caches(self):
        caches = {}
        for group, hosts in conf.CONNECTIONS.iteritems():
            caches[group] = []
            for host in hosts:
                try:
                    caches[group].append((host, Redis(**host)))
                except Exception, e:
                    self.logger.exception(e)
        return caches
    
    def get_stats(self, timeout=5):
        default_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(timeout)

        results = {}
        for group, hosts in self.get_caches().iteritems():
            results[group] = []
            for host, conn in hosts:
                try:
                    stats = conn.info()
                except Exception, e:
                    stats = {'online': 0}
                else:
                    stats['online'] = 1
                results[group].append((host, stats))

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
            'total': 0
        }

        for group in cache_stats.itervalues():
            for host, stats in group:
                for k in global_stats.iterkeys():
                    global_stats[k] += float(stats.get(k, 0))
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
            'online': 0,
            'total': 0,
        }
        server_stats = {}
        for group in self.get_stats().itervalues():
            for host, stats in group:
                hostname = host['host']
                if hostname not in server_stats:
                    server_stats[hostname] = global_stats.copy()
                
                for k in global_stats.iterkeys():
                    server_stats[hostname][k] += float(stats.get(k, 0))
                server_stats[hostname]['total'] += 1
                server_stats[hostname].setdefault('servers', []).append((host, stats))

        return self.render_to_response("nexus/redis/by_server.html", {
            'cache_stats': server_stats,
        }, request)

nexus.site.register(RedisModule, 'redis', category='cache')