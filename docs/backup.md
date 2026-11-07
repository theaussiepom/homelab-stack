# Configure PBS backups

[Documentation index](README.md) · [PBS client profile](reference/backup-profiles.md) · [Application coverage](reference/backup-coverage.md) · [Software selection](reference/software-and-runtime.md)

HomeLab can prepare the Proxmox Backup Client in your guests and, with an explicitly configured job, install a coordinated backup schedule. The library supplies the client software and classifies application data. Your site supplies the existing PBS destination, protected credentials, network access and permission to pause selected services. Source compilation does not run a backup or prove that an application can be restored.

## Select client preparation

Add the bare `backup` property at site root. This is a **site-root fragment**, not a complete site:

```yaml
backup:
```

This library registers one [pbs-client profile](reference/backup-profiles.md). `backup: null`, `backup: {}` and `backup: {profile: pbs-client}` select the same profile. The property’s presence enables client preparation; `backup: true` and `backup: false` are rejected. Omitting the root property adds no client phase and leaves existing provider volume defaults unchanged. Apps keep their independently selected profiles and placement.

Bare profile selection installs no timer and assumes no destination, credential or permission to interrupt a service. Add `backup.job` only when its inputs are prepared. The [selected framework backup contract](https://github.com/theaussiepom/homelab/blob/015e202a99037f642671c20ead2acb8eb972a331/docs/reference/backup.md) defines validation, generated deployment inputs, coordinated capture and execution. The library owns its client package and repository selection and each app’s recovery classification.

## Run the complete offline example

Use the `FRAMEWORK`, `STACK` and `PYTHON` paths from [First configuration](guides/first-configuration.md):

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" \
  --stack "$STACK" --site "$STACK/site.backup.example.yaml" --check
```

The [complete synthetic resolver site](../site.backup.example.yaml) includes an operational job with a PBS endpoint, file-secret references, UTC schedule, explicit transfer policy and dedicated staging volume. Offline compilation requires no PBS server and opens no secret files. It checks the composition and generated deployment inputs; it does not install a schedule or execute a backup. The default `site.example.yaml` omits backup entirely and keeps its previous deployment behavior. Deploying the separate backup example requires replacing its invented inputs with the real, reviewed prerequisites.

## Protect managed volumes explicitly

With root backup selected, add `backup:` to each managed volume that contains authoritative application data. The following is a **guest volume fragment**, not a site:

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

The generated native full-guest backup flags include `application` and exclude `cache`. A volume marker also accepts null or an empty object, but not a Boolean. App bindings reuse the declared paths; profiles do not repeat the site’s filesystem roots. With root backup selected, an authoritative app role cannot use an unmarked managed volume. This also applies to a native database’s engine volume, whose coherent database export is a separate requirement.

Data excluded from selected application recovery may still be copied by a full native volume backup if it shares a protected volume. Use separate volumes when that exclusion matters to backup size. A root-filesystem path does not create another provider mount or a separate native backup flag.

## What each deployment does

`Prepare` installs the exact client version selected by [the shared software definition](reference/software-and-runtime.md#registration-software-pbs-client). The separate `PBS agent` step records `/etc/homelab-backup/coverage.json` as root-only configuration and checks the client binary. PBS uses a command-line client; no always-running guest daemon is required.

The client-only repository uses Proxmox’s documented HTTP APT endpoint. APT verifies signed release metadata and package hashes against the official Trixie keyring, whose bytes are checked against the library’s recorded digest. This authenticates package contents without encrypting package-download traffic. The keyring retains the vendor’s two published archive keys. HomeLab uses no `trusted=yes`, insecure APT option or disabled certificate check. See the vendor’s [client repository and SecureApt guidance](https://pbs.proxmox.com/docs/installation.html#proxmox-backup-client-only-repository).

The coverage record identifies the guest, configuration paths, bound storage roles, individually managed runtime files, related database endpoints and native full-volume inclusion flags. Every library storage role has an explicit inclusion or exclusion. The compiler rejects missing classifications; an optional role that is not bound produces no invented host path.

When root monitoring is also selected, the framework adds each guest’s Zabbix agent configuration, existing pre-shared key and successful ownership receipt. Downloaded package caches can be rebuilt. Controller credentials and failed-operation records still need separate protected recovery storage.

## Database and application consistency

Native database settings need protection alongside data: PostgreSQL uses `/etc/postgresql`, MariaDB `/etc/mysql` and InfluxDB `/etc/influxdb`. The framework’s native adapters supply these settings paths; profiles do not repeat them. Live engine directories are classified as `database-export` and recorded with `include: false` for selected file capture. The [native database recovery guide](reference/backup-coverage.md#native-databases) describes the required recovery sets. Full-guest backups provide additional protection and do not replace coherent database exports.

With `backup.job`, PostgreSQL uses its installed major version’s `pg_dumpall`, including globals. MariaDB dumps all databases under an explicitly selected read lock. InfluxDB uses its native full backup with a selected private operator token. A database connection from an app identifies the related database; it does not itself perform a backup.

An `application-export` role requires the app in `job.capture.pause`. This explicitly permits stopping and restarting only that app’s existing Compose services, including supporting containers. Every member completes its checks before any app pauses. All selected writers pause while native exports and app files are captured, and services resume before encrypted upload. Capture does not recreate containers, issue radio or non-volatile-memory commands, play media or send synthetic device commands.

A common recovery-set manifest records the exact related database and file generations. This establishes a coordinated capture window, not a distributed transaction or a verified restore. Writers outside the declared apps still need consideration when testing recovery.

## First installation and later deployments

Selecting backup adds client software and the named step to each enabled guest’s existing deployment job. It does not rename jobs, add dependencies between apps, change app identities or replace service data or credentials. Existing holds, protected-input checks and source review still apply. Repeat deployments reuse the protected preparation payload; changed coverage produces a new input generation.

Guests disabled for deployment remain in the source coverage and operational group. They do not run deployment steps, and skipping them does not retire their protection. Ordinary deployment rejects removal of a commissioned job, changes to its stable group or member identity, or omission of an existing protected member. Retirement requires a separate explicit procedure; this contract provides no automatic retirement executor. An ordinary update does not delete backup history or reduce an existing schedule to preparation only.

## Bind an operational job

Follow the [complete synthetic job](../site.backup.example.yaml) and its [dedicated-volume guest](../examples/backup/guests/resolver.yaml). The framework documents [every nested job field](https://github.com/theaussiepom/homelab/blob/015e202a99037f642671c20ead2acb8eb972a331/docs/reference/backup.md#operational-job). Reuse existing external endpoints, guest interfaces, volumes and file-secret sources instead of repeating addresses, paths or credentials.

- Select one client for every configured guest, including members disabled for deployment. Each needs its own scoped PBS token identity and existing encryption key.
- Select a dedicated staging volume with no app bindings and no `backup:` marker. Its capacity must be at least four times the per-generation byte limit. On an existing HomeLab-managed guest, append a new slot after the existing volumes; do not reorder or resize existing storage. Checks before applying the change reject a foreign mount, symlink or nonempty staging path.
- Select the backup interface and declare network access to the PBS endpoint. Before capture, the runtime checks that the route uses the selected device and source address; it rejects fallback to the management path.
- Permit pauses only for required apps. List every MariaDB producer in `database_lock` and each InfluxDB producer and token reference in `influx_tokens`. Existing database connections supply recovery associations without adding deployment dependencies.
- Choose UTC `hourly`, `daily` or `HH:MM` scheduling, with limits on jitter, file count, bytes and duration. One controller timer coordinates all members under the existing deployment locks. It reads each member’s actually completed deployment; skipping an app in the latest deployment does not remove its protection.

## Operational job example

This is the complete **site-root backup fragment** from the [canonical operational site](../site.backup.example.yaml). It still needs that site’s endpoint, file-secret sources, network policy and guest staging volume. The documentation checks compare this excerpt with the maintained source.

```yaml
backup:
  job:
    name: example-recovery
    destination:
      endpoint:
        external: pbs
      datastore: recovery
      namespace: guests
      fingerprint: ab:ab:ab:ab:ab:ab:ab:ab:ab:ab:ab:ab:ab:ab:ab:ab:ab:ab:ab:ab:ab:ab:ab:ab:ab:ab:ab:ab:ab:ab:ab:ab
    schedule:
      calendar: '02:00'
      jitter_seconds: 300
    clients:
      resolver:
        auth_id: resolver@pbs!backup
        password: pbs-password
        encryption_key: pbs-key
        staging_volume: backup-stage
        interface: primary
    capture:
      pause: []
      database_lock: []
      influx_tokens: {}
    limits:
      max_bytes: 33554432
      max_files: 10000
      timeout_seconds: 300
```

Deployment installs the protected worker inputs and controller schedule; it does not execute a backup. A scheduled cycle captures native exports and declared files, uploads with client encryption, downloads and decrypts the exact archive into a private temporary directory, and compares every artifact hash. The root recovery set succeeds only after every member completes those checks. Successful temporary copies are removed only after exact readback verification.

After the controller accepts every member’s deployment records, a worker’s failed check before capture leaves evidence under that run’s UUID without opening a capture window. A later scheduled run may try those checks again with a new UUID. Earlier lock or deployment-record checks can stop the run before its UUID directory exists.

Once a capture window opens, a failed run keeps any remaining controller holds. Pending markers and recovery files still present on failed members remain for investigation. Members that have already verified their archives may have released their temporary copies and local pending markers before the group fails. No automatic recovery, replay or clearing of remaining holds and markers is installed. The client does not prune remote snapshots, earlier failures or the last successful recovery generation. Follow the framework’s [execution and failure rules](https://github.com/theaussiepom/homelab/blob/015e202a99037f642671c20ead2acb8eb972a331/docs/reference/backup.md#coordinated-execution-and-failure-behavior).

## Invalid cases

These source checks start from the complete example or the volume fragment above. Root-level selection errors have no more specific field path in their diagnostic; do not infer one.

| Invalid input | Diagnostic | Supported correction |
| --- | --- | --- |
| Root `backup: true` or `backup: false` | `component.fields` | Use a bare, null or empty selection to prepare the client; omit the root field when no backup feature is selected. Removing an existing operational job still requires the separate retirement procedure. |
| Root `backup: {profile: missing}` | `component.backup-profile-selection` | Select a registered backup profile, or omit `profile` when the library has exactly one. |
| `backup: true` on the fragment’s `application` volume | `component.backup-presence` at `guests.resolver.volumes.application` | Use bare `backup:` or an empty object to include the volume. |
| Add `backup:` to the operational job’s staging volume | `component.backup-staging-volume` | Keep staging dedicated, unprotected by native volume backup and unbound by apps. |

Correct the source and rerun the offline check. These refusals do not inspect real credentials, mount contents or PBS access.

## Later site integration and actual qualification

This implementation does not create the NAS-hosted PBS VM, datastore, namespace, account, encryption key, native Proxmox full-guest schedule or server maintenance jobs for retention, verification, pruning, garbage collection or offsite copies. Those require the site’s actual allocations and permissions. Guest tokens need permission to upload and read back their own namespace’s archives, not to administer the datastore or prune history.

Before declaring protection, verify a real scheduled cycle on the intended network, native database contents, related application and database manifests, full archive readback and an isolated service restore. Keep encryption keys independently recoverable. Offsite recovery needs a complete consistent datastore and its keys; copying namespace folders alone is insufficient.

New profiles follow [Contributing](contributing.md) and classify every storage role using the [profile template](templates/application-profile.md). Extend a native capture implementation in its owning framework adapter when needed; reusable profiles cannot supply arbitrary commands. Test component failures directly, mock collaborators in app and guest unit tests, and retain focused integration tests using the real compiler and generated packets.

Product references: [PBS client usage](https://pbs.proxmox.com/docs/backup-client.html) and [official client repository](https://pbs.proxmox.com/docs/installation.html#proxmox-backup-client-only-repository).
