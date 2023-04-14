![linting](https://github.com/visier/connector-python/actions/workflows/pylint.yml/badge.svg) ![pypi publishing](https://github.com/visier/connector-python/actions/workflows/publish-to-test-pypi.yml/badge.svg)
# Visier Python Connector
Use the Visier Python Connector to query Visier People data.

The connector enables Python developers to query Visier People data using Visier's SQL-like query language. 

## Prerequisites
The connector acts as a bridge between your Python application, which is typically Pandas-enabled, and Visier's cloud-hosted service infrastructure. In order to successfully connect to your Visier People data, you need:
* The URL domain name prefix. For example: `https://{vanity-name}.api.visier.io`.
* An API key issued by Visier.
* A username identifying a user within your organization's Visier tenant who has been granted API access capabilities.
* That user's password

## Example
This connector was authored with [Pandas](https://pandas.pydata.org/) in mind.

A small set of example queries have been provided. Generally, Visier Query API queries fall into one of two categories:
1. **Detail query** - These queries produce tabular results from underlying individual analytic objects. The shape of the result is inherently tabular with each table attribute represented as a column in the result set. Detail queries are often referred to as `list` or even `drill-through` queries. This query provides a detailed, non-aggregated view of the underlying analytical objects.
1. **Aggregate query** - These queries aggregate metric values. They do so along the axes defined for the query and they produce multi-dimensional cell sets by default However, by providing an `Accept` header whose first value is either `application/jsonlines` or `text/csv`, the server will flatten the cell set into a tabular format when building the response.

Visier also offers an experimental alternative to the JSON-based query definitions: SQL-like. This allows you to make queries using a language that comes close to SQL, which is generally more compact and intuitive. SQL-like allows definition of both aggregate and detail queries.

:warning: **SQL-like is in alpha stage and not yet suitable for production use**.

Example queries are provided through individual _files_. This is merely for convenience. SQL-like, being simple strings, can easily be provided to the call itself.

In order to reduce duplication, each provided sample below should be preceded by the necessary `import` statements as well as authentication credential definition:
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
This is an example of a snippet that may be added to something that loads detailed data such as a Jupyter Notebook. Detailed data is essentially granular, non-aggregated data from Visier entities. For example, subjects such as `Employee` or events such as `Compensation_Payout`.
```python
# List query from JSON query definition
list_query = load_json("detail/employee-pay_level.json")
list_result = s.executeList(list_query)
df_list = pd.DataFrame.from_records(data=list_result.rows(), columns=list_result.header)

# ...
print(df_list.head)
```

### Aggregate Query
Aggregate queries execute queries around Visier's predefined metrics. A metric is a calculation that targets a specific quantifiable question or scenario. They range from very simple like `employeeCount` to more complex ones like `hrRecruitingBudgetedLaborCostPerFTE`. 

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
This example shows the query definition. Notice how the options object can be used to aggressively eliminate zero and null-valued cells for the purpose of reducing the size of the overall result set to only include rows whose metric value > 0.
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
Add `visier-connector` as a dependency to your module or install directly: `pip install -U visier-connector`
