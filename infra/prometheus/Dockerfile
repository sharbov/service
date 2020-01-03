FROM prom/prometheus
ADD prometheus.yml /etc/prometheus/prometheus.yml
HEALTHCHECK CMD wget --spider http://localhost:9090/-/healthy