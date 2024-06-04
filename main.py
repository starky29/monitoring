import os, distro

#if distro.id() == ('ubuntu' or 'debian'):
#    os.system('sudo apt -y update && sudo apt -y install docker && sudo apt -y install docker-compose')
#else:
#    os.system('sudo dnf -y install docker && sudo dnf -y install docker-compose')
work_dir = '/opt/prometheus_stack'
prom_st = ['prometheus', 'grafana', 'alertmanager', 'blackbox']
if not os.path.isdir(work_dir):
    os.mkdir("/opt/prometheus_stack")
os.chdir('/opt/prometheus_stack')
for folder in prom_st:
    if not os.path.isdir(folder):
        os.mkdir(f"/opt/prometheus_stack/{folder}")

# создаем и заполняем общие настройки docker-compose
compose = open('docker-compose.yaml', 'w')
compose.write("version: '3.9'\n\n"
            "services:\n\n"
            "  prometheus:\n"
            "    image: prom/prometheus:latest\n"
            "    volumes:\n"
            "      - ./prometheus:/etc/prometheus/\n"
            "    container_name: prometheus\n"
            "    hostname: prometheus\n"
            "    command:\n"
            "      - --config.file=/etc/prometheus/prometheus.yml\n"
            "    ports:\n"
            "      - 9090:9090\n"
            "    restart: unless-stopped\n"
            "    networks:\n"
            "      - default\n\n"
            
            "  node-exporter:\n"
            "    image: prom/node-exporter\n"
            "    volumes:\n"
            "      - /proc:/host/proc:ro\n"
            "      - /sys:/host/sys:ro\n"
            "      - /:/rootfs:ro\n"
            "    container_name: exporter\n"
            "    hostname: exporter\n"
            "    command:\n"
            "      - --path.procfs=/host/proc\n"
            "      - --path.sysfs=/host/sys\n"
            "      - --collector.filesystem.ignored-mount-points\n"
            "      - ^/(sys|proc|dev|host|etc|rootfs/var/lib/docker/containers|rootfs/var/lib/docker/overlay2|rootfs/run/docker/netns|rootfs/var/lib/docker/aufs)($$|/)\n"
            "    ports:\n"
            "      - 9100:9100\n"
            "    restart: unless-stopped\n"
            "    networks:\n"
            "      - default\n\n"
            
            "  grafana:\n"
            "    image: grafana/grafana\n"
            "    user: root\n"
            "    depends_on:\n"
            "      - prometheus\n"
            "    ports:\n"
            "      - 3000:3000\n"
            "    volumes:\n"
            "      - ./grafana:/var/lib/grafana\n"
            "      - ./grafana/provisioning/:/etc/grafana/provisioning/\n"
            "    container_name: grafana\n"
            "    hostname: grafana\n"
            "    restart: unless-stopped\n"
            "    networks:\n"
            "      - default\n\n"
            
            #"alertmanager-bot:\n"
            #"  command:\n"
            #"    - --alertmanager.url=http://alertmanager:9093\n"
            #"    - --log.level=info\n"
            #"    - --store=bolt\n"
            #"    - --bolt.path=/data/bot.db\n"
            #"    - --telegram.admin=573454381\n"
            #"    - --telegram.token=5472129845:AAFTQRdujqIHgWHbbVtfYWQQvzvIN98KBqg\n"
            #"  image: metalmatze/alertmanager-bot:0.4.3\n"
            #"  user: root\n"
            #"  ports:\n"
            #"    - 8080:8080\n"
            #"  container_name: alertmanager-bot\n"
            #"  hostname: alertmanager-bot\n"
            #"  restart: unless-stopped\n"
            #"  volumes:\n"
            #"    - ./data:/data\n"
            #"  networks:\n"
            #"    - default\n\n"
            
            "  alertmanager:\n"
            "    image: prom/alertmanager:v0.21.0\n"
            "    user: root\n"
            "    ports:\n"
            "      - 127.0.0.1:9093:9093\n"
            "    volumes:\n"
            "      - ./alertmanager/:/etc/alertmanager/\n"
            "    container_name: alertmanager\n"
            "    hostname: alertmanager\n"
            "    restart: unless-stopped\n"
            "    command:\n"
            "      - '--config.file=/etc/alertmanager/config.yml'\n"
            "      - '--storage.path=/etc/alertmanager/data'\n"
            "    networks:\n"
            "      - default\n\n"
            
            "  blackbox:\n"
            "    image: prom/blackbox-exporter\n"
            "    container_name: blackbox\n"
            "    hostname: blackbox\n"
            "    ports:\n"
            "      - 9115:9115\n"
            "    restart: unless-stopped\n"
            "    command:\n"
            "      - '--config.file=/etc/blackbox/blackbox.yml'\n"
            "    volumes:\n"
            "      - ./blackbox:/etc/blackbox\n"
            "    networks:\n"
            "      - default\n"
            
            "networks:\n"
            "  default:\n"
            "    ipam:\n"
            "      driver: default\n"
            "      config:\n"
            "        - subnet: 172.28.0.0/24\n")
