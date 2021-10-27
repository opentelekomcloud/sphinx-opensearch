# Python-Sphinxsearch

The project python-sphinxsearch is used to index Sphinx-based documentations into Opensearch or Elasticsearch environments.
The current application is in alpha state and will be maintained continuosly until a first productive version will be released.

## Installation

## Parameters

The listed parameters are used to configure the indexing behavior of python-spinxsearch.

| Parameter | Function |
| ---------------------- | ----------- |
| `--delete-index` | If this parameter is set, the content of the index will be deleted first. |
| `--hosts <host:port>` | Provide one or multiple host_port values separated by space for multiple hosts. |
| `--index <index>` | Search index name; default: test-index |
| `--path <path>` | Path to json output folder of Sphinx. |
| `--post-count <count>` | Number of files being loaded for indexing iteration at the same time. Default: 5. |
| `--user <username>` | Username authorized for indexing operations. If the environment variable SEARCH_USER is set, the parameter will be omitted. |
| `--password <password>` | Password for the user account. If the environment variable SEARCH_PASSWORD is set, the parameter will be omitted. |
| `--variant <variant>` | Search backend variant. Choices: elasticsearch, opensearch (default) |