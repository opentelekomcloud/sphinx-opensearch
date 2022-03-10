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
import argparse
import json
import os
import sys
import logging

from bs4 import BeautifulSoup
from sphinx_opensearch.common.clients import create_index
from sphinx_opensearch.common.clients import Searchclient


def get_parser():
    # Format the output of help
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        '--base-url',
        metavar='<base_url>',
        required=True,
        help='Base-URL used to define a given URL where the documentation '
             'files are listed, e.g. http://test.com/'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Option enables Debug output.'
    )
    parser.add_argument(
        '--delete-index',
        action='store_true',
        help='Option deletes old index with the same name and creates new '
             'one.'
    )
    parser.add_argument(
        '--doc-url',
        metavar='<doc_url>',
        help='Optional URL part to substitute different documentation '
             'names under a given base-url, e.g. api-ref/service-A/ . '
             'The combination of mandatory base-URL and optional '
             'doc-URL results in the final URL.'
    )
    parser.add_argument(
        '--hosts',
        metavar='<host:port>',
        nargs='+',
        default=['localhost:9200'],
        help='Provide one or multiple host:port values '
             'separated by space for multiple hosts.\n'
             'Default: localhost:9200'
    )
    parser.add_argument(
        '--index',
        metavar='<index>',
        default='test-index',
        help="OpenSearch / ElasticSearch index name.\n"
             'Default: test-index'
    )
    parser.add_argument(
        '--path',
        metavar='<path>',
        default=".",
        help="Path to json output folder of Sphinx json-build process.\n"
             'Default: .'
    )
    parser.add_argument(
        '--post-count',
        metavar='<count>',
        default=5,
        type=int,
        help='Number of files being loaded for indexing at the same time.\n'
             'Default: 5'
    )
    parser.add_argument(
        '--user',
        metavar='<username>',
        help='Username for the connection.'
    )
    parser.add_argument(
        '--password',
        metavar='<password>',
        help='Password for the connection.'
    )
    parser.add_argument(
        '--variant',
        metavar='<variant>',
        default='opensearch',
        choices=['elasticsearch', 'opensearch'],
        help=('Search backend variant.\n'
              'default: opensearch\n'
              'choices: elasticsearch, opensearch')
    )

    args = parser.parse_args()
    return args


def get_user(args):
    user = {
        'name': '',
        'password': ''
    }
    user['name'] = os.environ.get('SEARCH_USER')
    user['password'] = os.environ.get('SEARCH_PASSWORD')
    if not user['name']:
        if args.user:
            user['name'] = args.user
        else:
            raise Exception('SEARCH_USER environment variable or --user '
                            'parameter do not exist.')
    if not user['password']:
        if args.password:
            user['password'] = args.password
        else:
            raise Exception('SEARCH_PASSWORD environment variable or '
                            '--password parameter do not exist.')
    return user


def delete_index(client, index):
    try:
        client.indices.delete(index=index, ignore=[400, 404])
    except Exception as e:
        sys.exit('Exception raised while index deletion:\n' + str(e))


def add_end_slash(path):
    if path[-1] != '/':
        path = path + '/'
    return path


def remove_start_slash(path):
    if path[0] == '/':
        path = path[1:]
    return path


def get_file_structure(path):
    try:
        f = open(path + "searchindex.json",)
        data = json.load(f)
        f.close()
    except FileNotFoundError:
        sys.exit('File searchindex.json not found under the specified path.')
    file_structure = data['docnames']
    return file_structure


def create_index_data(client, path, file_structure,
                      index, post_count, variant, base_url,
                      doc_url):
    json_list = []
    responses = []
    file_structure_length = len(file_structure)
    i = 0
    count = 0
    for file in file_structure:
        file_path = path + file + '.fjson'
        try:
            file = open(file_path,)
            data = json.load(file)
            data['base_url'] = base_url
            data['doc_url'] = doc_url
            data["body"] = BeautifulSoup(data["body"], "lxml").text
            file.close()
        except Exception as e:
            sys.exit("\nERROR:\n" + str(e))
        json_list.append(data)
        file_structure_length -= 1
        i += 1
        count += 1
        if (i < post_count) and (file_structure_length != 0):
            continue
        else:
            resp = create_index(
                client=client,
                json_list=json_list,
                index=index,
                variant=variant
            )
            responses.append(resp)
            json_list = []
            i = 0

    json_response = {
        'responses': responses,
        'uploaded_files': count
    }
    return json_response


def main():
    args = get_parser()
    user = get_user(args)

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    client = Searchclient(
        variant=args.variant,
        username=user['name'],
        password=user['password'],
        hosts=args.hosts
    )
    client = client.connect()

    if args.delete_index:
        delete_index(client=client, index=args.index)
    path = add_end_slash(args.path)
    file_structure = get_file_structure(path)

    base_url = add_end_slash(args.base_url)

    if args.doc_url:
        doc_url = add_end_slash(args.doc_url)
        doc_url = remove_start_slash(doc_url)

        response = create_index_data(
            client=client,
            path=path,
            file_structure=file_structure,
            index=args.index,
            post_count=args.post_count,
            variant=args.variant,
            base_url=base_url,
            doc_url=doc_url
        )

    else:
        response = create_index_data(
            client=client,
            path=path,
            file_structure=file_structure,
            index=args.index,
            post_count=args.post_count,
            variant=args.variant,
            base_url=base_url,
            doc_url=''
        )

    print(str(response['uploaded_files']) + ' new files successfully imported'
          ' to index ' + args.index)


if __name__ == "__main__":
    main()
