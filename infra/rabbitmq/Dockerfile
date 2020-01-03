FROM rabbitmq:3-management
RUN rabbitmq-plugins enable rabbitmq_prometheus
HEALTHCHECK CMD rabbitmq-diagnostics -q check_running