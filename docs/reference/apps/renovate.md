[Documentation](../../README.md) / [Reference](../README.md)

# Renovate

Run Mend Renovate Community Edition as a scheduled GitHub dependency-update server with a separate shared PostgreSQL database. It proposes catalogue pull requests for human review. It does not merge or deploy them.

## Choose this profile

Select `apps.<instance>.profile: renovate` on a Debian LXC using the Docker guest template. The [definition](../../../apps/renovate.yaml) owns one `renovate` service. Each instance requires its own project, storage and explicitly selected PostgreSQL owner. The current database contract supports one application database per PostgreSQL app. Multiple instances sharing one guest have not been verified.

CE is the server distribution, not the standalone CLI image. It uses hourly scans of exact repository names. There is no public listener, webhook, endpoint, Traefik dependency or Enterprise Web UI. The internal health endpoint is checked inside the running container.

## First installation

A fresh guest needs an owned volume for two new writable directories. The initializer creates them as UID/GID 12021 with mode 0700. The selected PostgreSQL app must already be under HomeLab ownership or complete its own supported commissioning. Its `properties.application_database: {app: renovate}` opts into creation of the consumer's role and database. This refuses pre-existing or partially created unowned database objects; it cannot adopt another installation.

Configure the GitHub App for selected repositories and disable its webhook. Review the vendor terms and obtain an appropriate CE licence before supplying the protected acceptance input. Source compilation and packet tests do not prove CE startup, authenticated scanning, database recovery or a working GitHub App.

## Minimal usage

This is an **app-selection fragment** from the [complete synthetic composition](../../../examples/catalogue/renovate.yaml):

```yaml
apps:
  renovate:
    profile: renovate
    guest: renovate
    lifecycle: fresh
```

Use app `renovate` in that composition. After the [source-only setup](../../guides/first-configuration.md) defines STACK, FRAMEWORK and PYTHON:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK" --site "$STACK/examples/catalogue/renovate.yaml" --check
```

This compiles both guests without credentials or target contact. PostgreSQL is the explicit `start` predecessor. The example includes both sides of the database firewall policy; a connection reference alone grants no access.

## Interfaces, listeners and storage

The required `database_interface` accepts a physical `guest-interface` binding. It supplies the source IPv4 address used by the PostgreSQL connection and scoped HBA rule. No listener or exported endpoint is declared. Outbound DNS, registry, GitHub and package access remain site policy.

| Storage role | Target | Requirement | Fresh owner |
| --- | --- | --- | --- |
| `scratch` | `/tmp` | Writable directory on an owned volume | 12021:12021, 0700 |
| `cache` | `/opt/containerbase` | Writable directory on an owned volume | 12021:12021, 0700 |

These are the only writable container mounts. The root filesystem is read-only, all capabilities are dropped and privilege escalation is disabled. There is no Docker socket mount.

## Application properties and connections

| Input | Presence and accepted value | Effect |
| --- | --- | --- |
| `properties.database` | Required nonempty mapping with exactly `name` and `user`; neither has a default. | Names the database and login owned by the selected PostgreSQL app. |
| `database.name`, `database.user` | Required strings matching `[a-z][a-z0-9_]{0,62}`. Reserved PostgreSQL names and the `pg_` prefix are refused. | Safe SQL identifiers; the role owns only its new database and has no administrative privileges or memberships. |
| `properties.repositories` | Required list of 1–10 distinct exact `owner/repository` strings; case-insensitive duplicates, wildcards, null and empty lists are refused. | Restricts hourly discovery to the installed App's selected repositories. |
| `connections.database` | Required PostgreSQL connection on TCP 5432 with `readiness: start`, to the explicit database owner in the same deployment context. | Derives PGHOST/PGPORT and ordering; no credentials are duplicated in this binding. |
| Producer `properties.application_database` | Required for this composition; exactly `{app: CONSUMER_ID}` on the selected PostgreSQL app. | Derives a narrowly scoped HBA entry and consumes the same protected database-password reference. |

Unknown properties are rejected. Omission, null or an empty value cannot disable a required input. The framework's [Renovate contract](https://github.com/theaussiepom/homelab/blob/f8a629ed78732f5fb72f3da6c7da0e88b7844606/docs/reference/renovate.md) owns validation and database lifecycle behavior.

## Protected inputs

| App secret role | Required value |
| --- | --- |
| `accept_terms` | Explicit `y` only after a human accepts the applicable Mend terms. |
| `license_key` | Appropriate current Mend Community licence. |
| `github_app_id` | Positive numeric GitHub App ID. |
| `github_app_key` | App PEM encoded as a single `base64://...` value. |
| `database_password` | Strong single-line UTF-8 password shared by reference with PostgreSQL. |

