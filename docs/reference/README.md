# Choose an application profile

[Documentation index](../README.md) · [Complete example catalogue](../../examples/catalogue/README.md)

A selection ID names a reusable application recipe, not a complete installed service. For your first configuration, [Design your homelab](../guides/design-your-homelab.md) connects these choices to your actual host facts and an editable complete source. Open a profile's page for required bindings, first-install prerequisites, placement limits and ordinary update behavior. [Templates](templates.md) supply guest defaults without choosing an app bundle.

## Start with the intended outcome

| Outcome | Profiles and important choice |
| --- | --- |
| Resolve and filter DNS | [Unbound](apps/unbound.md) can start from empty and publishes guest-loopback DNS only. [Pi-hole](apps/pihole.md) needs prepared configuration and its selected upstream binding. The [complete DNS walkthrough](../examples/local-dns.md) requires an existing matching HomeLab-managed guest and apps; it cannot install new LAN DNS services. |
| Home automation | [Home Assistant public](apps/homeassistant-public.md) and [Node-RED public](apps/node_red-public.md) select public images and can create a new configuration directory without adopting an existing one. The [Home Assistant](apps/homeassistant.md) and [Node-RED](apps/node_red.md) retained variants have different archive and authentication requirements. |
| Messaging, radio and telemetry | [MQTT](apps/mqtt.md) owns the prepared broker; [MQTT Explorer](apps/mqtt_explorer.md) is a separately selected authenticated browser. [Zigbee2MQTT](apps/zigbee2mqtt.md) and [WiNet](apps/winet.md) need their own hardware or network inputs and a broker connection. |
| Databases and administration | [PostgreSQL](apps/postgresql.md), [MariaDB](apps/mariadb.md) and [InfluxDB](apps/influxdb.md) are native profiles. [CloudBeaver](apps/cloudbeaver.md) and its [MariaDB-admin variant](apps/cloudbeaver-mariadb-admin.md) differ in administrator capability; a connection value alone does not grant it. |
| Identity, edge and monitoring | [Authentik](apps/authentik.md), [Traefik](apps/traefik.md) and [Zabbix](apps/zabbix.md) own distinct services. Selecting one does not automatically publish or enroll every app. |
| Other services | [Bitwarden](apps/bitwarden.md), [Music Assistant](apps/music_assistant.md) and [PegaProx](apps/pegaprox.md) each require specific existing files, credentials or companion services; their profile pages explain what must already be prepared. |

## Complete registered catalogue

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

- [Guest templates](templates.md): exact [base](templates/base.md) and [Docker](templates/docker.md) defaults and inheritance.
- [Software and runtime](software-and-runtime.md): named packages, images, process and security settings, health checks, authentication and monitoring choices.
- [Declaration records](declaration-records.md): field notation, selected values and the framework's typed owners.
- [Composition](../guides/compose-a-site.md): apply a choice to concrete site-owned identity and allocations.
- [Examples](../examples/README.md): complete maintained sources and source-only evidence.

The registration authority is [stack.json](../../stack.json); [images.json](../../images.json) owns image policy. Maintainers use the [profile documentation template](../templates/application-profile.md), [contributor workflow](../contributing.md) and [documentation conformance scope](../testing.md#documentation-conformance). Every profile's complete usage is recorded in the [example catalogue](../../examples/catalogue/README.md).

[Backup coverage for every profile](backup-coverage.md) identifies the state to preserve, required native database exports and explicit exclusions for transient or rebuildable data. The [PBS backup guide](../backup.md) explains client preparation, operational schedules and their prerequisites.

The [PBS client backup profile](backup-profiles.md) lists its selected software and exact guest configuration paths.
