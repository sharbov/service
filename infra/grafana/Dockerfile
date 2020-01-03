FROM grafana/grafana
RUN grafana-cli plugins install grafana-piechart-panel
ADD provisioning /etc/grafana/provisioning
ADD dashboards /var/lib/grafana/dashboards
HEALTHCHECK CMD wget --spider http://localhost:3000/api/health