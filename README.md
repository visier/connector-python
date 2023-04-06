![linting](https://github.com/visier/connector-python/actions/workflows/pylint.yml/badge.svg) ![pypi publishing](https://github.com/visier/connector-python/actions/workflows/publish-to-test-pypi.yml/badge.svg)
# Visier Python Connector
Use the Visier Python Connector to query Visier People Data.

The connector enables Python developers to query Visier People Data using Visier's SQL-like query language. 

## Prerequisites
The connector acts as middleware between your (typically Pandas-enabled) Python application and Visier's cloud-hosted service infrastructure. In order to successfully connect to your Visier People data, you need:
* The URL domain name prefix. Likely matching a pattern like this: `https://{vanity-name}.api.visier.io`.
* An API key that issued by Visier to your organization.
* A username identifying a user within your organization's Visier tenant who has been granted API access capabilities.
* That user's password

## Example
This connector was authored with [Pandas](https://pandas.pydata.org/) in mind.

A small set of example queries have been provided. Generally, Visier Query API queries fall into one of two categories:
1. **Detail query** - These queries produce tabular results from underlying individual 'Analytic Objects'. The shape of the result is inherently tabular with each table attribute represented as a column in the result set. Detail queries are often referred to as `list` or even `drill-through` queries. They all mean the same thing; a detailed, i.e. non-aggregated, view of the underlying analytical objects.
1. **Aggregate query** - As the name implies, these kinds of queries aggregate metric values. They do so along the axes defined for the query and they produce multi-dimensional cell sets by default, though by providing an `Accept` header whose first value is either `application/jsonlines` or `text/csv`, the server will flatten the cell set into a tabular format when building the response.

Visier also offers an experimental alternative to the JSON-based query definitions: SQL-like. As the alluded to by the name, this allows for queries using a language that comes close to SQL and is generally are more compact and intuitive query representation. SQL-like alllows definition of both aggregate as well as detail queries

:warning: SQL-like is in alpha stage and not suitable for use in production yet. Query feature-wise SQL-like is a proper subset with currently active development to close the parity gap.

Example queries are provided through individual files. This is merely for convenience. SQL-like, being simple strings, can easily be defined close the query call itself.

In order to reduce duplication, each provided sample below should be preceded by the necessary `import`s as well as authentication credential definition:
```python
import os
from visier.connector import Authentication, VisierSession
from examples import load_json, load_str
import pandas as pd

auth = Authentication(
    username = os.getenv("SOME_USERNAME"),
    password = os.getenv("SOME_PASSWORD"),
    host = os.getenv("SOME_HOST"),
    api_key = os.getenv("SOME_APIKEY"))
```

### Detail Query
This is an example of a snippet that may be added to e.g. a Jupyter Notebook that loads detailed data. Detailed data is essentially granular, i.e. non-aggregated, data from Visier entities, e.g. Subjects such as `Employee` or Events such as `Compensation_Payout`.
```python
# List query from JSON query definition
list_query = load_json("detail/employee-pay_level.json")
list_result = s.executeList(list_query)
df_list = pd.DataFrame.from_records(data=list_result.rows(), columns=list_result.header)

# ...
print(df_list.head)
```

### Aggregate Query
Aggregate queries, in contrast, executes queries around Visier's predefined Metrics. A Metric is an arbitrarily complex calculation that targets a specific quantifiable question or scenario. They range from very simple like `employeeCount` to more complex ones like `hrRecruitingBudgetedLaborCostPerFTE`. 

With a `VisierSession` available, an aggregate query is executed functionally identically:
```python
# Aggregate query from JSON query definition
aggregate_query = load_json("aggregate/applicants-source.json")
aggregate_result = s.executeAggregate(aggregate_query)
df_aggregate = pd.DataFrame.from_records(data=aggregate_result.rows(), columns=aggregate_result.header)

# Now that the data is in a Pandas Data Frame, do something with it, or just...
print(df_aggregate.head)
```

### SQL-like Queries
SQL-like allows definition of both aggregate as well as detail queries:

#### Detail Query
```python
# SQL-like detail query
sql_detail_query = load_str("sql-like/detail/employee-demo.sql")
list_result = s.executeSqlLike(sql_detail_query)
df_list = pd.DataFrame.from_records(data=list_result.rows(), columns=list_result.header)

# ...
print(df_list.head)
```

#### Aggregate Query
This example shows, in addition the query definition itself, how the `options` object can be used to aggressively eliminate zero and null-valued cells for the purpose of reducing the size of the overall result set to only include rows whose metric value > 0.
```python
# SQL-like aggregate query
sql_aggregate_query = load_str("sql-like/aggregate/employee-count.sql")
sparse_options = load_json("sql-like/options/sparse.json")
aggregate_result = s.executeSqlLike(sql_aggregate_query, sparse_options)
df_aggregate = pd.DataFrame.from_records(data=aggregate_result.rows(), columns=aggregate_result.header)

# ...
print(df_aggregate.head)
```

## Installation
Add `visier-connector` as a dependency or install directly e.g. in a virtual environment: `pip install -U visier-connector`
