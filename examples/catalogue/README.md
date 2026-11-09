# Complete profile compositions

These complete example configurations use invented inputs. You can check them offline and generate deployment files with the selected framework. Each YAML example is maintained in one place. References to existing resources and credentials do not supply their data or grant permission to deploy. Entries marked retained require an existing HomeLab-managed installation; the examples do not prescribe one fixed installation layout.

| Profile | Complete source | App instance |
| --- | --- | --- |
| [homeassistant](../../docs/reference/apps/homeassistant.md) | [existing-automation.yaml](existing-automation.yaml) | `homeassistant` |
| [homeassistant-bound](../../docs/reference/apps/homeassistant-bound.md) | [existing-automation-bound.yaml](existing-automation-bound.yaml) | `homeassistant` |
| [node_red](../../docs/reference/apps/node_red.md) | [existing-automation.yaml](existing-automation.yaml) | `node_red` |
| [node_red-bound](../../docs/reference/apps/node_red-bound.md) | [existing-automation-bound.yaml](existing-automation-bound.yaml) | `node_red` |
| [bitwarden](../../docs/reference/apps/bitwarden.md) | [vault.yaml](vault.yaml) | `vault` |
| [cloudbeaver](../../docs/reference/apps/cloudbeaver.md) | [database-guis.yaml](database-guis.yaml) | `cloud` |
| [pihole](../../docs/reference/apps/pihole.md) | [site.yaml](local-dns/site.yaml) | `filtering` |
| [unbound](../../docs/reference/apps/unbound.md) | [starter](../../site.example.yaml) | `recursive_dns` |
| [authentik](../../docs/reference/apps/authentik.md) | [identity-monitoring.yaml](identity-monitoring.yaml) | `identity` |
| [influxdb](../../docs/reference/apps/influxdb.md) | [native-databases.yaml](native-databases.yaml) | `influxdb` |
| [influxdb-web](../../docs/reference/apps/influxdb-web.md) | [native-databases-web.yaml](native-databases-web.yaml) | `influxdb` |
| [traefik](../../docs/reference/apps/traefik.md) | [edge-management.yaml](edge-management.yaml) | `edge` |
| [mariadb](../../docs/reference/apps/mariadb.md) | [native-databases.yaml](native-databases.yaml) | `mariadb` |
| [zabbix](../../docs/reference/apps/zabbix.md) | [identity-monitoring.yaml](identity-monitoring.yaml) | `monitoring` |
| [mqtt](../../docs/reference/apps/mqtt.md) | [messaging-radio.yaml](messaging-radio.yaml) | `broker` |
| [mqtt_explorer](../../docs/reference/apps/mqtt_explorer.md) | [messaging-radio.yaml](messaging-radio.yaml) | `browser` |
| [music_assistant](../../docs/reference/apps/music_assistant.md) | [music.yaml](music.yaml) | `music` |
| [music_assistant-split](../../docs/reference/apps/music_assistant-split.md) | [music-split.yaml](music-split.yaml) | `music` |
| [pegaprox](../../docs/reference/apps/pegaprox.md) | [edge-management.yaml](edge-management.yaml) | `manager` |
| [postgresql](../../docs/reference/apps/postgresql.md) | [native-databases.yaml](native-databases.yaml) | `postgresql` |
| [zigbee2mqtt](../../docs/reference/apps/zigbee2mqtt.md) | [messaging-radio.yaml](messaging-radio.yaml) | `radio` |
| [winet](../../docs/reference/apps/winet.md) | [messaging-radio.yaml](messaging-radio.yaml) | `telemetry` |
| [homeassistant-public](../../docs/reference/apps/homeassistant-public.md) | [new-automation.yaml](new-automation.yaml) | `homeassistant` |
| [node_red-public](../../docs/reference/apps/node_red-public.md) | [new-automation.yaml](new-automation.yaml) | `node_red` |
| [cloudbeaver-mariadb-admin](../../docs/reference/apps/cloudbeaver-mariadb-admin.md) | [database-guis.yaml](database-guis.yaml) | `administration` |

The public automation examples, Unbound without a storage mount, new database GUI workspaces and supported native database examples use `fresh` to permit creation of a new instance. Keep that policy for later deployments to the same HomeLab-managed instance. The other examples require existing HomeLab-managed resources. They cannot import another installation or prepare new application data.

Start with [the source environment](../../docs/guides/first-configuration.md) and select one actual file with `compile.py --check`; validation never runs its native actions. Each profile page explains the selected fields, first-use prerequisites, later deployment effects and refusals.
