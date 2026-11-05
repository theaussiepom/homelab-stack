# Library reference

[Documentation index](../README.md)

Choose a profile by its supported lifecycle and requirements, not only its product name. Each page lists roles, listeners, storage, inputs, conditional properties and resource policy.

| Profile | Application | Adapter / variant |
| --- | --- | --- |
| [homeassistant](apps/homeassistant.md) | Home Assistant | `homeassistant` |
| [node_red](apps/node_red.md) | Node-RED | `node_red` |
| [bitwarden](apps/bitwarden.md) | Bitwarden | `bitwarden` |
| [cloudbeaver](apps/cloudbeaver.md) | CloudBeaver | `cloudbeaver` |
| [pihole](apps/pihole.md) | Pi-hole | `pihole` |
| [unbound](apps/unbound.md) | Unbound | `unbound` |
| [authentik](apps/authentik.md) | Authentik | `authentik` |
| [influxdb](apps/influxdb.md) | InfluxDB | `influxdb` |
| [traefik](apps/traefik.md) | Traefik | `traefik` |
| [mariadb](apps/mariadb.md) | MariaDB | `mariadb` |
| [zabbix](apps/zabbix.md) | Zabbix | `zabbix` |
| [mqtt](apps/mqtt.md) | MQTT | `mqtt` |
| [mqtt_explorer](apps/mqtt_explorer.md) | MQTT Explorer | `mqtt_explorer` |
| [music_assistant](apps/music_assistant.md) | Music Assistant | `music_assistant` |
| [pegaprox](apps/pegaprox.md) | PegaProx | `pegaprox` |
| [postgresql](apps/postgresql.md) | PostgreSQL | `postgresql` |
| [zigbee2mqtt](apps/zigbee2mqtt.md) | Zigbee2MQTT | `zigbee2mqtt` |
| [winet](apps/winet.md) | WiNet | `winet` |
| [homeassistant-public](apps/homeassistant-public.md) | Home Assistant | `homeassistant` |
| [node_red-public](apps/node_red-public.md) | Node-RED | `node_red` |
| [cloudbeaver-mariadb-admin](apps/cloudbeaver-mariadb-admin.md) | CloudBeaver | `cloudbeaver` |

## Shared declarations

- [Guest templates](templates.md): resource/startup/security defaults and partial overrides.
- [Software and runtime](software-and-runtime.md): images, packages, process security, budgets, health and monitoring.
- [Composition](../guides/compose-a-site.md): where site allocations and instance identity belong.
- [Examples](../examples/README.md): complete maintained sources and their tested boundaries.

The library index is [stack.json](../../stack.json); image versions/policies are [images.json](../../images.json). There is no implicit guest set or unselected dependency.

Maintainers: use the [profile documentation template](../templates/application-profile.md) and [contributor workflow](../contributing.md). Every registered profile has a concrete, tested [complete composition](../../examples/catalogue/README.md).
