import argparse
import json
import sys
from bs4 import BeautifulSoup
from common.clients import Searchclient, create_index


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--delete-index',
        action='store_true',
        help='Option deletes old index with the same name and creates new '
             'one.'
    )
    parser.add_argument(
        '--hosts',
        metavar='<host:port>',
        nargs='+',
        default=['localhost:9200'],
        help='Provide one or multiple host:port values '
             'separated by space for multiple hosts.'
    )
    parser.add_argument(
        '--index',
        metavar='<index>',
        default='test-index',
        help='Search index for OpenSearch or ElasticSearch.\n'
             'Default: test-index'
    )
    parser.add_argument(
        '--path',
        metavar='<path>',
        default=".",
        help='Path to json output folder of Sphinx.'
    )
    parser.add_argument(
        '--post-count',
        metavar='<count>',
        default=5,
        type=int,
        help='Number of files being loaded for indexing at the\n'
             'same time.'
    )
    parser.add_argument(
        '--user',
        metavar='<username>',
        required=True,
        help='Username for the connection.'
    )
    parser.add_argument(
        '--password',
        metavar='<password>',
        required=True,
        help='Password for the connection.'
    )
    parser.add_argument(
        '--variant',
        metavar='<variant>',
        default='opensearch',
        choices=['elasticsearch', 'opensearch'],
        help=('Search backend variant.\n'
              'default: elasticsearch\n'
              'choices: elasticsearch, opensearch')
    )

    args = parser.parse_args()
    return args


def delete_index(client, index):
    try:
        client.indices.delete(index=index, ignore=[400, 404])
    except Exception as e:
        sys.exit('Exception raised while index deletion:\n' + str(e))


def generate_path(args):
    path = args.path
    if path[-1] != '/':
        path = path + '/'
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
                      index, post_count, variant):
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

    client = Searchclient(
        variant=args.variant,
        username=args.user,
        password=args.password,
        hosts=args.hosts
    )
    client = client.connect()

    if args.delete_index:
        delete_index(client=client, index=args.index)
    path = generate_path(args)
    file_structure = get_file_structure(path)
    response = create_index_data(
        client=client,
        path=path,
        file_structure=file_structure,
        index=args.index,
        post_count=args.post_count,
        variant=args.variant
    )
    print(str(response['uploaded_files']) + ' new files successfully imported'
          ' to index ' + args.index)


if __name__ == "__main__":
    main()
