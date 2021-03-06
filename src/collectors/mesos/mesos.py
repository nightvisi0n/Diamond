# coding=utf-8

"""

Collects metrics from a mesos instance. By default,
the collector is set up to query the mesos-master via
port 5050. Set the port to 5051 for mesos-slaves.

#### Example Configuration

```
    host = localhost
    port = 5050
```
"""

import diamond.collector
import json
import urllib2
from urlparse import urlparse


class MesosCollector(diamond.collector.Collector):

    METRICS_PATH = "metrics/snapshot"

    def get_default_config_help(self):
        config_help = super(MesosCollector,
                            self).get_default_config_help()
        config_help.update({
            'host': 'Hostname, using http scheme by default. For https pass '
                    'e.g. "https://localhost"',
            'port': 'Port (default is 5050; please set to 5051 for mesos-slave)'
        })
        return config_help

    def get_default_config(self):
        config = super(MesosCollector, self).get_default_config()
        config.update({
            'host': 'localhost',
            'port': 5050,
            'path': 'mesos'
        })
        return config

    def __init__(self, *args, **kwargs):
        super(MesosCollector, self).__init__(*args, **kwargs)

    def collect(self):
        metrics = self.get_metrics()

        for k, v in metrics.iteritems():
            key = self.clean_up(k)
            self.publish(key, v)

    def _get_url(self):
        parsed = urlparse(self.config['host'])
        scheme = parsed.scheme or 'http'
        host = parsed.hostname or self.config['host']
        return "%s://%s:%s/%s" % (
            scheme, host, self.config['port'], self.METRICS_PATH)

    def get_metrics(self):
        url = self._get_url()

        try:
            return json.load(urllib2.urlopen(url))
        except (urllib2.HTTPError, ValueError), err:
            self.log.error('Unable to read JSON response: %s' % err)
            return {}

    def clean_up(self, text):
        return text.replace('/', '.')
