# Prepare PBS clients

[Documentation index](README.md) · [Application coverage](reference/backup-coverage.md) ·
[Software selection](reference/software-and-runtime.md)

Add the bare `backup` property at site root to prepare the PBS client in every
guest. It is a presence-based feature, like root monitoring; do not write
`backup: true`. Apps retain their independent profiles and placement.

```yaml
backup:
```

The library registers one `pbs-client` backup profile. An explicit equivalent is
`backup: {profile: pbs-client}`. The [selected framework backup contract](https://github.com/theaussiepom/homelab/blob/dbca1f93f434c70d97f99df845972a3c467f6fc3/docs/reference/backup.md) owns validation,
compilation, phase execution and the language contract. This library owns the
client package/repository definition and each app's recovery classification.

## Run the complete offline example

Use the `FRAMEWORK`, `STACK` and `PYTHON` paths from
[First configuration](guides/first-configuration.md):

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" \
  --stack "$STACK" --site "$STACK/site.backup.example.yaml" --check
```

This complete synthetic resolver source requires no PBS server. It exercises
client selection and coverage compilation, not a backup or production deployment.
The existing `site.example.yaml` omits the feature and preserves its previous
deployment behavior. No default example activates a live schedule.

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

App state uses `application-export`. That is a **capture requirement**, not proof
that a producer exists or that copying the live directory is coherent. Before
activation, each producer must supply a supported consistent generation.
Neither this source feature nor ordinary CD stops an app or a radio to capture
it. Related database connections identify recovery dependencies, without adding
deployment ordering or claiming cross-service transactional snapshots.

## First installation and later deployments

Selecting the feature adds client software and the named step to the existing
guest job. It does not change job names, scheduling dependencies, app identities,
service data or credentials. Ordinary holds, input integrity and source review
remain enforced. A repeat deployment reuses the sealed preparation payload;
changed coverage becomes a new desired input generation.

Configured but disabled guests remain represented in source coverage. They do
not execute CD, and skipping them is not retirement. Removing `backup` does not
uninstall the client, remove a backup job or delete historical protection.

## Later site integration

This release prepares clients and records recovery requirements. It does not
create a NAS-hosted PBS server, datastore, export, token or key; activate timers;
run capture/upload/prune/GC; or claim a recovery point. Destination binding,
schedules, retention and encryption are deliberately absent from this phase's
accepted root object. They are not arbitrary optional fields to invent.

The future private deployment must qualify the NAS server separately, scoped
guest identities, native producers, complete immutable generations, encryption
and independent key recovery, scheduled transfer/readback, capacity and isolated
restores. Preserve existing successful generations on capture or transfer failure.
Offsite recovery requires a complete, consistent datastore/native set and its
keys; copying only PBS namespace folders is insufficient.

New profiles follow [Contributing](contributing.md) and classify every storage
role in the [profile template](templates/application-profile.md). Unknown fields,
Boolean enrollment, unsafe live-state capture declarations and missing protected
volume markers fail at the framework boundary. Library units check selections;
real compiler tests check composition. Source success does not prove live backup
or application recovery.

Product references: [PBS client usage](https://pbs.proxmox.com/docs/backup-client.html)
and [official client-only repository](https://pbs.proxmox.com/docs/installation.html#proxmox-backup-client-only-repository).