All five are required bounded scalar secrets, delivered by protected CD. No values appear in source or rendered public configuration. The framework seals a private Compose environment overlay; ordinary CD preserves it and verifies the existing database password without rotating it. The PostgreSQL owner receives only the database password. The licence and App credentials remain with Renovate.

## Software and resource policy

The profile selects [`docker`](../software-and-runtime.md#registration-software-docker), [`renovate-images`](../software-and-runtime.md#registration-software-renovate-images), [`container-host`](../software-and-runtime.md#registration-runtime-profiles-container-host) and [`renovate`](../software-and-runtime.md#registration-runtime-profiles-renovate). The authoritative CE image tag and immutable digest live in [images.json](../../../images.json). The service has a 2048 MiB limit, two CPUs and 512 PIDs. Guest memory must also cover the OS reserve; the complete example allocates 2560 MiB. These are initial resource bounds, not measured scan capacity.

## Later deployments

Keep the same database, role, App, project and storage identities. Ordinary deployment reuses the owned role and database, checks that elevated privileges and public database access remain absent, and authenticates with the existing sealed password. It does not adopt, drop, rotate or repair database objects. A partial first installation stops for review and preserves evidence.

Image proposals come from the existing catalogue through [the image-update guide](../../guides/images-and-updates.md#propose-catalogue-updates-with-renovate). Review and merge PRs under existing protections, then explicitly update the consuming site's pinned source and use protected CD. An image change can recreate the container and interrupt scans. Database schema compatibility and restore must be assessed before upgrading; no universal downgrade is promised.

## Invalid cases

Starting from the complete example, remove `postgresql.properties.application_database`: the binding layer emits `component.database-binding` because the consumer has no explicit owner. Restore the owner reference and compile both guests again.

Set `renovate.properties.repositories` to `['example/*']`: property validation emits `component.renovate-repositories` at `apps.renovate.properties`. Replace it with an exact repository name, then compile and generate the complete packets. Supplying `accept_terms: n` through protected CD is separately refused during private preparation; offline compilation does not read its value.

The [profile integration tests](../../../tests/test_profile_examples.py) exercise valid source, explicit dependencies, private reference propagation and these invalid cases. Native database and CE service acceptance require an authorized deployment and service checks.

## Backup coverage

See [Renovate recovery coverage](../backup-coverage.md#renovate). Scratch and downloaded tools are excluded as transient/rebuildable. The private overlay and database ownership receipt are configuration; PostgreSQL's native export covers the role and CE database. Independently retain the App key and licence. An isolated CE restore has not been verified.

## Declaration records

The following supplied values come from [renovate.yaml](../../../apps/renovate.yaml). They are reusable definition values, not arbitrary site overrides; [declaration records](../declaration-records.md) explains their types and binding rules.

| Declaration path | Selected value |
| --- | --- |
| <a id="declaration-adapter"></a>`adapter` | `"renovate"` |
| <a id="declaration-display-name"></a>`display_name` | `"Renovate"` |
| <a id="declaration-interfaces"></a>`interfaces` | `object` |
| <a id="declaration-interfaces-database-interface"></a>`interfaces.database_interface` | `object` |
| <a id="declaration-interfaces-database-interface-required"></a>`interfaces.database_interface.required` | `true` |
| <a id="declaration-interfaces-database-interface-accepts"></a>`interfaces.database_interface.accepts` | `["guest-interface"]` |
| <a id="declaration-listeners"></a>`listeners` | `{}` |
| <a id="declaration-endpoints"></a>`endpoints` | `{}` |
| <a id="declaration-storage"></a>`storage` | `object` |
| <a id="declaration-storage-scratch"></a>`storage.scratch` | `object` |
| <a id="declaration-storage-scratch-target"></a>`storage.scratch.target` | `"/tmp"` |
| <a id="declaration-storage-scratch-read-only"></a>`storage.scratch.read_only` | `false` |
| <a id="declaration-storage-scratch-required"></a>`storage.scratch.required` | `true` |
| <a id="declaration-storage-scratch-kind"></a>`storage.scratch.kind` | `"directory"` |
| <a id="declaration-storage-scratch-initialize"></a>`storage.scratch.initialize` | `object` |
| <a id="declaration-storage-scratch-initialize-type"></a>`storage.scratch.initialize.type` | `"directory"` |
| <a id="declaration-storage-scratch-initialize-uid"></a>`storage.scratch.initialize.uid` | `12021` |
| <a id="declaration-storage-scratch-initialize-gid"></a>`storage.scratch.initialize.gid` | `12021` |
| <a id="declaration-storage-scratch-initialize-mode"></a>`storage.scratch.initialize.mode` | `"0700"` |
| <a id="declaration-storage-cache"></a>`storage.cache` | `object` |
| <a id="declaration-storage-cache-target"></a>`storage.cache.target` | `"/opt/containerbase"` |
| <a id="declaration-storage-cache-read-only"></a>`storage.cache.read_only` | `false` |
| <a id="declaration-storage-cache-required"></a>`storage.cache.required` | `true` |
| <a id="declaration-storage-cache-kind"></a>`storage.cache.kind` | `"directory"` |
| <a id="declaration-storage-cache-initialize"></a>`storage.cache.initialize` | `object` |
| <a id="declaration-storage-cache-initialize-type"></a>`storage.cache.initialize.type` | `"directory"` |
| <a id="declaration-storage-cache-initialize-uid"></a>`storage.cache.initialize.uid` | `12021` |
| <a id="declaration-storage-cache-initialize-gid"></a>`storage.cache.initialize.gid` | `12021` |
| <a id="declaration-storage-cache-initialize-mode"></a>`storage.cache.initialize.mode` | `"0700"` |
| <a id="declaration-connections"></a>`connections` | `object` |
| <a id="declaration-connections-database"></a>`connections.database` | `object` |
| <a id="declaration-connections-database-type"></a>`connections.database.type` | `"postgresql"` |
| <a id="declaration-connections-database-required"></a>`connections.database.required` | `true` |
| <a id="declaration-connections-database-readiness"></a>`connections.database.readiness` | `["start"]` |
| <a id="declaration-software"></a>`software` | `["docker", "renovate-images"]` |
| <a id="declaration-runtime"></a>`runtime` | `["container-host", "renovate"]` |
| <a id="declaration-health"></a>`health` | `object` |
| <a id="declaration-health-ready"></a>`health.ready` | `object` |
| <a id="declaration-health-ready-profile"></a>`health.ready.profile` | `"adapter-ready"` |
| <a id="declaration-secrets"></a>`secrets` | `object` |
| <a id="declaration-secrets-accept-terms"></a>`secrets.accept_terms` | `object` |
| <a id="declaration-secrets-accept-terms-required"></a>`secrets.accept_terms.required` | `true` |
| <a id="declaration-secrets-license-key"></a>`secrets.license_key` | `object` |
| <a id="declaration-secrets-license-key-required"></a>`secrets.license_key.required` | `true` |
| <a id="declaration-secrets-github-app-id"></a>`secrets.github_app_id` | `object` |
| <a id="declaration-secrets-github-app-id-required"></a>`secrets.github_app_id.required` | `true` |
| <a id="declaration-secrets-github-app-key"></a>`secrets.github_app_key` | `object` |
| <a id="declaration-secrets-github-app-key-required"></a>`secrets.github_app_key.required` | `true` |
| <a id="declaration-secrets-database-password"></a>`secrets.database_password` | `object` |
| <a id="declaration-secrets-database-password-required"></a>`secrets.database_password.required` | `true` |
| <a id="declaration-monitoring"></a>`monitoring` | `object` |
| <a id="declaration-monitoring-profile"></a>`monitoring.profile` | `"docker-agent"` |
| <a id="declaration-backup"></a>`backup` | `object` |
| <a id="declaration-backup-include"></a>`backup.include` | `{}` |
| <a id="declaration-backup-exclude"></a>`backup.exclude` | `object` |
| <a id="declaration-backup-exclude-scratch"></a>`backup.exclude.scratch` | `"transient"` |
| <a id="declaration-backup-exclude-cache"></a>`backup.exclude.cache` | `"rebuildable"` |
