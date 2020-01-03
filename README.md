# Python Backend Service Example

### Features

 * Interactive API documentation (OpenAPI).
 * Monitoring dashboard for background workers.
 * Full Docker integration (Docker based).
 * Docker Compose integration for local development.
 * Python client generation.
 * Unittests & integration tests included.

### Service Tech Stack

 * Flask + Connexion for the service API.
 * Gunicorn + Gevent for the HTTP Server.
 * Flask-SQLalchemy + Postgres for the service database .
 * Celery + Rabbitmq for the service workers.
 * Flower for workers monitoring.
 * Traefik as a reverse proxy.

### Dev & Build Tech Stack

 * Docker build environment.
 * Build process managed by a Makefile.
 * Static-code-analysis using Flake8 & Pylint
 * Code formatting using Black.
 * Service unit-tests & integration tests using Nose2.
    * Coverage reports.
    * JUnit XML tests reports.
    * Running tests in parallel.
    * Docker env management using docker-test-tools.
 * Python client generation using swagger-code-gen project.

### Makeflie Actions

To view the Makefile options run `make help`

|Command         |Description                                        |
|:---------------|:--------------------------------------------------|
|make static     | Run static code analysis                          |
|make format     | Run auto code formatting                          |
|make unittests  | Run the unittests & generate reports              |
|make image      | Build the service image                           |
|make up         | Run the service stack using docker-compose        |
|make down       | Stop the service stack using docker-compose       |
|make integration| Run the integration tests                         |
|make clean      | Clean generated files                             |
|make help       | Show makefile actions                             |

### Dashboard URLs

|Name              |Service|URL                                      |
|------------------|-------|-----------------------------------------|
|API documentation |OpenAPI|http://localhost/service/api/v1/ui/#/    |
|Workers           |Flower |http://monitor.localhost/?refresh=1      |
|Tracing           |Jaeger |http://tracer.localhost/                 |
|Edge Router       |Traefik|http://localhost:8080/dashboard/#/       |
|Metrics           |Grafana|http://grafana.localhost/                |
|Logs              |Kibana |http://kibana.localhost/                 |