compose.close()

#создаем и заполняем конфиги сервисов
#prometeus
cfg_promet = open('prometheus/prometheus.yml', 'w')
cfg_promet.write("scrape_configs:\n"
                 "  - job_name: node\n"
                 "    scrape_interval: 5s\n"
                 "    static_configs:\n"
                 "    - targets: ['node-exporter:9100']\n"
                 "  - job_name: 'blackbox'\n"
                 "    metrics_path: /probe\n"
                 "    params:\n"
                 "      module: [http_2xx]\n"
                 "    static_configs:\n"
                 "      - targets:\n"
                 "        #- https://\n" #мониторинг сайта
                 "    relabel_configs:\n"
                 "      - source_labels: [__address__]\n"
                 "        target_label: __param_target\n"
                 "      - source_labels: [__param_target]\n"
                 "        target_label: instance\n"
                 "      - target_label: __address__\n"
                 "        replacement: blackbox:9115\n"
                 "rule_files:\n"
                 "  - 'alert.rules'\n"
                 "alerting:\n"
                 "  alertmanagers:\n"
                 "  - scheme: http\n"
                 "    static_configs:\n"
                 "    - targets:\n"
                 "      - 'alertmanager:9093'\n")
cfg_promet.close()
cfg_promet_rules = open('prometheus/alert.rules', 'w')
cfg_promet_rules.write("groups:\n"
                       "- name: test\n"
                       "  rules:\n"
                       "  - alert: PrometheusTargetMissing\n"
                       "    expr: up == 0\n"
                       "    for: 0m\n"
                       "    labels:\n"
                       "      severity: critical\n"
                       "    annotations:\n"
                       '      summary: "Prometheus target missing (instance {{ $labels.instance }})"\n'
                       '      description: "A Prometheus target has disappeared. An exporter might be crashed. VALUE = {{ $value }}  LABELS: {{ $labels }}"\n'
                       "  - alert: BlackboxSlowProbe\n"
                       "    expr: avg_over_time(probe_duration_seconds[1m]) > 5\n"
                       "    for: 1m\n"
                       "    labels:\n"
                       "      severity: warning\n"
                       "    annotations:\n"
                       "      summary: Blackbox slow probe (instance {{ $labels.instance }})\n"
                       '      description: "Blackbox probe took more than 1s to complete\\n  VALUE = {{ $value }}\\n  LABELS = {{ $labels }}"\n'
                       "  - alert: BlackboxProbeHttpFailure\n"
                       "    expr: probe_http_status_code <= 199 OR probe_http_status_code >= 400\n"
                       "    for: 0m\n"
                       "    labels:\n"
                       "      severity: critical\n"
                       "    annotations:\n"
                       "      summary: Blackbox probe HTTP failure (instance {{ $labels.instance }})\n"
                       '      description: "HTTP status code is not 200-399\\n  VALUE = {{ $value }}\\n  LABELS = {{ $labels }}"')
cfg_promet_rules.close()
#alertmanager оповещение
cfg_alert = open('alertmanager/config.yml', 'w')
cfg_alert.write("route:\n"
                "    receiver: 'alertmanager-bot'\n\n"
                "receivers:\n"
                "- name: 'alertmanager-bot'\n"
                "  webhook_configs:\n"
                "  - send_resolved: true\n"
                "    url: 'http://alertmanager-bot:8080'\n")

cfg_alert.close()

# мониторинг http blackbox
cfg_alert = open('blackbox/blackbox.yml', 'w')
cfg_alert.write("modules:\n"
                "  http_2xx:\n"
                "    prober: http\n"
                "    timeout: 5s\n"
                "    http:\n"
                '      valid_http_versions: ["HTTP/1.1", "HTTP/2.0"]\n'
                "      valid_status_codes: [200]\n"
                "      method: GET\n"
                "      no_follow_redirects: true\n"
                "      fail_if_ssl: false\n"
                "      fail_if_not_ssl: false\n"
                "      fail_if_body_matches_regexp:\n"
                '        - "Could not connect to database"\n'
                "      fail_if_body_not_matches_regexp:\n"
                '        - "Download the latest version here"\n'
                "      fail_if_header_matches: # Verifies that no cookies are set\n"
                "        - header: Set-Cookie\n"
                "          allow_missing: true\n"
                "          regexp: '.*'\n"
                "      fail_if_header_not_matches:\n"
                "        - header: Access-Control-Allow-Origin\n"
                "          regexp: '(\*|example\.com)'\n"
                "      tls_config:\n"
                "        insecure_skip_verify: false\n"
                '      preferred_ip_protocol: "ip4"\n'
                "      ip_protocol_fallback: false")
cfg_alert.close()
