import requests
from env_vars import BEARER_TOKEN
from typing import Any, List, Dict


def get_prompt_response(text: str) -> Dict[str, Any]:
    """
    Query plugin with user's prompt
    """

    url = "http://0.0.0.0:8000/prompt"
    headers = {
        "Content-Type": "application/json",
        "accept": "application/json",
        "Authorization": f"Bearer {BEARER_TOKEN}",
    }
    data = {"prompt_query": {"query": text}, "source_id": "myvoyagerdbname"}

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        result = response.json()
        # process the result
        return result
    else:
        raise ValueError(f"Error: {response.status_code} : {response.content}")


def query_vector_database(query_prompt: str, filter: dict = None, top_k: int = 10) -> Dict[str, Any]:
    """
    Query vector database to retrieve chunk using query_prompt.
    """

    url = "http://0.0.0.0:8000/query"
    headers = {
        "Content-Type": "application/json",
        "accept": "application/json",
        "Authorization": f"Bearer {BEARER_TOKEN}",
    }

    if not filter:
        filter = {
            "property_ids": []
        }

    data = {"queries": [
        {"query": query_prompt, "top_k": top_k, "filter": filter, "source_id": "myvoyagerdbname"}]}

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        result = response.json()
        # process the result
        return result
    else:
        raise ValueError(f"Error: {response.status_code} : {response.content}")


def get_embedding(text: str) -> List[float]:
    """
    Get embedding from plugin configured EMBEDDING_MODEL
    """

    url = "http://0.0.0.0:8000/embedding"
    headers = {
        "Content-Type": "application/json",
        "accept": "application/json",
        "Authorization": f"Bearer {BEARER_TOKEN}",
    }
    data = {"text": text}

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        result = response.json()
        # process the result
        return result
    else:
        raise ValueError(f"Error: {response.status_code} : {response.content}")


def scrape_voyager_to_vector_database(vdb_server: str, vdb_database: str, vdb_user: str, vdb_password: str):
    import pyodbc

    print(
        f"Connecting to Voyager DB...  [server={vdb_server},database={vdb_database},uid={vdb_user},pwd=<env:vdb_password>]")
    conn = pyodbc.connect(
        DRIVER='{ODBC Driver 18 for SQL Server}',
        encrypt='no',
        trust_server_certificate='yes',
        server=vdb_server,
        database=vdb_database,
        uid=vdb_user,
        pwd=vdb_password
    )
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
    ,1,1,'') AS story,
    u.HPROPERTY AS property_ids
    FROM tenant t
    INNER JOIN tenant_history th on th.hTent = t.HMYPERSON
    INNER JOIN unit u on u.hmy = th.hUnit
    WHERE NULLIF(t.sfirstname,'') IS NOT NULL AND NULLIF(t.slastname,'') IS NOT NULL AND NULLIF(th.sEvent,'') IS NOT NULL
    group by t.HMYPERSON, u.HPROPERTY
    """

    print("Querying db...")
    cur.execute(query)
    all_rows = cur.fetchall()
    for i in range(len(all_rows)):
        row = all_rows[i]
        print(f"{len(all_rows)}/{i} - {str(row[0])}")
        upsert_text_to_vector_database(str(row[0]), row[1], [
                                  int(p) for p in str(row[2]).split(',')])


def upsert_text_to_vector_database(id: str, text: str, property_ids: List[int] = None):
    """
    Upload one piece of text to the database.
    """
    url = "http://0.0.0.0:8000/upsert"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + BEARER_TOKEN,
    }

    if property_ids:
        metadata = {
            "json_data": {
                "property_ids": property_ids
            }
        }
    else:
        metadata = {}

    data = {
        "documents": [{
            "id": id,
            "text": text,
            "metadata": metadata,
            "source_id": "myvoyagerdbname"
        }]
    }
    response = requests.post(url, json=data, headers=headers, timeout=600)

    if response.status_code == 200:
        print("uploaded successfully.")
    else:
        print(f"Error: {response.status_code} {response.content}")


def upsert_files_to_vector_database(directory: str, property_ids: List[int] = None):
    """
    Upload all files under a directory to the vector database.
    """

    url = "http://0.0.0.0:8000/upsert-file"
    headers = {"Authorization": "Bearer " + BEARER_TOKEN}
    files = []

    if property_ids:
        metadata = {
            "json_data": {
                "property_ids": property_ids
            }
        }
        data = {
            "documents": [{
                "id": id,
                "text": text,
                "metadata": metadata,
                "source_id": "myvoyagerdbname"
            }]
        }

    for filename in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, filename)):
            file_path = os.path.join(directory, filename)
            with open(file_path, "rb") as f:
                file_content = f.read()
                files.append(("file", (filename, file_content, "text/plain")))
            response = requests.post(url,
                                     headers=headers,
                                     data=data,
                                     files=files,
                                     timeout=600)
            if response.status_code == 200:
                print(filename + " uploaded successfully.")
            else:
                print(
                    f"Error: {response.status_code} {response.content} for uploading "
                    + filename)


def print_usage():
    print("""
