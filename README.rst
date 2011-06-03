nexus-redis
-----------

Provides a Redis statistics module in `Nexus <https://github.com/dcramer/nexus>`_.

Install
=======

Install using pip, or easy_install::

	pip install nexus_redis

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