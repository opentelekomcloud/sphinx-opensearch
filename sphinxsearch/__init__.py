import argparse
import json
import sys

from elasticsearch import Elasticsearch, helpers


def get_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--delete-index',
        action='store_true',
        help='Option deletes old index with the same name and creates new '
             'one.'
    )
    parser.add_argument(
        '--hostname',
        metavar='<hostname>',
        help='Elasticsearch hostname.'
    )
    parser.add_argument(
        '--index',
        metavar='<index>',
        default='test-index',
        help='Elasticsearch index.\n'
             'Default: test-index'
    )
    parser.add_argument(
        '--path',
        metavar='<path>',
        default=".",
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
        help='Number of files being loaded for elasticsearch import at the\n'
             'same time.'
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
    return args

def delete_index(es, index):
    try:
        es.indices.delete(index=index, ignore=[400, 404])
    except Exception as e:
        sys.exit('Exception raised while index deletion:\n' + e)

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


def create_index(es, json_list, index):
    try:
        response = helpers.bulk(es, json_list, index=index)
    except Exception as e:
        sys.exit("\nERROR:\n" + e)
    return response


def create_index_data(es, path, file_structure, index, post_count):
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
            file.close()
        except Exception as e:
            sys.exit("\nERROR:\n" + e)
        json_list.append(data)
        file_structure_length -= 1
        i += 1
        count += 1
        if (i < post_count) and (file_structure_length != 0):
            continue
        else:
            resp = create_index(es, json_list, index)
            responses.append(resp)
            json_list = []
            i = 0
    json_response = {
        'responses': responses,
        'uploaded_files': count
    }
    return json_response


def main():
    es = Elasticsearch()
    args = get_parser()
    if args.delete_index:
        delete_index(es=es, index=args.index)
    path = generate_path(args)
    file_structure = get_file_structure(path)
    response = create_index_data(
        es=es,
        path=path,
        file_structure=file_structure,
        index=args.index,
        post_count=args.post_count
    )
    print(str(response['uploaded_files']) + ' new files successfully imported'
          ' to index ' + args.index)


if __name__ == "__main__":
    main()
