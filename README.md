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

## Authentication Environment
As of version `0.9.8`, the Visier Python Connector supports two means of authentication:
1. OAuth2.0: The connector supports the so called three-legged authentication flow. This means that authentication (and consent) have to be provided through the authorization server. In accordance with the OAuth2.0 protocol, no user credentials are provided directly to Visier. This is the preferred authentication method.
1. Basic Authentication: This is a traditional authentication mechanism where Visier username and password are provided directly to Visier for authentication.

In order to avoid passing authentication credentials in via command line arguments, Visier recommends that at least basic authentication credentials such as username and password are provided via environment variables. However, using a new function, `make_auth()`, the appropriate authentication configuration object will be created from `VISIER_`-prefixed environment variables, as outlined  below.

### OAuth2.0
Though the Visier Python Connector doesn't directly interact with the environment variables, the following list and example below illustrate the OAuth2.0 authentication parameters. These are also the environment variables the `make_auth()` utility function will use.
* `VISIER_HOST`: The fully qualified domain name and protocol to access your Visier tenant as well as to initiate the OAuth2.0 authentication process
* `VISIER_APIKEY`: The API key granted by Visier
* `VISIER_CLIENT_ID`: The identifier of the pre-registered application
* `VISIER_REDIRECT_URI`: The URI the `authorize` call will ultimately redirect to upon a successful authorization code generation. By default, this will be `http://localhost:5000/oauth2/callback` however note that it must match the `redirect_uri` in the client application definition exactly. If the client application setting is different, it is essential that that exact value is provided to the connector.
* `VISIER_TARGET_TENANT_ID`: The technical name of the tenant for the customer. This is only applicable in partner configurations

On Linux-like systems, with an X-display available, create a file named `.env` and populate it like the following example, substituting with actual values as appropriate:
```sh
export VISIER_HOST=https://customer-specific.api.visier.io
export VISIER_CLIENT_ID=client-id
export VISIER_APIKEY=the-api-key-issued-by-visier
export VISIER_REDIRECT_URI=
# export VISIER_REDIRECT_URI=http://localhost:5000/oauth2/callback
export VISIER_TARGET_TENANT_ID=
export VISIER_USERNAME=
export VISIER_PASSWORD=
```

Source this file in and the environment is ready for using the connector with OAuth2.0 authentication:
```sh
$ source .env
```

### Basic Authentication
Though the Visier Python Connector doesn't directly interact with the environment variables, the following list and example below illustrate the basic authentication parameters. These are also the environment variables the `make_auth()` utility function will use.
* `VISIER_HOST`: The fully qualified domain name and protocol to access your Visier tenant
* `VISIER_USERNAME`: The user name with sufficient API capabilities
* `VISIER_PASSWORD`: The password of that user
* `VISIER_APIKEY`: The API key granted by Visier
* `VISIER_VANITY`: The readable name of the customer organization
* `VISIER_TARGET_TENANT_ID`: The technical name of the tenant for the customer. This is only applicable in partner configurations

To illustrate this process, consider the following example approach suitable in a non-production environment:

On Linux-like systems, create a file named `.env` and populate it like the following example, substituting with actual values as appropriate:
```sh
echo -n "Enter the password for the Visier API User: "
read -s vpwd
export VISIER_VANITY=customer-specific
export VISIER_HOST=https://$VISIER_VANITY.api.visier.io
export VISIER_USERNAME=apiuser@example.com
export VISIER_PASSWORD=$vpwd
export VISIER_TARGET_TENANT_ID=tenant-code
export VISIER_APIKEY=the-api-key-issued-by-visier
export VISIER_CLIENT_ID=
```

Source this environment in and provide the password when prompted:
```sh
$ source .env
```

## Connector Separation
As of version `0.9.5`, the Python connector has separated the API calls from the `VisierSession` object. As a result of this change, the query execution methods on the `VisierSession` have been deprecated and will be subject to removal in a future release.

