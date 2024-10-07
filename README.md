# About
Collection of Assignments for Concordia's SOEN 363 Data Systems for Software Engineers

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