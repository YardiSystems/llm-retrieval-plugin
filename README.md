# Setup
## Python Setup
- Ensure python3.10 is installed
    ```
    sudo apt-get install python3.10 python3-pip python3-distutils
    ```

## VSCODE Setup
- Get source code
    ```
    git clone https://github.com/YardiSystems/llm-retrieval-plugin.git
    cd llm-retrieval-plugin
    ```

- Install Python Poetry
    ```
    pip3 install poetry
    ```

- Setup Python Virtual Environment with poetry
    ```
    poetry shell
    ```

- Launch Visual Studio Code
    ```
    code .
    ```

- Set VSCode Python Interpreter to Venv Python
    1. Open any python file in the left file window in vscode
    2. On the bottom right of the vscode window, click the python version and select the one marked ('.venv': Poetry)
    3. Open a terminal in vscode by pressing CTRL + `

- Install dependencies through poetry
    ```
    poetry install
    ```

- Create a .vscode/launch.json file for debugging
    ```
    {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Run llm plugin",
                "type": "python",
                "request": "launch",
                "cwd": "${workspaceFolder}",
                "module": "uvicorn",
                "justMyCode": false,
                "args": [
                    "server.main:app",
                    "--host",
                    "0.0.0.0",
                    "--port",
                    "8000",
                ],
                "env": {
                    // Use the following if you get SSL error messages from the plugin.
                    // Copy the "tools/ysifwcert01-ca.crt" file to /usr/local/share/ca-certificates
                    // Run chmod +644 /usr/local/share/ca-certificates/*.crt
                    // Run update-ca-certificates
                    // Uncomment the following line
                    // "REQUESTS_CA_BUNDLE":"/etc/ssl/certs/ca-certificates.crt"
                }
            },
            {
                "name": "Python: Current File",
                "type": "python",
                "request": "launch",
                "program": "${file}",
                "console": "integratedTerminal",
                "justMyCode": true
            }
        ]
    }
    ```

- Configure environment variables
    - Environment variables set in the env_vars.py file will be applied if not already set in your environment.
        #### General Environment Variables (see README-PLUGIN.md for full list)

        The plugin requires the following environment variables to work:

        | Name             | Required | Description                                                                                                                                                                                                                                                   |
        | ---------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
        | `DATASTORE`      | Yes      | This specifies the vector database provider you want to use to store and query embeddings. You can choose from `elasticsearch`, `chroma`, `pinecone`, `weaviate`, `zilliz`, `milvus`, `qdrant`, `redis`, `azuresearch`, `supabase`, `postgres`, `analyticdb`. |
        | `BEARER_TOKEN`   | Yes      | This is a secret token that you need to authenticate your requests to the API. You can generate one using any tool or method you prefer, such as [jwt.io](https://jwt.io/).
        | `OPENAI_API_KEY` | Yes      | This is your OpenAI API key that you need to generate embeddings using the `text-embedding-ada-002` model. You can get an API key by creating an account on [OpenAI](https://openai.com/). You should set this in your shell on startup instead of here by using ~/.bashrc or add it to the .vscode/launch.json ENV array which is configured in the .gitignore file to prevent leaking it to source control.
        | `EMBEDDING_MODEL`| No       | This chooses the embedding model used. It defaults to OpenAI's "text-embedding-ada-002" if not set, but supports any HuggingFace.co sentence-transformer models, like "all-MiniLM-L6-v2".
        | `MILVUS_COLLECTION`| No       | If using Milvus this will choose the name of the collection that gets created. It defaults to "c_<GUID>", but it is suggested to set it to something static so subsequent runs of the engine use the same uploaded data.

<br />
<br />

# Running

## Start Milvus
```
docker-compose -f tools/docker-compose-milvus.yml up -d --wait
```


## Start the plugin
```
# F5 to run in debugger or ...

poetry run start
```


## Add data to Vector DB
```
### UPSERT TEXT
python3 tools/tools.py upsert


### UPSERT FILE CONTENTS OF DIRECTORY
python3 tools/tools.py upsert_files


### RUN VOYAGER DB TENANT HISTORY SCRAPER SCRIPT
# install mssql plugin (only need once)
poetry install -E mssql

# [optional] set voyager db connection details before running to avoid prompting
export vdb_server=<voyager db server>
export vdb_database=<voyager db database name>
export vdb_user=<voyager db login user name>
export vdb_password=<voyager db login user password>

python3 tools/tools.py scrape_voyager_db
```


## Get Vector DB results from text
```
python3 tools/tools.py query_vector_db
```


## Get Embedding for text
```
python3 tools/tools.py get_embedding
```


## Ask LLM using Voyager data
```
python3 tools/tools.py ask
```