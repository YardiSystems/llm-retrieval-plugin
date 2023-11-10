import os
import pyodbc
import requests
import sys

from env_vars import BEARER_TOKEN

def upsert(id: str, content: str):
    """
    Upload one piece of text to the database.
    """
    url = "http://0.0.0.0:8000/upsert"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + BEARER_TOKEN,
    }

    data = {
        "documents": [{
            "id": id,
            "text": content,
        }]
    }
    response = requests.post(url, json=data, headers=headers, timeout=600)

    if response.status_code == 200:
        print("uploaded successfully.")
    else:
        print(f"Error: {response.status_code} {response.content}")


if __name__ == "__main__":

    print("Connectiong to db...")
    conn = pyodbc.connect(
        DRIVER='{ODBC Driver 18 for SQL Server}'
        ,encrypt='no'
        ,trust_server_certificate='yes'
        ,server=os.environ.get("vdb_server") or ""
        ,database=os.environ.get("vdb_database") or ""
        ,uid=os.environ.get("vdb_user") or ""
        ,pwd=os.environ.get("vdb_password") or "")
    cur = conn.cursor()

    query = """
    SELECT 
    LTRIM(RTRIM('tenant_' + CAST(t.HMYPERSON AS varchar))) AS id,
    STUFF((
        SELECT ' The Tenant ' + t1.sfirstname + ' ' + t1.slastname
        + ' performed ' + CAST(th1.sEvent AS VARCHAR(MAX))
        + CASE WHEN th1.hUnit IS NOT NULL THEN ' in unit ' + LTRIM(RTRIM(u1.scode)) ELSE '' END
        + CASE WHEN th1.hUnit IS NOT NULL THEN ' in property ' + LTRIM(RTRIM(p1.saddr1)) + ' (' + LTRIM(RTRIM(p1.SCODE)) +')' ELSE '' END
        + CASE WHEN th1.cRent IS NOT NULL THEN ' with the rent amount of ' + CAST(ISNULL(th1.cRent,0) AS VARCHAR) ELSE '' END
        + CASE WHEN th1.cDeposit0 IS NOT NULL THEN ' with the deposit amount of ' + CAST(ISNULL(th1.cDeposit0,0) AS VARCHAR) ELSE '' END
        + CASE WHEN th1.dtDate IS NOT NULL THEN ' on the date ' + CAST(CONVERT(DATE, th1.dtDate) AS varchar) ELSE '' END
        + '.'
        FROM tenant t1
        inner join tenant_history th1 on th1.hTent = t1.HMYPERSON
        left outer join unit u1 on u1.hmy = th1.hUnit
        left outer join property p1 on p1.hmy = u1.HPROPERTY
        where t1.HMYPERSON = t.HMYPERSON AND NULLIF(th1.sevent,'') IS NOT NULL
        FOR XML PATH(''),TYPE).value('(./text())[1]','VARCHAR(MAX)')
    ,1,1,'') AS story
    FROM tenant t
    INNER JOIN tenant_history th on th.hTent = t.HMYPERSON
    WHERE NULLIF(t.sfirstname,'') IS NOT NULL AND NULLIF(t.slastname,'') IS NOT NULL AND NULLIF(th.sEvent,'') IS NOT NULL
    group by t.HMYPERSON
    """

    print("Querying db...")
    cur.execute(query)
    all_rows = cur.fetchall()
    for i in range(len(all_rows)):
        row = all_rows[i]
        print(f"{len(all_rows)}/{i} - {str(row[0])}")
        upsert(str(row[0]), row[1])

