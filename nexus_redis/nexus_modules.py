import socket
from redis import Redis

from django.utils.datastructures import SortedDict

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

        for group, hosts in self.get_caches().iteritems():
            res = []
            for host in hosts:
                try:
                    stats = host.info()
                except:
                    stats = {'online': 0}
                else:
                    stats['online'] = 1
                res.append((host, stats))
            yield res

        socket.setdefaulttimeout(default_timeout)
    
    def get_title(self):
        return 'Redis'
    
    def get_urls(self):
        from django.conf.urls.defaults import patterns, url

        urlpatterns = patterns('',
            url(r'^$', self.as_view(self.index), name='index'),
        )
        
        return urlpatterns
    
    def render_on_dashboard(self, request):
        cache_stats = list(self.get_stats())
        
        global_stats = {
            'bytes': 0,
            'limit_maxbytes': 0,
            'curr_items': 0,
            'curr_connections': 0,
            'total_connections': 0,
            'total_items': 0,
            'cmd_get': 0,
            'get_hits': 0,
            'get_misses': 0,
            'rusage_system': 0,
            'online': 0,
        }
        for host, stats in cache_stats:
            for k in global_stats.iterkeys():
                global_stats[k] += float(stats.get(k, 0))
        global_stats['total'] = len(cache_stats)

        return self.render_to_string('nexus/redis/dashboard.html', {
            'global_stats': global_stats,
        })
    
    def index(self, request):
        try:
            cache_stats = ((k, SortedDict(sorted(v.iteritems(), key=lambda x: x[0]))) for k, v in self.get_stats())
        except AttributeError:
            cache_stats = []
        
        return self.render_to_response("nexus/redis/index.html", {
            'cache_stats': cache_stats,
        }, request)
nexus.site.register(RedisModule, 'redis', category='cache')