The new way of invoking Visier public APIs through the Visier Python connector requires instantiating the appropriate API client and calling the methods defined on the client object. The following example, invokes the `analytic-objects` Model API to obtain the metadata for two analytic objects:
```python
    with VisierSession(auth) as session:
        model_client = ModelApiClient(session)

        objs = model_client.get_analytic_objects(["Requisition", "Employee_Exit"])
        print(objs.text)
```
### Error handling
By default, a failed API call will return `None` and information about the error is available on the client object. Using the example above, the last error in the event `objs` was `None` would be `model_client.last_error()`.

It is however possible to force the API client to instead raise a `QueryExecutionException`. This is accomplished when instantiating the API client with the following parameter value `raise_on_error=True`. Using the example above, the `model_client` instantiation would look like this: `model_client = ModelApiClient(session, raise_on_error=True)`.

# Examples
## Query API
The Query API Client is used to make calls to Visier's Query APIs. 

**Note that the `examples` in this repository are not included in the `visier-connector` package** Instead, these `examples` should be copied into a sample application or the example queries can be run with a test script in this repository as per the snippets below.

The Query API examples use [Pandas](https://pandas.pydata.org/) to illustrate a common data engineering and data science workflow using Visier data.
 
A small set of example queries have been provided. Generally, Visier Query API queries fall into one of two categories:
1. **Detail query** - These queries produce tabular results from underlying individual analytic objects. The shape of the result is inherently tabular with each table attribute represented as a column in the result set. Detail queries are often referred to as `list` or even `drill-through` queries. This query provides a detailed, non-aggregated view of the underlying analytical objects.
1. **Aggregate query** - These queries aggregate metric values. They do so along the axes defined for the query and they produce multi-dimensional cell sets by default However, by providing an `Accept` header whose first value is either `application/jsonlines` or `text/csv`, the server will flatten the cell set into a tabular format when building the response.

Visier also offers an experimental alternative to the JSON-based query definitions: SQL-like. This allows you to make queries using a language that comes close to SQL, which is generally more compact and intuitive. SQL-like allows definition of both aggregate and detail queries.

Example queries are provided through individual _files_. This is merely for convenience. SQL-like, being simple strings, can easily be provided to the call itself.

In order to reduce duplication, each provided sample below should be preceded by the necessary `import` statements as well as authentication credential definition (note the use of pandas here is only demo purposes. The Visier Python Connector does not depend on pandas):
```python
import os
from visier.connector import VisierSession, make_auth
from visier.api import QueryApiClient
from examples import load_json, load_str
import pandas as pd

auth = make_auth()
```

### Detail Query
This is an example of a snippet that may be added to something that loads detailed data such as a Jupyter Notebook. Detailed data is essentially granular, non-aggregated data from Visier entities. For example, subjects such as `Employee` or events such as `Compensation_Payout`.
```python
with VisierSession(auth) as s:
    client = QueryApiClient(s)
    # List query from JSON query definition
    list_query = load_json("detail/employee-pay_level.json")
    list_result = client.list(list_query)
    df_list = pd.DataFrame.from_records(data=list_result.rows(), columns=list_result.header)

    # ...
    print(df_list.head)
```

### Aggregate Query
Aggregate queries execute queries around Visier's predefined metrics. A metric is a calculation that targets a specific quantifiable question or scenario. They range from very simple like `employeeCount` to more complex ones like `hrRecruitingBudgetedLaborCostPerFTE`. 

With a `VisierSession` available, an aggregate query is executed functionally identically:
```python
with VisierSession(auth) as s:
    client = QueryApiClient(s)
    # Aggregate query from JSON query definition
    aggregate_query = load_json("aggregate/applicants-source.json")
    aggregate_result = client.aggregate(aggregate_query)
    df_aggregate = pd.DataFrame.from_records(data=aggregate_result.rows(), columns=aggregate_result.header)

    # Now that the data is in a Pandas Data Frame, do something with it, or just...
    print(df_aggregate.head)
```

### SQL-like Queries
SQL-like allows definition of both aggregate as well as detail queries:

#### Detail Query
```python
with VisierSession(auth) as s:
    client = QueryApiClient(s)
    # SQL-like detail query
    sql_detail_query = load_str("sql-like/detail/employee-demo.sql")
    list_result = client.sqllike(sql_detail_query)
    df_list = pd.DataFrame.from_records(data=list_result.rows(), columns=list_result.header)

    # ...
    print(df_list.head)
```

#### Aggregate Query
This example shows the query definition. Notice how the options object can be used to aggressively eliminate zero and null-valued cells for the purpose of reducing the size of the overall result set to only include rows whose metric value > 0.
```python
with VisierSession(auth) as s:
    client = QueryApiClient(s)
    # SQL-like aggregate query
    sql_aggregate_query = load_str("sql-like/aggregate/employee-count.sql")
    sparse_options = load_json("sql-like/options/sparse.json")
    aggregate_result = client.sqllike(sql_aggregate_query, sparse_options)
    df_aggregate = pd.DataFrame.from_records(data=aggregate_result.rows(), columns=aggregate_result.header)

    # ...
    print(df_aggregate.head)
```

## Model API
The Model API Client is used to make calls to the Visier Model API.
In order to run the example below, ensure you add the following import statement to your program:
```python
from visier.api import ModelApiClient
```

In the example below, we query for the metadata for two named selection concepts on the `Requisition` analytic object:
```python
    with VisierSession(auth) as session:
        model_client = ModelApiClient(session)

        concepts = model_client.get_selection_concepts("Requisition", ["isRequisitionbyOtherIncomingReasons", "isActiveRequisition"])
        print(concepts)
```

## Direct Intake API
The Direct Intake API enable clients to load data whose structure already matches the target analytic object.
Be sure to import the appropriate API client: `from visier.api import DirectIntakeApiClient`

The instantiation of the API client follows the same pattern as both Query and Model. Regarding the semantics of the API, there are two points to be mindful of:
1. The Direct Intake API is so called because this method of loading data into the Visier system relies on the source data already having been cleansed, deduplicated and transformed. Should these criteria not be met, then these APIs are not suitable for loading data, and alternative methods that leverage Visier's Data Provisioning data transformation mechanisms should be used instead.
1. The call sequence follows a transactional pattern. A transaction is started, followed by a number of uploads after which the transaction is either committed or, in cases where the load should be aborted, rolled-back.

:warning: Please be sure to read the product documentation to ensure the API calling principal has sufficient capabiltities to successfully make these calls.

### Schema determination
As this load mechanism is strictly dependent on the structure of the source files matching the schema of the target objects, a `schemas` API is available to query for the so called 'staging' schema of the target object:
```python
schema = intake_client.get_object_schema("Employee_Exit")
```
It's important to note that this schema is distinct from the so called 'analytic' schema obtained through the Model API. The 'analytic' schema will include elements that are used during query composition and will include artifacts whose values are derived from others. The 'staging' schema on the other hand, contains only key fields, simple properties, dimension and reference keys.

### Load example
Below is a simple example that shows loading data for Employee and Employee_Exit:
```python
    with VisierSession(auth) as session:
        intake_client = DirectIntakeApiClient(session, raise_on_error=True)

        try:
            response = intake_client.start_transaction()
            tx_id = response.json()["transactionId"]
            print(f"Transaction ID: {tx_id}")

            response = intake_client.upload_file(tx_id, "Employee", "/tmp/data/employee-data.zip")
            print(response)

            response = intake_client.upload_file(tx_id, "Employee_Exit", "/tmp/data/exits.csv")
            print(response)
            
            response = intake_client.commit_transaction(tx_id)
            print(response)
        except:
            print(f"Intake failed. Rolling back {tx_id}")
            intake_client.rollback_transaction(tx_id)
```

### Any Visier public API
While connector provides specific functions for querying data, it also provides a lower level, generic function for executing other public Visier APIs. Below is a simple example for determining which Plans have been defined for a given model:
```python
def get_location_levels(context: SessionContext) -> Response:
    path = "/v1/data/model/plan-models/WorkforcePlanModel/plans"
    return context.session().get(url=context.mk_url(path))

with VisierSession(auth) as s:
    levels = s.execute(get_location_levels)
    print(levels.json())
```

## Installation
Add `visier-connector` as a dependency to your module or install directly: `pip install -U visier-connector`
