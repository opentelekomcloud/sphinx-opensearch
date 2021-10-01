import argparse
import json
from elasticsearch import Elasticsearch, helpers

es = Elasticsearch()
parser = argparse.ArgumentParser()

parser.add_argument(
    '--hostname',
    metavar='<hostname>',
    help='Elasticsearch hostname.'
)
parser.add_argument(
    '--index',
    metavar='<index>',
    default='test-index',
    help='Elasticsearch index.'
)
parser.add_argument(
    '--path',
    metavar='<path>',
    help='Path to json output folder of Sphinx.'
)
parser.add_argument(
    '--port',
    metavar='<port>',
    choices=[443],
    help='Elasticsearch port.'
)
parser.add_argument(
    '--post-count',
    metavar='<count>',
    default=5,
    type=int,
    help='Number of files being loaded for elasticsearc import at the same\n'
         'time.'
)
parser.add_argument(
    '--user',
    metavar='<username>',
    help='Elasticsearch username.'
)
parser.add_argument(
    '--scheme',
    metavar='<scheme>',
    choices=['https', 'http'],
    help='Elasticsearch scheme.'
)
parser.add_argument(
    '--secret',
    metavar='<secret>',
    help='Elasticsearch secret.'
)

args = parser.parse_args()
path = args.path
if path[-1] != '/':
    path = path + '/'
f = open(path + "/searchindex.json",)
data = json.load(f)
f.close()

file_names = data['docnames']



json_list = []
file_names_length = len(file_names)
i = 0
for f in file_names:
    fn = path + f + '.fjson'
    try:
        file = open(fn,)
        data = json.load(file)
        file.close()
    except Exception as e:
        print("\nERROR:", e)
    json_list.append(data)
    file_names_length -= 1
    i += 1
    if (i < args.post_count) and (file_names_length != 0):
        continue
    else:
        try:
            response = helpers.bulk(es, json_list, index=args.index)
            print ("\nactions RESPONSE:", response)
        except Exception as e:
            print("\nERROR:", e)
        json_list = []
        i = 0
