"""Definition and owner pointers, never copied field lists, values or constraints.

Update definition locations only after reviewing an accepted declaration change. The actual source
loader and validator own acceptance; documentation cells own the statements tested.
"""

DEFINITIONS = {
    ('backup_profiles', 'pbs-client'): ('backup/pbs-client.yaml', 'docs/reference/backup-profiles.md'),
    ('app_profiles', 'homeassistant-bound'): ('apps/homeassistant-bound.yaml', 'docs/reference/apps/homeassistant-bound.md'),
    ('app_profiles', 'homeassistant-custom'): ('apps/homeassistant-custom.yaml', 'docs/reference/apps/homeassistant-custom.md'),
    ('app_profiles', 'node_red-bound'): ('apps/node_red-bound.yaml', 'docs/reference/apps/node_red-bound.md'),
    ('app_profiles', 'node_red-custom'): ('apps/node_red-custom.yaml', 'docs/reference/apps/node_red-custom.md'),
    ('app_profiles', 'bitwarden'): ('apps/bitwarden.yaml', 'docs/reference/apps/bitwarden.md'),
    ('app_profiles', 'cloudbeaver'): ('apps/cloudbeaver.yaml', 'docs/reference/apps/cloudbeaver.md'),
    ('app_profiles', 'pihole-web'): ('apps/pihole-web.yaml', 'docs/reference/apps/pihole-web.md'),
    ('app_profiles', 'pihole'): ('apps/pihole.yaml', 'docs/reference/apps/pihole.md'),
    ('app_profiles', 'unbound'): ('apps/unbound.yaml', 'docs/reference/apps/unbound.md'),
    ('app_profiles', 'authentik'): ('apps/authentik.yaml', 'docs/reference/apps/authentik.md'),
    ('app_profiles', 'influxdb-web'): ('apps/influxdb-web.yaml', 'docs/reference/apps/influxdb-web.md'),
    ('app_profiles', 'influxdb'): ('apps/influxdb.yaml', 'docs/reference/apps/influxdb.md'),
    ('app_profiles', 'traefik'): ('apps/traefik.yaml', 'docs/reference/apps/traefik.md'),
    ('app_profiles', 'mariadb'): ('apps/mariadb.yaml', 'docs/reference/apps/mariadb.md'),
    ('app_profiles', 'zabbix'): ('apps/zabbix.yaml', 'docs/reference/apps/zabbix.md'),
    ('app_profiles', 'mqtt'): ('apps/mqtt.yaml', 'docs/reference/apps/mqtt.md'),
    ('app_profiles', 'mqtt_explorer'): ('apps/mqtt_explorer.yaml', 'docs/reference/apps/mqtt_explorer.md'),
    ('app_profiles', 'music_assistant-split'): ('apps/music_assistant-split.yaml', 'docs/reference/apps/music_assistant-split.md'),
    ('app_profiles', 'music_assistant'): ('apps/music_assistant.yaml', 'docs/reference/apps/music_assistant.md'),
    ('app_profiles', 'pegaprox'): ('apps/pegaprox.yaml', 'docs/reference/apps/pegaprox.md'),
    ('app_profiles', 'postgresql'): ('apps/postgresql.yaml', 'docs/reference/apps/postgresql.md'),
    ('app_profiles', 'zigbee2mqtt'): ('apps/zigbee2mqtt.yaml', 'docs/reference/apps/zigbee2mqtt.md'),
    ('app_profiles', 'winet'): ('apps/winet.yaml', 'docs/reference/apps/winet.md'),
    ('app_profiles', 'homeassistant'): ('apps/homeassistant.yaml', 'docs/reference/apps/homeassistant.md'),
    ('app_profiles', 'node_red'): ('apps/node_red.yaml', 'docs/reference/apps/node_red.md'),
    ('app_profiles', 'cloudbeaver-mariadb-admin'): ('apps/cloudbeaver-mariadb-admin.yaml', 'docs/reference/apps/cloudbeaver-mariadb-admin.md'),
    ('guest_templates', 'base'): ('templates/base.yaml', 'docs/reference/templates/base.md'),
    ('guest_templates', 'docker'): ('templates/docker.yaml', 'docs/reference/templates/docker.md'),
}

REGISTRATIONS = {
    'policies.tls': (),
    'policies.authentication': (),
    'policies.middlewares': (),
    'policies.transport': (),
    'bundles': (),
    'backup_profiles': ('pbs-client',),
    'software': ('pbs-client', 'docker', 'curl', 'network-tools', 'yaml-parser', 'mariadb-client', 'postgresql', 'mariadb', 'influxdb', 'homeassistant-custom-images', 'node_red-custom-images', 'bitwarden-images', 'cloudbeaver-images', 'pihole-images', 'unbound-images', 'authentik-images', 'traefik-images', 'zabbix-images', 'mqtt-images', 'mqtt_explorer-images', 'music_assistant-images', 'pegaprox-images', 'zigbee2mqtt-images', 'winet-images', 'homeassistant-upstream-images', 'node_red-upstream-images'),
    'runtime_profiles': ('container-host', 'homeassistant', 'node_red', 'bitwarden', 'cloudbeaver', 'pihole', 'unbound', 'authentik', 'traefik', 'zabbix', 'mqtt', 'mqtt_explorer', 'music_assistant', 'pegaprox', 'zigbee2mqtt', 'winet', 'homeassistant-mdns', 'native-postgresql', 'native-mariadb', 'native-influxdb'),
    'health_profiles': ('adapter-ready',),
    'authentication_profiles': ('cloudbeaver-oidc', 'node-red-retained-oidc', 'zabbix-saml'),
    'monitoring_profiles': ('linux-agent', 'docker-agent', 'postgresql-agent', 'mariadb-agent', 'influxdb-agent'),
    'assets': ('proxmox-backup-repository-key', 'postgresql-repository-key', 'mariadb-repository-key', 'influxdb-repository-key'),
    'policies.network': ('mqtt_backend_ingress', 'http_backend_egress', 'resolver_dns_udp_first', 'source_bound_package_image_provider_web_egress', 'resolver_dns_tcp_first', 'package_repository_web_egress', 'package_image_provider_web_egress'),
}

# Optional instance controls accepted even though the profile supplies no value.
MQTT_PROPERTIES = {
    'password_file': ('blueprints/component_foundations.py', 'validate',
                      'docs/reference/apps/mqtt.md', 'mqtt-password-file'),
}
