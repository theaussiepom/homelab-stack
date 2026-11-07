# Application backup coverage

[Configure PBS backups](../backup.md) · [Profile catalogue](README.md)

These are source recovery requirements, not observations of installed protection.
Profile roles map to guest volume/root paths through the existing app bindings.
Only bound optional roles produce paths. Generated runtime leaves are included
individually; public source/Git alone cannot replace private credentials or keys.

- **files**: selected configuration; verify the actual path and ownership at adoption.
- **application-export**: coherent native/service-aware capture required before upload. A warm directory scan is not enough.
- **database-export**: a native database producer owns the export; its raw engine directory is excluded from selected file intake.
- **transient/rebuildable**: explicitly excluded from selected recovery. An exclusion does not delete the original data or exclude a whole full-guest volume.

## Native databases

| Producer | Required native recovery set | Configuration retained separately |
| --- | --- | --- |
| PostgreSQL | Compatible native backups or logical database exports, roles/globals, extensions, locale/version metadata, keys and actual restored database verification | `/etc/postgresql` |
| MariaDB | Supported compatible native/logical backups, users/grants/plugins/collations and recovery of the selected schemas/history, including late writes | `/etc/mysql` |
| InfluxDB | Native backup plus organization/bucket/authentication and version/engine metadata; verify query and write behavior after restore | `/etc/influxdb` |

Each producer owns its own credentials and consistency boundary. A database
connection from another app is not a backup producer. A bound root `backup.job` runs the finite native producers and coordinated
application capture window. Bare `backup:` installs no timer. Actual restore
qualification and NAS/server maintenance remain part of site integration.

## Application recovery notes

| App | Authoritative recovery material and consistency limits |
| --- | --- |
| Home Assistant | Config, `.storage`, auth/fabric/pairing/private state, compatible custom integrations/patches and selected media; recorder recovery is separate when connected. An existing SQLite database needs a supported consistent capture. |
| Node-RED | Flows, credentials, credential encryption key, settings, modules and persistent context as one usable generation. Preserve private API/OIDC inputs independently where the guest does not retain them. |
| Bitwarden | `/etc/bitwarden` includes attachments and application protection material. Associate it with the MariaDB generation and required environment/encryption material; database-only recovery is insufficient. Logs are excluded. |
| Authentik | PostgreSQL generation plus secret key, media, custom templates, certs and compatible Redis state. Stop the owned Redis and Authentik services before capture; a warm Redis directory copy is not coherent. |
| MQTT | Broker configuration/password/cert material plus retained messages, durable sessions and QoS persistence. Use a broker-supported consistent capture; do not publish synthetic device commands as a backup test. |
| MQTT Explorer | Saved connection/UI state plus the separately owned broker account. Capturing the GUI is not a broker backup. |
| Zigbee2MQTT | Keys, devices/groups/database/state plus existing coordinator backups, hardware/firmware identity and backup age. No routine radio/NVM commands, reset or duplicate coordinator activation. |
| Pi-hole | Teleporter/native export and coherent configuration SQLite/private state. Optional query-history volume is excluded by default; it is not the authoritative configuration export. A Pi-hole configuration capture requires explicit permission to pause its owned services; do not assume DNS can be interrupted. |
| Unbound | Configuration, private control/server keys and trust-anchor state. Device/chroot nodes and cache are reproducible; the mixed runtime `var` role requires a service-aware selection rather than guessing its contents. |
| Music Assistant | Provider identities, authentication and private app state, including consistent SQLite/native artifacts. A backup test must not issue playback/player commands. |
| PegaProx | Config, encryption key/accounts and coherent encrypted SQLite/state. Application logs are excluded; database files alone do not restore the key. |
| CloudBeaver | Workspace, saved connections/private settings and required generated-account custody. Managed database contents belong to their native database producers. |
| Traefik | ACME account/certificate material, owned static/dynamic configuration and required provider/trust inputs. Preserve renewal/account identity; recompilable public route definitions are a separate rebuild input. |
| Zabbix | PostgreSQL recovery plus owned runtime configuration, agent PSKs, Proxmox token/trust and required Influx data when selected. No per-guest credential rotation is implied. |
| WiNet | Owned options/runtime configuration and required inverter/MQTT credentials. This profile declares no separate storage volume; it does not imply the configuration is credential-free. |

Database-only copies, one online SQLite export, file integrity and a successful
PBS upload each prove different things. None alone proves a matched application
restore. Site integration must establish coherent generations and independently
recoverable secret/key custody.

## Exact profile storage dispositions

Every registered variant is listed below. Paths are application mount targets,
not site allocations; the compiler derives the real source from each binding.

### authentik

[Application reference](apps/authentik.md) · [Definition](../../apps/authentik.yaml)

| Role / app target | Disposition | Capture requirement |
| --- | --- | --- |
| `media` — `/media` | state | application-export |
| `templates` — `/templates` | configuration | files |
| `certs` — `/certs` | configuration | files |
| `redis` — `/data` | state | application-export |

### bitwarden

[Application reference](apps/bitwarden.md) · [Definition](../../apps/bitwarden.yaml)

| Role / app target | Disposition | Capture requirement |
| --- | --- | --- |
| `data` — `/etc/bitwarden` | state | application-export |
| `logs` — `/var/log/bitwarden` | Excluded: transient | None |

### cloudbeaver-mariadb-admin

[Application reference](apps/cloudbeaver-mariadb-admin.md) · [Definition](../../apps/cloudbeaver-mariadb-admin.yaml)

| Role / app target | Disposition | Capture requirement |
| --- | --- | --- |
| `workspace` — `/opt/cloudbeaver/workspace` | state | application-export |

