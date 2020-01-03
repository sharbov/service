#!/usr/bin/env bash

# set metrics arguments only when required
if [ $METRICS_ENABLED = 1 ]; then
  events_args=""
  metrics_args="--statsd-host=statsd:9125 --statsd-prefix=api"
else
  events_args="-E"
  metrics_args=""
fi

case $SERVICE_NAME in

  api)

    # === API entry point ===
    bash /service/entrypoints/wait-for-it.sh postgres:5432
    bash /service/entrypoints/wait-for-it.sh rabbitmq:5672

    gunicorn service.app:app \
     --name 'service' \
     --log-level=info \
     --bind 0.0.0.0:8000 \
     --reload \
     -k gevent --worker-connections 1001 --workers 1 \
     $metrics_args

    ;;

  cpu-worker)

    # === CPU worker entry point ===
    bash /service/entrypoints/wait-for-it.sh rabbitmq:5672

    celery worker \
      --app=service.app:celery_app \
      --loglevel=INFO \
      --hostname=cpu_worker@%h \
      --autoscale=8,1 \
      --concurrency=8 \
      -Q cpu \
      $events_args

  ;;

  io-worker)

    # === IO worker entry point ===
    bash /service/entrypoints/wait-for-it.sh rabbitmq:5672

    celery worker \
      --app=service.app:celery_app \
      --loglevel=INFO \
      --hostname=io_worker@%h \
      --concurrency=1000 \
      --pool=gevent \
      -Q io \
      $events_args

  ;;

  flower)

    # === Flower entry point ===
    bash /service/entrypoints/wait-for-it.sh rabbitmq:15672

    celery flower \
      --app=service.app:celery_app \
      --loglevel=INFO \
      --rabbitmq=pyamqp://admin:mypass@rabbitmq// \
      --rabbitmq_api=http://admin:mypass@rabbitmq:15672/api/ \
      --address=0.0.0.0 \
      --port=8000 \
      --max_tasks=10000 \
      -Q cpu,io

  ;;

  events-tracker)

    # === events-tracker entry point ===
    bash /service/entrypoints/wait-for-it.sh rabbitmq:5672
    bash /service/entrypoints/wait-for-it.sh statsd:9125

    celery -A service.app:celery_app events -c service.tracker.EventsTracker --frequency=2.0 --pidfile /tmp/celerybeat.pid

  ;;

esac