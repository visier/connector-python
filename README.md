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

### Detail query
This is an example of a snippet that may be added to e.g. a Jupyter Notebook that loads detailed data. Detailed data is essentially granular, i.e. non-aggregated, data from Visier entities, e.g. Subjects such as `Employee` or Events such as `Compensation_Payout`.
```python
import os
from visier.connector import Authentication
from visier.connector import VisierSession
import pandas as pd

auth = Authentication(
    username = os.getenv("SOME_USERNAME"),
    password = os.getenv("SOME_PASSWORD"),
    host = os.getenv("SOME_HOST"),
    api_key = os.getenv("SOME_APIKEY"))

with VisierSession(auth) as s:
    list_result = s.execute("""
        SELECT 
            EmployeeID, 
            Union_Status, 
            Direct_Manager.Gender AS "DMG"
        FROM Employee
        WHERE
            isFemale = TRUE AND
            isHighPerformer = TRUE AND
            effectiveInstant BETWEEN date("2020-01-01") AND date("2021-12-31")
    """)

    df_list = pd.DataFrame.from_records(data=list_result.rows(), columns=list_result.header)
    # Now that the data is in a Pandas Data Frame, do something with it, or just...
    print(df_list.head)
```

### Aggregate query
Aggregate queries, in contrast, executes queries around Visier's predefined Metrics. A Metric is an arbitrarily complex calculation that targets a specific quantifiable question or scenario. They range from very simple like `employeeCount` to more complex ones like `hrRecruitingBudgetedLaborCostPerFTE`. 

With a `VisierSession` available, an aggregate query is executed functionally identically:
```python
    aggregate_result = s.execute("""
        SELECT 
            employeeCount(),
            level(Location, "Location_0"),
            level(Gender, "Gender"),
            level(Union_Status, "Union_Status"),
            period(3, Month) AS Time,
            level(Location, "Location_1")
        FROM Employee 
        WHERE 
            effectiveInstant IN intervalFrom(date("2020-04-01"), 2)
    """)
    df_aggregate = pd.DataFrame.from_records(data=aggregate_result.rows(), columns=aggregate_result.header
```

## Installation
Add `visier-connector` as a dependency or install directly e.g. in a virtual environment: `pip install -U visier-connector`