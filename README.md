# About
Repo containing the project for Concordia's Data Systems for Software Engineers (SOEN-363) course.

## Team Members

| Name            | Student ID |
| --------------- | ---------- |
| Nathan Grenier  | 40250986   |
| Nathanial Hwong | 40243583   |

## Setting Environment Variables
Set these env variables before running any commands:

PostgreSQL:
- POSTGRES_DB
- POSTGRES_USER
- POSTGRES_PASSWORD

PG Admin:
- PGADMIN_DEFAULT_EMAIL
- PGADMIN_DEFAULT_PASSWORD

API: 
- RANDOMHOUSE_API_KEY

## Using Docker (PostgreSQL Container)
> You should [install docker](https://docs.docker.com/engine/install/) for you system before starting.

Both the Postgres instance and database management tool (pgAdmin) are configured in the `docker-compose.yml` file.

1. To run both services, use `docker compose up`.
    > You can run the container in "detached" mode by appending the `-d` flag to the command above.
2. Next, check that both services are running with `docker ps`.
3. Copy the "postgres" services docker id (ex: 1fc60e0e538d).
4. Inspect the details of the postgres container using `docker inspect {postgres id}`.
5. Search for the `IPAddress` attribute of the postgres database and keep note of it.
6. Open `http://localhost:5050/` to view the pgAdmin webpage.
7. Click on the "Add New Server" Quick Link in pgAdmin to add the postgres instance.
8. In the General tab: 
   - Give the postgres server a name.
    > ![](/static/pgAdmin-General.png)
9. In the Connection Tab: 
   - Enter the postgres container's ip address
   - Enter the same username as in the `.env` file (POSTGRES_USER) 
   - Enter the same password as in the `.env` file (POSTGRES_PASSWORD)
    > ![](/static/pgAdmin-Connection.png)

## Using plantUML

In order to render ER diagrams (chen's notation), you must use the [server version](https://github.com/qjebbs/vscode-plantuml?tab=readme-ov-file#use-plantuml-server-as-render) of plantUML.

### Setup
To pull the docker image, run:
```bash
docker run -d -p 8181:8080 --name plantuml -e BASE_URL=plantuml plantuml/plantuml-server:jetty
```

Add the following settings to your `setting.json` file in VsCode:
```json
  "plantuml.server": "http://localhost:8181/plantuml",
  "plantuml.render": "PlantUMLServer",
```

> Note: You can change the host's port (port before the ":") to whatever you'd like. Default for http is usually `80` or `8080` 

### Useful Commands

- Start the container: `docker start {name}`
- Stop the container: `docker stop {name}`
- List all running containers: `docker ps` 

### Exporting
To specify where the diagrams should be defined and exported, add the following to VsCode's `setting.json`:

```json
  "plantuml.diagramsRoot": "diagrams/src",
  "plantuml.exportOutDir": "diagrams/out",
```

## Python Venv

First, install virtualvenv using `pip install virtualenv`.

Now, you can create a venv to work in using `virtualenv --python 3.12.1 venv`

> Note: You need the specified version on python installed on your local computer to run the command above

### Working in the venv

In order to activate the venv to start working in it, use this command:

```bash
# Linux and Mac
source venv/bin/activate

# Windows
.\venv\Scripts\activate
```

To stop working in the venv, use the command: `deactivate`.

### Installing Project Dependencies

Use the following command while in the venv to install the project's dependencies:

```bash
pip install -r requirements.txt
```

### Setting the Jupyter Notebook's Kernel

To set the Jupyter Notebook's Kernel, click the following icon and select the venv you just made.

<img src="static/noterbook-kernel-picker.gif" width="600" />

## Code Formatting and Linting

I like using Ruff to format and lint my python code. This package is installed whenever you [install the project's dependencies](#installing-project-dependencies) and can be used with the following command:

```bash
ruff format .
```

If you want the file to format on save, you can install the VsCode Ruff extension and add these lines to VsCodes' `setting.json` file:

```json
{
  "notebook.formatOnSave.enabled": true,
  "notebook.codeActionsOnSave": {
    "notebook.source.organizeImports": "explicit"
  },
  "[python]": {
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": "explicit"
    },
    "editor.defaultFormatter": "charliermarsh.ruff"
  }
}
``` 