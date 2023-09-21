![linting](https://github.com/visier/connector-python/actions/workflows/pylint.yml/badge.svg) ![pypi publishing](https://github.com/visier/connector-python/actions/workflows/publish-to-test-pypi.yml/badge.svg)
# Visier Python Connector
The Visier Python Connector allows Python developers to query against the Visier platform in Visier's SQL-like syntax.

## Prerequisites
This connector acts as a bridge between your Python application and Visier's cloud-hosted service infrastructure. To successfully connect to your Visier data, you need:
* The URL domain name prefix. For example: `https://{vanity-name}.api.visier.io`.
* An API key issued by Visier.
* One of:
    * A registered OAuth client application in your Visier tenant.
    * A Visier username and password with API access capabilities.

## Authentication Environment
As of version `0.9.8`, the Visier Python Connector supports two authentication methods:
* **OAuth 2.0**: A three-legged authentication flow that authenticates through the authorization server. In OAuth 2.0 protocol, no user credentials are provided directly to Visier. We recommend using the OAuth 2.0 authentication method.
* **Basic authentication**: A traditional authentication flow that authenticates through a Visier username and password.

To avoid passing authentication credentials in with command-line arguments, Visier recommends that basic authentication credentials, such as username and password, are passed in through environment variables. You can use the `make_auth()` function to create the appropriate authentication configuration object from `VISIER_`-prefixed environment variables, as described below.

### OAuth 2.0
The following list defines the OAuth 2.0 authentication parameters. These are also the environment and `dotenv` variables the `make_auth()` utility function will use when instantiating an authentication object.
* `VISIER_HOST`: The fully qualified domain name and protocol to access your Visier tenant and initiate the OAuth 2.0 authentication process.
* `VISIER_APIKEY`: The API key granted by Visier.
* `VISIER_CLIENT_ID`: The identifier of the registered client application.
* `VISIER_CLIENT_SECRET`: The generated secret of the registered client application. This is required for customer-registered applications.
* `VISIER_REDIRECT_URI`: The URI the `authorize` call will redirect to upon a successful authorization code generation. By default, this is `http://localhost:5000/oauth2/callback` but the URI must match the `redirect_uri` in the client application registration exactly. If the client application URI is different, it is essential that that exact value is provided to the Python connector.
* `VISIER_TARGET_TENANT_ID`: The tenant code of the target tenant. This is only applicable in partner configurations.

The following example illustrates an authentication environment. Let's say you're using a Linux-like system with an X-display available. First, create a file named `.env` and then populate the file as shown next, substituting the example values with actual values as appropriate.
```sh
export VISIER_HOST=https://customer-specific.api.visier.io
export VISIER_CLIENT_ID=client-id
export VISIER_APIKEY=the-api-key-issued-by-visier
export VISIER_REDIRECT_URI=
# export VISIER_REDIRECT_URI=http://localhost:5000/oauth2/callback
export VISIER_TARGET_TENANT_ID=
export VISIER_USERNAME=
export VISIER_PASSWORD=

echo -n "Enter the client secret for client with id $VISIER_CLIENT_ID: "
read -s secret
export VISIER_CLIENT_SECRET=$secret
```

**Note**: You may provide a valid username and password combination with the variables above. If a username and password are provided along with the client ID and secret, the connector will use the password grant type instead of the authorization code grant type. We do not recommend the password grant type in a production environment.

Next, source the file below in and then the environment is ready to use the connector with OAuth 2.0 authentication.
```sh
$ source .env
```

Because the connector supports [python-dotenv](https://pypi.org/project/python-dotenv/) , some users may prefer to define assignments directly in `.env` instead of sourcing it into the OS environment. In the following snippet, the connector uses credentials obtained with dotenv.
```python
from dotenv import dotenv_values
from visier.connector import VisierSession, make_auth
from visier.api import ModelApiClient

env_creds = dotenv_values()
auth = make_auth(env_values=env_creds)

with VisierSession(auth) as s:
    ...
```
#### Callback URI
The OAuth 2.0 authentication flow requires that the authorizing server can call back to the initiating client with an authorization code. In OAuth mode, the connector starts a transient web server that listens for an authorization code on http://localhost:5000/oauth2/callback. You can modify the URL by setting a different value for `VISIER_REDIRECT_URI`. The `VISIER_REDIRECT_URI` value must exactly match the URI value in your Visier OAuth 2.0 client registration and must respect Visier's callback URI rules, such as a limited set of permissible subnets.

### Basic Authentication
The Visier Python Connector doesn't directly interact with the environment variables. The following list defines the basic authentication parameters. The basic authentication parameters are also the environment variables that the `make_auth()` utility function uses.
* `VISIER_HOST`: The fully qualified domain name and protocol to access your Visier tenant.
* `VISIER_USERNAME`: The Visier user that has sufficient API capabilities.
* `VISIER_PASSWORD`: The password of that user.
* `VISIER_APIKEY`: The API key granted by Visier.
* `VISIER_VANITY`: The vanity name of the Visier tenant.
* `VISIER_TARGET_TENANT_ID`: The tenant code of the target tenant. This is only applicable in partner configurations.

The following example illustrates an authentication environment. The example is suitable in a non-production environment.

Let's say you're using a Linux-like system. First, create a file named `.env` and then populate the file as shown next, substituting the example values with actual values as appropriate.
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

Next, source this environment in and provide the password when prompted.
```sh
$ source .env
```

## Jupyter Notebooks
Jupyter notebooks and lab are well-suited to run Visier connector code. However, some users may not find OS-level variables ideal. As of version `0.9.9`, the Visier Python connector supports [dotenv](https://pypi.org/project/python-dotenv/) to facilitate a more dynamic switching of Visier authentication parameters. If the file is called `.env`, the Python package `dotenv` attempts to load the file. If the file has a different name, you must provide that file name when loading the environment with `dotenv`.

### Jupyter Basic Authentication Example
Basic authentication is the most practical means of authenticating against Visier for Jupyter notebooks.

Create an environment file to store the authentication parameters.

Example environment file:
```
VISIER_VANITY=customer-specific
VISIER_HOST=https://customer-specific.api.visier.io
VISIER_APIKEY=the-api-key-issued-by-visier
VISIER_USERNAME=apiuser@example.com
VISIER_PASSWORD=password-or-variable-reference
```

Create a basic authentication object as described in the following snippet:
```python
from dotenv import dotenv_values
from visier.connector import VisierSession, make_auth
from visier.api import QueryApiClient

env_creds = dotenv_values()
auth = make_auth(env_values=env_creds)

with VisierSession(auth) as s:
    query_client = QueryApiClient(s)
    ...
```

### Jupyter OAuth 2.0 Example
OAuth authentication to Visier in Jupyter notebooks is only supported when the Jupyter server runs on your local computer, bound to `localhost`. We only recommend using OAuth in Jupyter notebooks against Visier for test and development uses.

To authenticate with OAuth, you must first register an OAuth 2.0 client in Visier. Visier administrators can register OAuth clients.

After the OAuth client is registered in Visier, create an environment file to store the authentication parameters.

Example environment file:
```
VISIER_HOST=https://customer-specific.api.visier.io
VISIER_CLIENT_ID=client-id-from-registration
VISIER_APIKEY=the-api-key-issued-by-visier
```

Create an OAuth authentication object, as described next.
```python
from dotenv import dotenv_values
from visier.connector import VisierSession, make_auth
from visier.api import QueryApiClient

env_creds = dotenv_values()
auth = make_auth(env_values=env_creds)

with VisierSession(auth) as s:
    query_client = QueryApiClient(s)
    ...
```

## Connector Separation
As of version `0.9.5`, the Python connector separates API calls from the `VisierSession` object. As a result of this change, query execution methods on the `VisierSession` are deprecated and will be removed in a future release.

As of version `0.9.5`, you can invoke Visier public APIs through the Visier Python connector by instantiating the appropriate API client and calling the methods defined on the client object. The following example invokes the `analytic-objects` Data Model endpoint to retrieve metadata for two analytic objects: `Requisition` and `Employee_Exit`.
```python
    with VisierSession(auth) as session:
        model_client = ModelApiClient(session)

        objs = model_client.get_analytic_objects(["Requisition", "Employee_Exit"])
        print(objs.text)
```
### Error Handling
By default, a failed API call returns `None` and information about the error is available on the client object. Using the example above, if the call failed, the value of `objs` is `None` (no value). To investigate why the call failed, you can call `model_client.last_error()` to find the issue.

It's possible to force the API client to instead raise a `QueryExecutionException`. To do so, instantiate the API client with the parameter value `raise_on_error=True`. Using the example above, the `model_client` instantiation would appear as `model_client = ModelApiClient(session, raise_on_error=True)`.

# Examples
## Data Query API
The Query API client makes calls to Visier's Data Query API. The Data Query API examples use [Pandas](https://pandas.pydata.org/) to illustrate common data engineering and data science workflows using Visier data.

**Note**: The `examples` in this repository are not included in the `visier-connector` package. To use the `examples`, copy them into a sample application or run the example queries with a test script in this repository as shown in the samples below.
 
Generally, Visier Query API queries are one of:
* **List query**: List queries provide a detailed, non-aggregated view of underlying analytic objects in a tabular format. Each table attribute represents a column in the result set. List queries are also referred to as `detail` or `drill through` queries.
* **Aggregate query**: Aggregate queries aggregate metric values. The API aggregates the query's defined axes and then produces multi-dimensional cell sets. To get a flat response rather than a multi-dimensional response, you can provide an `Accept` header whose first value is either `application/jsonlines` or `text/csv`. You must always include `application/json` after the flat format to successfully get error responses.

If you'd prefer not to make JSON-based queries, Visier offers a SQL-like alternative that allows you to make queries in a language close to SQL. This is preferable for users who prefer the more compact and intuitive aspects of SQL. You can define both aggregate and list queries in Visier's SQL-like dialect.

In this repository, example queries are provided in individual files for your convenience. However, SQL-like is formed with simple strings and can be provided to the call itself rather than in files.

To reduce duplication, ensure that you precede each sample with the necessary `import` statements and authentication credential definition, as shown next. 

**Note**: The use of pandas here is for demonstration purposes. The Visier Python Connector does not depend on pandas.
```python
import os
from visier.connector import VisierSession, make_auth
from visier.api import QueryApiClient
from examples import load_json, load_str
import pandas as pd

auth = make_auth()
```

### List Query
List data is granular, non-aggregated data from Visier objects like the `Employee` subject or the `Compensation_Payout` event. In this example, we define a snippet to get `Employee.Pay_Level` that you can add to a third-party resource that loads detailed data; for example, a Jupyter Notebook.
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
Aggregate queries execute queries using Visier metrics. A metric is a business question or concern that is quantifiable as a number. Visier metrics range from simple metrics like `employeeCount` to more complex metrics like `hrRecruitingBudgetedLaborCostPerFTE`. In this example, we define a query to aggregate `applicantCount` by `Application_Source` and `Applicant_Stage`.

With a `VisierSession` available, an aggregate query is executed functionally identically.
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

### SQL-Like Query
You can write SQL-like queries to define both list and aggregate queries.

#### SQL-Like List Query
In this example, we define a snippet to get the `EmployeeID`, `Union_Status`, `Direct_Manager.Gender`, `Direct_Manager.Vaccination_Status` where `isFemale` = `TRUE` and `isHighPerformer` = `TRUE` between January 1, 2020 and December 31, 2021.
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

#### SQL-Like Aggregate Query
In this example, we define a snippet to aggregate `employeeCount` by `Location_0`, `Gender`, `Union_Status`, and `Location_1` for 4 periods of 3 months each starting from April 1, 2020. In aggregate SQL-like queries, you can use `options` to eliminate cells with zero and null values. This reduces the size of the overall result set to only include rows whose metric value is more than 0.
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

## Data Model API
The Model API client makes calls to Visier's Data Model API.

To run the example below, add the following import statement to your program.
```python
from visier.api import ModelApiClient
```

In this example, we query for the metadata of selection concepts on the `Requisition` analytic object: `isRequisitionbyOtherIncomingReasons` and `isActiveRequisition`.
```python
    with VisierSession(auth) as session:
        model_client = ModelApiClient(session)

        concepts = model_client.get_selection_concepts("Requisition", ["isRequisitionbyOtherIncomingReasons", "isActiveRequisition"])
        print(concepts)
```

## Direct Data Intake API
The Direct Intake API allows users to load data whose structure already matches the target analytic object. To instantiate the Direct Data Intake API, follow the same pattern as the Data Query API and Data Model API.
First, import the appropriate API client: `from visier.api import DirectIntakeApiClient`

**Note**:
- The Direct Data Intake API requires that your source data is  cleansed, deduplicated, and transformed before sending the data to Visier. If any of these criteria are not met, the Direct Data Intake API is not suitable for loading data. You may instead send data to Visier through alternative methods, such as SFTP or data connectors.
- The Direct Data Intake API call sequence follows a transactional pattern. You first start a transaction, then make the required file uploads to the transaction, and finally commit the  transaction. If a transaction must be aborted, you can instead roll back the transaction instead of committing it.

:warning: The API caller must have sufficient capabilities in Visier to successfully call the Direct Data Intake API.

### Data Load Schema
To understand the required structure to load data into target objects, use the `schemas` endpoint. The `schemas` endpoint returns the data load schema, or staging schema, of a specified target object.
```python
schema = intake_client.get_object_schema("Employee_Exit")
```
The data load schema is distinct from the analytic schema retrieved through the Data Model API. The analytic schema defines an object's attributes, such as its display name and associated dimensions. The data load schema defines an object's mandatory and optional data columns, data type, and other schema details.

### File Upload
In this example, we load data for `Employee` and `Employee_Exit`.
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

### Other Uses
In addition to querying data, this connector provides a lower level, generic function for executing other public Visier APIs. The following example illustrates how this connector can determine all the plans defined on a plan model.
```python
def get_location_levels(context: SessionContext) -> Response:
    path = "/v1/data/model/plan-models/WorkforcePlanModel/plans"
    return context.session().get(url=context.mk_url(path))

with VisierSession(auth) as s:
    levels = s.execute(get_location_levels)
    print(levels.json())
```

## Installation
Add `visier-connector` as a dependency to your module or install `pip install -U visier-connector` directly.
