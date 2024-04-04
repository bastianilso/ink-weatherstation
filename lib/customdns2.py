import requests
from requests.adapters import HTTPAdapter, Retry
import random

# Create a custom HTTPAdapter
class CustomHTTPAdapter(requests.adapters.HTTPAdapter):
    def resolve(self, hostname):
        ips = [
            '8.8.8.8'  # Google
        ]
        resolutions = {
            'dns.google.com': random.choice(ips),
        }
        return resolutions.get(hostname)

    def send(self, request, **kwargs):
        from urllib.parse import urlparse

        connection_pool_kwargs = self.poolmanager.connection_pool_kw

        result = urlparse(request.url)
        resolved_ip = self.resolve(result.hostname)

        if result.scheme == 'https' and resolved_ip:
            request.url = request.url.replace(
                'https://' + result.hostname,
                'https://' + resolved_ip,
            )
            connection_pool_kwargs['server_hostname'] = result.hostname  # SNI
            connection_pool_kwargs['assert_hostname'] = result.hostname

            # overwrite the host header
            request.headers['Host'] = result.hostname
        else:
            # theses headers from a previous request may have been left
            connection_pool_kwargs.pop('server_hostname', None)
            connection_pool_kwargs.pop('assert_hostname', None)

        return super(CustomHTTPAdapter, self).send(request, **kwargs)

# Create a custom session that uses CustomHTTPAdapter in the mount function
class SessionCustomDNS(requests.Session):
    def mount(self, prefix, adapter=None):
        if prefix.startswith('http://') or prefix.startswith('https://'):
            retries = Retry(total=10, backoff_factor=2, status_forcelist=[502, 503, 504])
            adapter = CustomHTTPAdapter(max_retries=retries)
        return super().mount(prefix, adapter)