### cloudbeaver

[Application reference](apps/cloudbeaver.md) · [Definition](../../apps/cloudbeaver.yaml)

| Role / app target | Disposition | Capture requirement |
| --- | --- | --- |
| `workspace` — `/opt/cloudbeaver/workspace` | state | application-export |

### homeassistant-public

[Application reference](apps/homeassistant-public.md) · [Definition](../../apps/homeassistant-public.yaml)

| Role / app target | Disposition | Capture requirement |
| --- | --- | --- |
| `config` — `/config` | state | application-export |
| `media` — `/media` | state | application-export |
| `community` — `/hacsfiles` | state | application-export |
| `startup` — `/startup` | configuration | files |

### homeassistant

[Application reference](apps/homeassistant.md) · [Definition](../../apps/homeassistant.yaml)

| Role / app target | Disposition | Capture requirement |
| --- | --- | --- |
| `config` — `/config` | state | application-export |
| `media` — `/media` | state | application-export |
| `community` — `/hacsfiles` | state | application-export |
| `startup` — `/startup` | configuration | files |

### influxdb

[Application reference](apps/influxdb.md) · [Definition](../../apps/influxdb.yaml)

| Role / app target | Disposition | Capture requirement |
| --- | --- | --- |
| `data` — `/var/lib/influxdb` | database | database-export |

### mariadb

[Application reference](apps/mariadb.md) · [Definition](../../apps/mariadb.yaml)

| Role / app target | Disposition | Capture requirement |
| --- | --- | --- |
| `data` — `/var/lib/mysql` | database | database-export |

### mqtt

[Application reference](apps/mqtt.md) · [Definition](../../apps/mqtt.yaml)

| Role / app target | Disposition | Capture requirement |
| --- | --- | --- |
| `config` — `/mosquitto/config` | configuration | files |
| `data` — `/mosquitto/data` | state | application-export |
| `log` — `/mosquitto/log` | Excluded: transient | None |

### mqtt_explorer

[Application reference](apps/mqtt_explorer.md) · [Definition](../../apps/mqtt_explorer.yaml)

| Role / app target | Disposition | Capture requirement |
| --- | --- | --- |
| `data` — `/app/data` | state | application-export |

### music_assistant

[Application reference](apps/music_assistant.md) · [Definition](../../apps/music_assistant.yaml)

| Role / app target | Disposition | Capture requirement |
| --- | --- | --- |
| `data` — `/data` | state | application-export |

### node_red-public

[Application reference](apps/node_red-public.md) · [Definition](../../apps/node_red-public.yaml)

| Role / app target | Disposition | Capture requirement |
| --- | --- | --- |
| `data` — `/data` | state | application-export |

### node_red

[Application reference](apps/node_red.md) · [Definition](../../apps/node_red.yaml)

| Role / app target | Disposition | Capture requirement |
| --- | --- | --- |
| `data` — `/data` | state | application-export |
| `config` — `/config` | state | application-export |
| `settings` — `/runtime-settings.js` | configuration | files |
| `healthcheck` — `/healthcheck.js` | Excluded: rebuildable | None |

### pegaprox

[Application reference](apps/pegaprox.md) · [Definition](../../apps/pegaprox.yaml)

| Role / app target | Disposition | Capture requirement |
| --- | --- | --- |
| `config` — `/app/config` | state | application-export |
| `logs` — `/app/logs` | Excluded: transient | None |

### pihole

[Application reference](apps/pihole.md) · [Definition](../../apps/pihole.yaml)

| Role / app target | Disposition | Capture requirement |
| --- | --- | --- |
| `config` — `/etc/pihole` | state | application-export |
| `database` — `/ftl-db` | Excluded: transient | None |

### postgresql

[Application reference](apps/postgresql.md) · [Definition](../../apps/postgresql.yaml)

| Role / app target | Disposition | Capture requirement |
| --- | --- | --- |
| `data` — `/var/lib/postgresql` | database | database-export |

### traefik

[Application reference](apps/traefik.md) · [Definition](../../apps/traefik.yaml)

| Role / app target | Disposition | Capture requirement |
| --- | --- | --- |
| `certs` — `/var/traefik/certs` | state | application-export |

### unbound

[Application reference](apps/unbound.md) · [Definition](../../apps/unbound.yaml)

| Role / app target | Disposition | Capture requirement |
| --- | --- | --- |
| `config` — `/opt/unbound/etc/unbound` | configuration | files |
| `dev` — `/opt/unbound/etc/unbound/dev` | Excluded: transient | None |
| `var` — `/opt/unbound/etc/unbound/var` | state | application-export |
| `control_key` — `/opt/unbound/etc/unbound/unbound_control.key` | configuration | files |
| `control_cert` — `/opt/unbound/etc/unbound/unbound_control.pem` | configuration | files |
| `server_key` — `/opt/unbound/etc/unbound/unbound_server.key` | configuration | files |
| `server_cert` — `/opt/unbound/etc/unbound/unbound_server.pem` | configuration | files |

### winet

[Application reference](apps/winet.md) · [Definition](../../apps/winet.yaml)

No declared storage roles. Preserve the individually owned runtime inputs and the related native database recovery sets where configured.

### zabbix

[Application reference](apps/zabbix.md) · [Definition](../../apps/zabbix.yaml)

No declared storage roles. Preserve the individually owned runtime inputs and the related native database recovery sets where configured.

### zigbee2mqtt

[Application reference](apps/zigbee2mqtt.md) · [Definition](../../apps/zigbee2mqtt.yaml)

| Role / app target | Disposition | Capture requirement |
| --- | --- | --- |
| `data` — `/app/data` | state | application-export |

