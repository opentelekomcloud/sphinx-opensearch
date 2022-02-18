# Sphinx-Opensearch

The project sphinx-opensearch is used to index Sphinx-based documentations into Opensearch or Elasticsearch environments.
The current application is in alpha state and will be maintained continuosly until a first productive version will be released.

## Installation

The following instructions describe several ways to install sphinx-opensearch.

### Installation via PyPi repository

```
pip install sphinx-opensearch
```

### Installation from Sources

```
git clone git@github.com:opentelekomcloud/sphinx-opensearch.git
cd ./sphinx-opensearch
python setup.py install
```

## Parameter

The listed parameters are used to configure the indexing behavior of python-spinxsearch.

| Parameter | Default | Function |
| ---------------------- | ----------- | ----------- |
| `--base-url <base_url>` || Base-URL used to define a given URL where the documentation files are listed, e.g. http://test.com/ |
| `--delete-index` || If this parameter is set, the content of the index will be deleted first. |
| `--doc-url <doc_url>` || Optional URL part to substitute different documentation names under a given base-url, e.g. api-ref/service-A/ . The combination of mandatory base-URL and optional doc-URL results in the final URL. |
| `--hosts <host:port>` | localhost:9200 | Provide one or multiple host_port values separated by space for multiple hosts. |
| `--index <index>` | test-index | OpenSearch / ElasticSearch index name |
| `--path <path>` | ./ | Path to json output folder of Sphinx. |
| `--post-count <count>` | 5 | Number of files being loaded for indexing iteration at the same time. |
| `--user <username>` || Username authorized for indexing operations. If the environment variable SEARCH_USER is set, the parameter will be omitted. |
| `--password <password>` || Password for the user account. If the environment variable SEARCH_PASSWORD is set, the parameter will be omitted. |
| `--variant <variant>` | opensearch | Search backend variant. Choices: elasticsearch, opensearch |

## Example

The following example shows the usage of sphinx-opensearch. 

---
**NOTE**

As prerequesit the Sphinx-build process of any project has already been finished and the build format is **JSON**.

---

```
sphinxsearch --delete-index --base-url 'http://test.com/' --doc-url 'umn/compute/' --hosts myhost:9200 yourhost:9200 --index compute --path path/to/sphinx/json-output/ --post-count 5 --user ME --password PW --variant opensearch
```