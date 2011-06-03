nexus-redis
-----------

Provides a Redis statistics module in `Nexus <https://github.com/dcramer/nexus>`_.

Install
=======

Install using pip, or easy_install::

	pip install nexus-redis

Config
======

Add nexus_redis to your ``INSTALLED_APPS``::

	INSTALLED_APPS = (
	    'nexus',
	    'nexus_redis',
	)

Usage
=====

The Redis module is automatically integrated into Nexus and provides statistics for all connections specificed in ``NEXUS_REDIS_CONNECTIONS``.

::

    NEXUS_REDIS_CONNECTIONS = getattr(settings, 'NEXUS_REDIS_CONNECTIONS', {
        'group': [
            {'host': '127.0.0.1', 'port': 8930, 'db': 0},
        ],
    })
