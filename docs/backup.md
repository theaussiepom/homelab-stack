# Configure PBS backups

[Documentation index](README.md) · [Application coverage](reference/backup-coverage.md) ·
[Software selection](reference/software-and-runtime.md)

Add the bare `backup` property at site root to prepare the PBS client in every
guest. It is a presence-based feature, like root monitoring; do not write
`backup: true`. Apps retain their independent profiles and placement.

```yaml
backup:
```

The library registers one `pbs-client` backup profile. An explicit equivalent is
`backup: {profile: pbs-client}`. The [selected framework backup contract](https://github.com/theaussiepom/homelab/blob/dcba8641270378305fa53a6979ca93f1b7fa794c/docs/reference/backup.md) owns validation,
compilation, coordinated capture, phase execution and the language contract. This library owns the
client package/repository definition and each app's recovery classification.

## Run the complete offline example

Use the `FRAMEWORK`, `STACK` and `PYTHON` paths from
[First configuration](guides/first-configuration.md):

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" \
  --stack "$STACK" --site "$STACK/site.backup.example.yaml" --check
```

This complete synthetic resolver source includes a fully bound operational job:
PBS endpoint, file-secret references, UTC schedule, explicit transfer policy and
a dedicated staging volume. Offline compilation requires no PBS server and opens
no secret files. It proves composition, not a backup or deployment.
The existing `site.example.yaml` omits the feature and preserves its previous
deployment behavior. The default `site.example.yaml` installs no schedule; deploying the separate
backup example would require supplying its real private prerequisites first.

## Protect managed volumes explicitly

With root backup selected, include each authoritative managed volume by property
presence. The following is a **guest volume fragment**, not a site:

```yaml
volumes:
  application:
    storage: local
    slot: 0
    path: /srv/example-application
    size_gib: 8
    backup:
  cache:
    storage: local
    slot: 1
    path: /srv/example-cache
    size_gib: 2
```

Native full-guest backup includes `application` and excludes `cache`. App storage
bindings reuse these paths; profiles never repeat the site's filesystem roots.
An app's authoritative role cannot use an unmarked managed volume when this
feature is selected. Transient material sharing a protected volume can still be
part of the full native volume backup; the selected-recovery catalogue is a
different, narrower tier. Use separate volumes when exclusion matters to size.

## What each deployment does

`Prepare` installs `proxmox-backup-client=4.2.8-1` from the official Debian Trixie
client-only repository using its digest-pinned public signing asset. A separate
`PBS agent` step records `/etc/homelab-backup/coverage.json` as root-only
configuration and checks the client binary. PBS uses a command-line client;
this does not require an always-running guest daemon.

The client-only repository uses Proxmox's documented HTTP APT endpoint.
Its signed release metadata and package hashes are verified against the
digest-pinned official Trixie keyring, and the client version is exact. This
authenticates package contents; it does not encrypt package-download traffic.
The keyring retains the vendor's two published archive keys. No `trusted=yes`,
insecure APT option or disabled certificate check is used. See the vendor's
[client repository and SecureApt guidance](https://pbs.proxmox.com/docs/installation.html#proxmox-backup-client-only-repository).

The coverage record includes the guest identity, configuration paths, each
bound storage role, individually owned runtime files, related database
endpoints and native full-volume inclusion flags. Every library storage role
has an explicit include or exclusion disposition. The compiler refuses missing
classifications; optional unbound roles need no invented host path.

With root monitoring also selected, the framework adds the Zabbix agent's
configuration, existing PSK and successful ownership receipt to each guest's
inventory. Downloaded package caches are reproducible. Controller credentials
and failed-operation records still require separate protected custody.

## Database and application consistency

Database guests still have settings to protect: PostgreSQL's `/etc/postgresql`,
MariaDB's `/etc/mysql` and InfluxDB's `/etc/influxdb`. Their live engine directories
are catalogued as requiring `database-export`, with `include: false` for selected
file capture. The [coverage guide](reference/backup-coverage.md#native-databases)
defines the required native recovery sets. Full-guest backups are additional
protection, not a substitute for these exports.

With `backup.job`, PostgreSQL uses installed-major `pg_dumpall` with globals,
MariaDB uses an all-database logical dump under an explicitly selected read lock,
and Influx uses its native full backup with a selected private operator token.
The native settings paths come from the framework's owning native adapter; profiles
do not repeat them.

An `application-export` role uses a coherent stop/capture/start window, requiring
its app in `job.capture.pause`. That permission covers only the app's existing
Compose services, including owned sidecars. Every member preflights before any
app pauses; native exports and app files are captured while all selected writers
are quiescent. Services resume before encrypted upload. No radio/NVM command,
container recreation, playback or synthetic device action forms part of capture.
A common recovery-set manifest binds exact related database/file generations.
This is a coordinated window, not a distributed transaction or verified restore.

## First installation and later deployments

Selecting the feature adds client software and the named step to the existing
guest job. It does not change job names, scheduling dependencies, app identities,
service data or credentials. Ordinary holds, input integrity and source review
remain enforced. A repeat deployment reuses the sealed preparation payload;
changed coverage becomes a new desired input generation.

Configured but disabled guests remain represented in source coverage. They do
not execute CD, and skipping them is not retirement. Removing a commissioned `job`, changing its stable group/member identity or
omitting an existing protected member refuses; explicit retirement is separate.
No ordinary update deletes history or downgrades recurring protection.

## Bind an operational job

Follow the complete [synthetic job](../site.backup.example.yaml) and its
[dedicated-volume guest](../examples/backup/guests/resolver.yaml). The framework
reference documents every nested `job` field; this library does not add a second
schema. Reuse an existing external endpoint, guest interface, volume and
file-secret source rather than repeating IPs, paths or credentials.

- Select one client entry per configured guest, including CD-disabled members.
  Each uses a unique scoped PBS token identity and existing encryption key.
- Select a dedicated staging volume without `backup:` and without app bindings.
  Its capacity is at least four times the per-generation byte limit. Append a
  new slot after existing volumes on owned updates; do not reorder/resize old
  storage. Source guards refuse foreign/nonempty mount preimages.
- Select the intended backup interface and an explicit network policy for the
  PBS endpoint. Runtime route admission rejects management-path fallback.
- Grant service pauses only to required apps; list every MariaDB producer in
  `database_lock` and every Influx producer/token reference in `influx_tokens`.
  Database consumers still use existing connections; backup adds no CD DAG edge.
- Schedule UTC `hourly`, `daily` or `HH:MM`, with bounded jitter, file count,
  bytes and duration. One controller timer coordinates all members under the
  existing CD locks. It reads their actual completed deployed generations;
  an app skipped in the latest CD does not lose protection.

CD installs the sealed worker inputs and schedule, but does not execute a backup.
The scheduled cycle captures native exports and declared files, uploads with
client encryption, restores the exact archive into private temporary readback,
and compares the complete artifact hashes. Every member must succeed before the
root recovery set is complete. Failed payloads, pending records, controller holds
and prior successes are preserved; no automatic recovery or remote pruning is
installed. Successful temporary copies are released only after exact readback.

## Later site integration and actual qualification

This public implementation does not create the NAS-hosted PBS VM, datastore,
namespace, account, key, native PVE full-guest schedule or server retention,
verification/prune/GC/offsite job. Those need concrete private allocations and
permissions when that phase is requested. Guest tokens need upload/readback for
their own namespace, not datastore administration or pruning.

Before declaring protection, verify a real scheduled cycle on the intended
network, native database content, related application/database manifests, archive
readback and an isolated service restore. Keep encryption keys independently
recoverable. Offsite recovery requires a complete consistent datastore and its
keys; copying namespace folders alone is insufficient.

New profiles follow [Contributing](contributing.md) and classify every storage
role in the [profile template](templates/application-profile.md). Extend a native
capture recipe in its owning framework adapter when needed; never put arbitrary
commands in a reusable profile. Test component failures directly, mock collaborators
in app/guest units, and retain focused real compiler/packet integrations.

Product references: [PBS client usage](https://pbs.proxmox.com/docs/backup-client.html)
and [official client repository](https://pbs.proxmox.com/docs/installation.html#proxmox-backup-client-only-repository).