Usage:
  python3 tools/tools.py <option>

Options:
    prompt
    scrape_voyager_db
    get_embedding
    query_vector_db
    upsert_to_vector_db
    upsert_files_to_vector_db
""")


if __name__ == "__main__":
    import sys
    import os

    if len(sys.argv) == 1 or not sys.argv[1]:
        print_usage()

    elif sys.argv[1] == "prompt":
        if len(sys.argv) == 3:
            text = sys.argv[2]
        else:
            text = input("Enter your prompt: ")

        print(get_prompt_response(text=text))

    elif sys.argv[1] == "query_vector_db":
        query_prompt = input("Enter query prompt: ")
        filter = input("Enter filter (default none): ")
        top_k = input("Enter top_k (default 10): ")
        if not top_k:
            top_k = 10
        print(query_vector_database(
            query_prompt=query_prompt, filter=filter, top_k=top_k))

    elif sys.argv[1] == "scrape_voyager_db":
        server = os.environ.get("vdb_server")
        if not server:
            server = input("Voyager DB Server:")
        database = os.environ.get("vdb_database")
        if not database:
            database = input("Voyager DB Name:")
        user = os.environ.get("vdb_user")
        if not user:
            user = input("Voyager DB User:")
        password = os.environ.get("vdb_password")
        if not password:
            password = input("Voyager DB Password:")
        scrape_voyager_to_vector_database(
            vdb_server=server, vdb_database=database, vdb_user=user, vdb_password=password)

    elif sys.argv[1] == "get_embedding":
        if len(sys.argv) == 3:
            text = sys.argv[2]
        else:
            text = input("Enter text to generate embedding for: ")

        print(get_embedding(text=text))

    elif sys.argv[1] == "upsert":
        if len(sys.argv) >= 3:
            id = sys.argv[2]
            text = sys.argv[3]
            property_ids = []
            if len(sys.argv) == 5:
                property_ids = [int(x.strip('[]'))
                                for x in sys.argv[4].split(",")]
        else:
            id = input("Enter id: ")
            text = input("Text: ")
            property_ids = input("Property Ids CSV (default none): ")
        
        upsert_text_to_vector_database(
            id=id, text=text, property_ids=property_ids)

    elif sys.argv[1] == "upsert_files":
        if len(sys.argv) >= 2:
            directory = sys.argv[2]
            property_ids = []
            if len(sys.argv) == 3:
                property_ids = [int(x.strip('[]'))
                                for x in sys.argv[3].split(",")]
        else:
            directory = input("Enter directory: ")
            property_ids = input("Property Ids CSV (default none): ")

        upsert_files_to_vector_database(
            directory=directory, property_ids=property_ids)

    else:
        print_usage()
