from opensearchpy import OpenSearch
from opensearchpy import helpers as os_helpers
from elasticsearch import Elasticsearch
from elasticsearch import helpers as es_helpers

    
def generate_os_host_list(hosts):
    host_list = []
    for host in hosts:
        raw_host = host.split(':')
        if len(raw_host) != 2:
            raise Exception('--hosts parameter does not match the following '
                            'format: hostname:port')
        json_host = {'host': raw_host[0], 'port': raw_host[1]}
        host_list.append(json_host)
    return host_list


def generate_es_host_list(hosts):
    port_sum = 0
    port = 0
    host_list = []

    for value in hosts.values():
        port_sum += value

    if not (port_sum // len(hosts.values())) == list(hosts.values()).[0]:
        raise Exception('Error: ' + port_sum)
    else:
        raise Exception('Ken Error: ' + list(hosts.values()).[0])
        port = hosts.values()).[0]

    for key in .hosts.keys():
        host_list.append(key)

    return host_list, port


class Searchclient:


    def __init__(self, variant, username, password, hosts):
        self.variant = variant
        self.username = username
        self.password = password
        self.hosts = generate_json_host_list(hosts)


    def connect(self):
        if self.variant = 'opensearch':
            client = OpenSearch(
                hosts=self.hosts,
                http_compress=True,
                http_auth=(self.username, self.password),
                use_ssl=True,
                verify_certs=True,
                ssl_assert_hostname=False,
                ssl_show_warn=False
            )
            return client

        elif self.variant = 'elasticsearch':
            hosts, port = generate_os_host_list(self.hosts)
            port = 0
            client = Elasticsearch(
                hosts,
                http_auth=(self.username, self.password),
                scheme='https',
                port=list(self.hosts.values()).[0]
            )
            return client
