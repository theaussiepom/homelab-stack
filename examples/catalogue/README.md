# Complete profile compositions

These are synthetic source-only compositions, not an implicit installation layout. Each canonical YAML body is maintained once and passes the real library resolver and packet lowerer. Existing resources/credentials are references, not supplied data or deployment authority. Retained entries require an already HomeLab-managed installation.

| Profile | Complete source | App instance |
| --- | --- | --- |
| [homeassistant](../../docs/reference/apps/homeassistant.md) | [existing-automation.yaml](existing-automation.yaml) | `homeassistant` |
| [node_red](../../docs/reference/apps/node_red.md) | [existing-automation.yaml](existing-automation.yaml) | `node_red` |
| [bitwarden](../../docs/reference/apps/bitwarden.md) | [vault.yaml](vault.yaml) | `vault` |
| [cloudbeaver](../../docs/reference/apps/cloudbeaver.md) | [database-guis.yaml](database-guis.yaml) | `cloud` |
| [pihole](../../docs/reference/apps/pihole.md) | [site.yaml](local-dns/site.yaml) | `filtering` |
| [unbound](../../docs/reference/apps/unbound.md) | [starter](../../site.example.yaml) | `recursive_dns` |
| [authentik](../../docs/reference/apps/authentik.md) | [identity-monitoring.yaml](identity-monitoring.yaml) | `identity` |
| [influxdb](../../docs/reference/apps/influxdb.md) | [native-databases.yaml](native-databases.yaml) | `influxdb` |
| [traefik](../../docs/reference/apps/traefik.md) | [edge-management.yaml](edge-management.yaml) | `edge` |
| [mariadb](../../docs/reference/apps/mariadb.md) | [native-databases.yaml](native-databases.yaml) | `mariadb` |
| [zabbix](../../docs/reference/apps/zabbix.md) | [identity-monitoring.yaml](identity-monitoring.yaml) | `monitoring` |
| [mqtt](../../docs/reference/apps/mqtt.md) | [messaging-radio.yaml](messaging-radio.yaml) | `broker` |
| [mqtt_explorer](../../docs/reference/apps/mqtt_explorer.md) | [messaging-radio.yaml](messaging-radio.yaml) | `browser` |
| [music_assistant](../../docs/reference/apps/music_assistant.md) | [music.yaml](music.yaml) | `music` |
| [pegaprox](../../docs/reference/apps/pegaprox.md) | [edge-management.yaml](edge-management.yaml) | `manager` |
| [postgresql](../../docs/reference/apps/postgresql.md) | [native-databases.yaml](native-databases.yaml) | `postgresql` |
| [zigbee2mqtt](../../docs/reference/apps/zigbee2mqtt.md) | [messaging-radio.yaml](messaging-radio.yaml) | `radio` |
| [winet](../../docs/reference/apps/winet.md) | [messaging-radio.yaml](messaging-radio.yaml) | `telemetry` |
| [homeassistant-public](../../docs/reference/apps/homeassistant-public.md) | [new-automation.yaml](new-automation.yaml) | `homeassistant` |
| [node_red-public](../../docs/reference/apps/node_red-public.md) | [new-automation.yaml](new-automation.yaml) | `node_red` |
| [cloudbeaver-mariadb-admin](../../docs/reference/apps/cloudbeaver-mariadb-admin.md) | [database-guis.yaml](database-guis.yaml) | `administration` |

For a supported new instance, the public automation, no-bind Unbound, new database GUI/workspace and native creation-policy sources use `fresh`. Keep that policy for later owned deployments. The other practical sources deliberately show retained prerequisites; they are not import or new-data commissioning procedures.

Start with [the source environment](../../docs/guides/first-configuration.md) and select one actual file with `compile.py --check`; validation never runs its native actions. Each profile page explains the selected fields, first-use prerequisites, later deployment effects and refusals.
