[Documentation](../../README.md) / [Reference](../README.md)

# Scrypted

Run prepared Scrypted configuration and its database on local guest storage while keeping NVR recordings on a separately mounted NAS directory.

## Choose this profile

| Setting | Value |
| --- | --- |
| Site selection | `apps.<instance>.profile: scrypted` |
| Adapter / owned container | `scrypted` / `scrypted` |
| Placement | Debian Docker guest on Proxmox, with host networking |
| Multiple instances | Use separate guests because the web listener uses a fixed host socket. |

The reusable declaration is [scrypted.yaml](../../../apps/scrypted.yaml). Your site supplies the guest identity, interfaces, storage, access rules and deployment authority. Selecting a web endpoint or adding Proxmox routing labels does not require another app to start first. Select an actual readiness dependency only when the service needs it.

## Minimal usage

This is an **app-selection fragment** from the [complete synthetic composition](../../../examples/catalogue/scrypted.yaml):

```yaml
apps:
  scrypted:
    profile: scrypted
    guest: cameras
    lifecycle: retained
```

The complete example requires an already HomeLab-managed guest, prepared Scrypted state and its exact NAS bind. It cannot adopt an existing installation. After [source-only setup](../../guides/first-configuration.md) defines STACK, FRAMEWORK and PYTHON, compile it with:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK" --site "$STACK/examples/catalogue/scrypted.yaml" --check
```

Compilation reads no credentials and contacts no target. It does not establish that a NAS mount exists or that Scrypted can decode or record video.

## Interfaces, listeners and endpoints

| Role | Required | Accepted binding |
| --- | --- | --- |
| `web_interface` | Yes | `guest-interface` |

| Listener | Service / namespace | Bind | Port |
| --- | --- | --- | --- |
| `web_listener` | `scrypted` / `host` | wildcard | `80/tcp` |
| `secure_listener` | `scrypted` / `host` | wildcard | `443/tcp` |

| Endpoint | Protocol | Address |
| --- | --- | --- |
| `web_endpoint` | `http` | Selected `web_interface` address and web listener port |

The process uses host networking. The adapter explicitly sets the HTTP and HTTPS ports above and derives the container name and hostname from the selected runtime identity. The selected role advertises an address; it does not restrict Scrypted to that address or create firewall rules. Your site must explicitly allow the required browser, camera, recording and discovery traffic. A listener check does not prove any of those integrations. The HTTPS listener uses Scrypted's own certificate; a routed HTTP exposure still has separately declared ingress TLS and access policy.

## Storage

| Role | Required | Container target | Binding / access | Initializer |
| --- | --- | --- | --- | --- |
| `data` | Yes | `/server/volume` | local managed guest volume / writable directory | None |
| `recordings` | Yes | `/nvr` | complete declared NAS root path / writable directory | None |

Bind `data` to a managed volume. Bind `recordings` to a guest `root_path` with `subpath: ''` and an exact `host_bind` declaration. The mount metadata supplies the expected NAS source, filesystem and root within that filesystem. The two directories must be separate and must not contain one another. Neither bind creates a missing host directory.

Before starting the container, HomeLab verifies the existing database directory and the recording mount's exact source, NFS filesystem, filesystem root, mount target and writable access. It refuses a missing mount rather than writing recordings to a local fallback. The check does not establish free space, NAS durability or an independent recording backup.

## Connections, private inputs and application properties

This profile declares no companion-service connection or direct secret role. Existing Scrypted credentials, camera identities, plugins and NVR configuration remain in its prepared data. Protect that directory and its recovery material.

The adapter accepts no application properties. Arbitrary commands, environment variables, devices and mount overrides are not accepted inputs.

## Software and resource policy

Software: [`docker`](../software-and-runtime.md#registration-software-docker), [`curl`](../software-and-runtime.md#registration-software-curl), [`scrypted-images`](../software-and-runtime.md#registration-software-scrypted-images). Runtime: [`container-host`](../software-and-runtime.md#registration-runtime-profiles-container-host) and [`scrypted`](../software-and-runtime.md#registration-runtime-profiles-scrypted).

| Image role | Catalogue ID | Policy |
| --- | --- | --- |
| `scrypted` | `scrypted` | Floating `ghcr.io/koush/scrypted:latest` |

| Service | Memory MiB | CPU limit | PID limit | Numeric user |
| --- | --- | --- | --- | --- |
| `scrypted` | 4096 | 4 | 512 | `0:0` |

The guest needs additional memory for its operating system. The container has no swap allowance beyond its memory limit, no graphics-device passthrough and no automatic restart. Resource limits contain failures; they do not prove a decoder is safe.

The upstream `/init` entrypoint remains in place. Before the upstream server command runs, a fixed helper reads the database using Level only and checks the software decoder settings. It requires one global NVR decoder with `hwaccel: none` and `hwscalar: Software`; explicit hardware overrides and enabled OpenCL motion are refused. The helper loads no plugin or graphics code and changes no settings. Opening Level can update its normal lock and log files.

## First installation

This adapter starts prepared Scrypted state. It does not create an empty installation, restore a backup, import a foreign ownership record, copy recordings or configure cameras. Prepare the local data generation and exact NAS attachment through an authorised commissioning procedure before the first application start. The NAS mount needs platform support and authority beyond naming a `root_path`.

## Later deployments

Keep the same app, service and Compose project identities, both storage bindings, numeric user and credentials. Ordinary CD maintains the declared runtime and repeats the storage and software-setting checks. A floating latest tag can select a different upstream image; it is not a digest pin or a promise of compatibility with a future image.

HomeLab does not silently reset decoder choices, initialise missing state, change data ownership or recover an unavailable NAS. A failed guard leaves the service unstarted. Authorised target checks must separately establish login, camera connections, software decoding and recording continuity. Read [images and updates](../../guides/images-and-updates.md) before changing software.

## Backup coverage

The [recovery catalogue](../backup-coverage.md#scrypted) classifies local `data` as state captured with `application-export`. Enrolling the guest in PBS requires the normal protected backup inputs and explicit permission to pause Scrypted for a consistent capture. The NAS `recordings` role is excluded as `external-recordings`; that exclusion does not mean the recordings are transient or rebuildable, and makes no independent backup claim. See [PBS backups](../../backup.md).

## Invalid cases and verification

| Invalid change | Refusal and correction |
| --- | --- |
| Bind recordings to a local volume, a subdirectory binding or an undeclared host mount | `component.scrypted-storage`; bind the exact declared NAS root path. |
| Use `external-recordings` for another app or another role | `component.backup-external-recordings`; use the correct storage classification. |
| Missing, read-only or different NAS mount | Pre-start storage guard refuses; restore the declared mount before retrying. |
| Default global decoder or an explicit hardware override | Startup settings guard refuses; review and prepare software settings before retrying. |

Run the [library checks](../../testing.md), including the real example compiler integration. Source tests, hosted CI, deployment and service acceptance remain separate evidence.

## Declaration records

These are the complete supplied fields in [scrypted.yaml](../../../apps/scrypted.yaml). They describe reusable definition values, not arbitrary instance overrides. [Declaration records](../declaration-records.md) explains the notation. The documentation tests compare these rows with the loaded profile.

| Declaration path | Selected value |
| --- | --- |
| <a id="declaration-adapter"></a>`adapter` | `"scrypted"` |
| <a id="declaration-display-name"></a>`display_name` | `"Scrypted"` |
| <a id="declaration-interfaces"></a>`interfaces` | `object` |
| <a id="declaration-interfaces-web-interface"></a>`interfaces.web_interface` | `object` |
| <a id="declaration-interfaces-web-interface-required"></a>`interfaces.web_interface.required` | `true` |
| <a id="declaration-interfaces-web-interface-accepts"></a>`interfaces.web_interface.accepts` | `["guest-interface"]` |
| <a id="declaration-listeners"></a>`listeners` | `object` |
| <a id="declaration-listeners-web-listener"></a>`listeners.web_listener` | `object` |
| <a id="declaration-listeners-web-listener-service"></a>`listeners.web_listener.service` | `"scrypted"` |
| <a id="declaration-listeners-web-listener-namespace"></a>`listeners.web_listener.namespace` | `"host"` |
| <a id="declaration-listeners-web-listener-interface"></a>`listeners.web_listener.interface` | `"web_interface"` |
| <a id="declaration-listeners-web-listener-bind"></a>`listeners.web_listener.bind` | `"wildcard"` |
| <a id="declaration-listeners-web-listener-protocol"></a>`listeners.web_listener.protocol` | `"tcp"` |
| <a id="declaration-listeners-web-listener-port"></a>`listeners.web_listener.port` | `80` |
| <a id="declaration-listeners-secure-listener"></a>`listeners.secure_listener` | `object` |
| <a id="declaration-listeners-secure-listener-service"></a>`listeners.secure_listener.service` | `"scrypted"` |
| <a id="declaration-listeners-secure-listener-namespace"></a>`listeners.secure_listener.namespace` | `"host"` |
| <a id="declaration-listeners-secure-listener-interface"></a>`listeners.secure_listener.interface` | `"web_interface"` |
| <a id="declaration-listeners-secure-listener-bind"></a>`listeners.secure_listener.bind` | `"wildcard"` |
| <a id="declaration-listeners-secure-listener-protocol"></a>`listeners.secure_listener.protocol` | `"tcp"` |
| <a id="declaration-listeners-secure-listener-port"></a>`listeners.secure_listener.port` | `443` |
| <a id="declaration-endpoints"></a>`endpoints` | `object` |
| <a id="declaration-endpoints-web-endpoint"></a>`endpoints.web_endpoint` | `object` |
| <a id="declaration-endpoints-web-endpoint-listener"></a>`endpoints.web_endpoint.listener` | `"web_listener"` |
| <a id="declaration-endpoints-web-endpoint-protocol"></a>`endpoints.web_endpoint.protocol` | `"http"` |
| <a id="declaration-endpoints-web-endpoint-via"></a>`endpoints.web_endpoint.via` | `"web_interface"` |
| <a id="declaration-storage"></a>`storage` | `object` |
| <a id="declaration-storage-data"></a>`storage.data` | `object` |
| <a id="declaration-storage-data-target"></a>`storage.data.target` | `"/server/volume"` |
| <a id="declaration-storage-data-read-only"></a>`storage.data.read_only` | `false` |
| <a id="declaration-storage-data-required"></a>`storage.data.required` | `true` |
| <a id="declaration-storage-data-kind"></a>`storage.data.kind` | `"directory"` |
| <a id="declaration-storage-recordings"></a>`storage.recordings` | `object` |
| <a id="declaration-storage-recordings-target"></a>`storage.recordings.target` | `"/nvr"` |
| <a id="declaration-storage-recordings-read-only"></a>`storage.recordings.read_only` | `false` |
| <a id="declaration-storage-recordings-required"></a>`storage.recordings.required` | `true` |
| <a id="declaration-storage-recordings-kind"></a>`storage.recordings.kind` | `"directory"` |
| <a id="declaration-software"></a>`software` | `["docker", "curl", "scrypted-images"]` |
| <a id="declaration-runtime"></a>`runtime` | `["container-host", "scrypted"]` |
| <a id="declaration-health"></a>`health` | `object` |
| <a id="declaration-health-ready"></a>`health.ready` | `object` |
| <a id="declaration-health-ready-profile"></a>`health.ready.profile` | `"adapter-ready"` |
| <a id="declaration-monitoring"></a>`monitoring` | `object` |
| <a id="declaration-monitoring-profile"></a>`monitoring.profile` | `"docker-agent"` |
| <a id="declaration-backup"></a>`backup` | `object` |
| <a id="declaration-backup-include"></a>`backup.include` | `object` |
| <a id="declaration-backup-include-data"></a>`backup.include.data` | `object` |
| <a id="declaration-backup-include-data-category"></a>`backup.include.data.category` | `"state"` |
| <a id="declaration-backup-include-data-capture"></a>`backup.include.data.capture` | `"application-export"` |
| <a id="declaration-backup-exclude"></a>`backup.exclude` | `object` |
| <a id="declaration-backup-exclude-recordings"></a>`backup.exclude.recordings` | `"external-recordings"` |
