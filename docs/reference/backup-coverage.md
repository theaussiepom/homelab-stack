# Application backup coverage

[Configure PBS backups](../backup.md) · [PBS client profile](backup-profiles.md) · [Profile catalogue](README.md)

This catalogue states what each application needs for recovery. It does not report installed protection or a verified restore. App bindings connect profile storage roles to actual guest volumes or root-filesystem paths. Only bound optional roles produce paths. HomeLab lists generated runtime files individually; public source and Git cannot replace private credentials or encryption keys.

- **files** identifies configuration files for capture. Verify the actual path and file ownership when preparing the installation.
- **application-export** requires consistent application state. An operational job must have permission to pause the app’s existing services before capture; copying a directory while its writers run is insufficient.
- **database-export** requires the database’s native export procedure. Its live engine directory is excluded from selected file capture.
- **transient** and **rebuildable** explicitly exclude a role from selected application recovery. Exclusion neither deletes the original data nor excludes an entire volume from native full-guest backup.

## Native databases

| Producer | Required native recovery set | Configuration retained separately |
| --- | --- | --- |
| PostgreSQL | Preserve compatible native backups or logical exports, roles and globals, extensions, locale and version metadata, and keys. Verify the actual restored databases. | `/etc/postgresql` |
| MariaDB | Preserve supported compatible native or logical backups, users, grants, plugins and collations. Verify recovery of the selected schemas and history, including late writes. | `/etc/mysql` |
| InfluxDB | Preserve a native backup, organization, bucket and authentication information, and version and engine metadata. Verify queries and writes after restore. | `/etc/influxdb` |

Each database owns its credentials and the procedure that keeps its export consistent. Another app’s database connection is not a backup producer. A configured root `backup.job` runs the supported native producers and coordinates the application capture window. Bare `backup:` installs no timer. Testing restores and maintaining the NAS and PBS server remain site responsibilities.

## Application recovery notes

| App | Authoritative recovery material and consistency limits |
| --- | --- |
| Home Assistant | Preserve configuration, `.storage`, authentication, fabric and pairing records, other private state, compatible custom integrations and patches, and selected media. Recover an external recorder separately when selected. An existing SQLite database needs consistent capture. |
| Node-RED | Preserve flows, credentials, the credential-encryption key, settings, modules and persistent context from one usable generation. Keep private API and OpenID Connect inputs independently recoverable when the guest does not retain them. |
| Bitwarden | `/etc/bitwarden` includes attachments and application protection files. Match it to the MariaDB generation and required environment and encryption files; a database-only copy cannot recover the vault. Logs are excluded. |
| Authentik | Preserve the matching PostgreSQL generation, secret key, media, custom templates, certificates and compatible Redis state. Stop the app’s Redis and Authentik services before capture; copying a running Redis directory does not preserve a coherent state. |
| MQTT | Preserve broker configuration, passwords and certificates, retained messages, durable sessions and quality-of-service persistence. Use a capture procedure that keeps the broker’s state consistent; do not publish synthetic device commands as a backup test. |
| MQTT Explorer | Preserve saved connections and user-interface state, plus the separately managed broker account. Capturing the GUI does not back up the broker. |
| Zigbee2MQTT | Preserve keys, devices, groups, databases and state, together with existing coordinator backups, hardware and firmware identity, and backup age. Routine capture must not issue radio or non-volatile-memory commands, reset the coordinator or activate a duplicate coordinator. |
| Pi-hole | Recovery needs Teleporter or native exports and consistently captured configuration, SQLite databases and private state. The optional query-history volume is excluded by default and does not replace configuration recovery. Capturing the configuration requires explicit permission to pause the app’s services; do not assume DNS can be interrupted. |
| Unbound | Preserve configuration, private control and server keys, and trust-anchor state. Device nodes, chroot nodes and cache can be rebuilt. The mixed runtime `var` role needs capture that accounts for the service’s changing state; do not guess which files matter. |
| Music Assistant | Preserve provider identities, authentication and private app state, including consistent SQLite or native artifacts. A backup test must not issue playback or player commands. |
| PegaProx | Preserve configuration, encryption keys, accounts and consistently captured encrypted SQLite data and other state. Application logs are excluded; database files alone cannot restore the key. |
| CloudBeaver | Preserve the workspace, saved connections, private settings and ownership records for generated accounts. Managed database contents must be backed up by their native database producers. |
| Traefik | Preserve ACME accounts and certificates, managed static and dynamic configuration, and required provider and trust inputs. Keep the renewal and account identities. Public route definitions that can be regenerated are separate rebuild inputs. |
| Zabbix | Preserve the PostgreSQL recovery set, managed runtime configuration, agent pre-shared keys, Proxmox token and trust inputs, and required InfluxDB data when selected. Recovery does not imply rotating each guest’s credentials. |
| WiNet | Preserve managed options and runtime configuration, plus the required inverter and MQTT credentials. This profile has no separate storage volume; it still has protected configuration. |

Database-only copies, one SQLite export taken while it is running, file-integrity checks and a successful PBS upload establish different facts. None alone proves that the related application and database can be restored together. Site verification must establish matching generations and independently recoverable credentials and keys. The profile’s capture classification does not claim that every vendor recovery export or service restore has already been performed.

## Exact profile storage dispositions

Every registered variant is listed below. Paths are application mount targets, not site allocations; the compiler derives the real source from each binding.

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

### homeassistant-bound

[Application reference](apps/homeassistant-bound.md) · [Definition](../../apps/homeassistant-bound.yaml)

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

### influxdb-web

[Application reference](apps/influxdb-web.md) · [Definition](../../apps/influxdb-web.yaml)

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

### music_assistant-split

[Application reference](apps/music_assistant-split.md) · [Definition](../../apps/music_assistant-split.yaml)

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

Prepare the excluded health wrapper using the [rebuild source](#node-red-health-wrapper-recovery)
before recovering this app; its absence from selected capture does not make it optional.

### node_red-bound

[Application reference](apps/node_red-bound.md) · [Definition](../../apps/node_red-bound.yaml)

| Role / app target | Disposition | Capture requirement |
| --- | --- | --- |
| `data` — `/data` | state | application-export |
| `config` — `/config` | state | application-export |
| `settings` — `/runtime-settings.js` | configuration | files |
| `healthcheck` — `/healthcheck.js` | Excluded: rebuildable | None |

The bound profile also needs the [recoverable health wrapper](#node-red-health-wrapper-recovery)
before CD can start and check the app.

<a id="node-red-health-wrapper-recovery"></a>
#### Rebuild the Node-RED health wrapper

The reusable wrapper is versioned as
[`node-red-healthcheck.js`](https://github.com/theaussiepom/homelab/blob/c694b1d286faf60e29f5a9f5a0a218c9dcbbc4da/proxmox/applications/node-red-healthcheck.js).
Use the same framework revision selected by this Stack. During recovery,
separately prepare that file at the app's bound `healthcheck` storage source
before CD. The profile mounts it read-only at `/healthcheck.js`; it reads the
recovered `/config/settings.js` and uses `NODE_RED_WEB_ADDRESS` when selected.
If you maintain a different wrapper, keep its version and a separate recoverable
copy. The public helper cannot reproduce custom behavior that it does not contain.

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
