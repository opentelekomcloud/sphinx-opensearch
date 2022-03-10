# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import sys

from elasticsearch import Elasticsearch
from elasticsearch import helpers as es_helpers

from opensearchpy import helpers as os_helpers
from opensearchpy import OpenSearch


def generate_os_host_list(hosts):
    host_list = []
    for host in hosts:
        raw_host = host.split(':')
        if len(raw_host) != 2:
            raise Exception('--hosts parameter does not match the following '
                            'format: hostname:port')
        json_host = {'host': raw_host[0], 'port': int(raw_host[1])}
        host_list.append(json_host)
    return host_list


def generate_es_host_list(hosts):
    port_sum = 0
    port = None
    host_list = []

    for host in hosts:
        raw_host = host.split(':')
        host_list.append(raw_host[0])
        raw_host[1] = int(raw_host[1])
        port_sum += raw_host[1]
        if not port:
            port = raw_host[1]

    if ((port_sum // len(hosts)) != port):
        raise Exception('Error: For variant elasticsearch specified ports '
                        'cannot be different: ' + str(hosts))

    return host_list, port


def create_index(client, json_list, index, variant):
    try:
        if variant == 'opensearch':
            response = os_helpers.bulk(
                client,
                json_list,
                index=index
            )
        if variant == 'elasticsearch':
            response = es_helpers.bulk(
                client,
                json_list,
                index=index
            )
    except Exception as e:
        sys.exit("\nERROR:\n" + str(e))
    return response


class Searchclient:

    def __init__(self, variant, username, password, hosts):
        self.variant = variant
        self.username = username
        self.password = password
        self.hosts = hosts

    def connect(self):
        if self.variant == 'opensearch':
            hosts = generate_os_host_list(self.hosts)
            client = OpenSearch(
                hosts=hosts,
                http_compress=True,
                http_auth=(self.username, self.password),
                use_ssl=True,
                verify_certs=True,
                ssl_assert_hostname=False,
                ssl_show_warn=False
            )
            return client

        elif self.variant == 'elasticsearch':
            hosts, port = generate_es_host_list(self.hosts)
            client = Elasticsearch(
                hosts=hosts,
                http_auth=(self.username, self.password),
                scheme='https',
                port=port
            )
            return client
