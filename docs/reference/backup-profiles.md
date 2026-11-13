# PBS client backup profile

[Reference index](README.md) · [Configure PBS backups](../backup.md) · [Application recovery coverage](backup-coverage.md)

The `pbs-client` profile selects the Proxmox Backup Client and lists guest configuration that its recovery inventory must include. It does not create a PBS server, supply credentials or install a schedule on its own. The site chooses the profile and, when ready, supplies an operational job through the [framework backup contract](https://github.com/theaussiepom/homelab/blob/0394051c59602efad1c4b1fb26c3ecef9107c04b/docs/reference/backup.md).

## Selection and field meaning

This library registers one backup profile in [stack.json](../../stack.json), using the complete [backup/pbs-client.yaml](../../backup/pbs-client.yaml) definition. Adding bare `backup:` at site root selects shared defaults; each guest needs its own `backup:` marker to install the client. `backup: null`, `backup: {}` and `backup: {profile: pbs-client}` make the same shared profile selection. Omitting the root field does not add client preparation. Booleans are not accepted. None of these forms installs a timer without an explicit `backup.job`.

With an operational job, the site may share interface and staging-volume names through `backup.defaults`. Each guest's enrollment marker inherits them; a guest `backup:` object may override `interface`, `staging_volume`, `backup_id` and `limits`. The compiler derives the client set from explicit guest enrollment, including disabled members. Root defaults never enroll other guests. Missing interface or volume references refuse instead of selecting a fallback. Without a job, use the preparation-only bare, null or empty guest marker; operational bindings are not ignored.

| Field | Meaning and constraints |
| --- | --- |
| `type` | Required; exactly `pbs-client`. It does not select an arbitrary agent or command. |
| `software` | Required nonempty list of unique software IDs. The selected definitions must provide exactly one versioned `proxmox-backup-client` package. This profile selects the [shared PBS software definition](software-and-runtime.md#registration-software-pbs-client). |
| `configuration` | Required named map, which may be empty. Each entry has a required canonical absolute `path` other than `/` and a required `kind` of `file` or `directory`. These are guest recovery paths, not files read during compilation. |

The [configuration records](#declaration-configuration) below select the hostname, hosts file and SSH directory. When root monitoring is also selected, the framework adds its managed Zabbix agent configuration, pre-shared key and ownership receipt. The [framework profile rules](https://github.com/theaussiepom/homelab/blob/0394051c59602efad1c4b1fb26c3ecef9107c04b/docs/reference/backup.md#backup-profiles) define those reserved paths and reject conflicting selections.

## Complete example and deployment effects

The [complete operational site](../../site.backup.example.yaml) and its [guest declaration](../../examples/backup/guests/resolver.yaml) supply the destination, management-secret reference, synthetic public recovery key, explicit guest enrollment, transfer policy, schedule and dedicated staging volume. Use the [offline command](../backup.md#run-the-complete-offline-example) to resolve that source and generate deployment inputs without contacting PBS or reading secrets. The example includes a job; bare profile selection is preparation only.

The operational example declares the shared bindings once and keeps its guest marker bare. [Size clients independently](../backup.md#size-clients-independently) replaces that marker with a tested limits override while preserving the same backup ID, staging volume, interface and shared timeout. No authored client list is generated or copied into the site.

For an enrolled guest this profile supplies client software and coverage; an operational job also installs its worker and controller schedule. Complete the framework’s [setup prerequisites and expected sequence](https://github.com/theaussiepom/homelab/blob/fb99e9d3225858686d277e225b47e18ac76d9ad5/docs/backup/configure.md#review-the-generated-change) and [credential placement](https://github.com/theaussiepom/homelab/blob/fb99e9d3225858686d277e225b47e18ac76d9ad5/docs/backup/access.md#what-goes-where) before deployment. The [library guide](../backup.md#first-installation-and-later-deployments) retains this example’s selection and compatibility limits.

Later deployments preserve identities, credentials and failure evidence. Changed coverage needs genuine guest readiness; ordinary CD does not retire a commissioned job. Follow the [retirement contract](https://github.com/theaussiepom/homelab/blob/fb99e9d3225858686d277e225b47e18ac76d9ad5/docs/reference/backup.md#later-deployments-and-retirement). Source checks do not verify capture, readback or service restoration.

## Declaration records

These are all supplied fields in [backup/pbs-client.yaml](../../backup/pbs-client.yaml) after the loader removes `schema` and `kind`. `object` introduces nested fields. These are reusable definition values; the site supplies only the controls allowed by the [backup contract](https://github.com/theaussiepom/homelab/blob/0394051c59602efad1c4b1fb26c3ecef9107c04b/docs/reference/backup.md#syntax). [Declaration records](declaration-records.md) explains the notation and source comparison.

| Declaration path | Selected value |
| --- | --- |
| <a id="declaration-type"></a>`type` | `"pbs-client"` |
| <a id="declaration-software"></a>`software` | `["pbs-client"]` |
| <a id="declaration-configuration"></a>`configuration` | `object` |
| <a id="declaration-configuration-hostname"></a>`configuration.hostname` | `object` |
| <a id="declaration-configuration-hostname-path"></a>`configuration.hostname.path` | `"/etc/hostname"` |
| <a id="declaration-configuration-hostname-kind"></a>`configuration.hostname.kind` | `"file"` |
| <a id="declaration-configuration-hosts"></a>`configuration.hosts` | `object` |
| <a id="declaration-configuration-hosts-path"></a>`configuration.hosts.path` | `"/etc/hosts"` |
| <a id="declaration-configuration-hosts-kind"></a>`configuration.hosts.kind` | `"file"` |
| <a id="declaration-configuration-ssh"></a>`configuration.ssh` | `object` |
| <a id="declaration-configuration-ssh-path"></a>`configuration.ssh.path` | `"/etc/ssh"` |
| <a id="declaration-configuration-ssh-kind"></a>`configuration.ssh.kind` | `"directory"` |
