# PBS client backup profile

[Reference index](README.md) · [Configure PBS backups](../backup.md) · [Application recovery coverage](backup-coverage.md)

The `pbs-client` profile selects the Proxmox Backup Client and lists guest configuration that its recovery inventory must include. It does not create a PBS server, supply credentials or install a schedule on its own. The site chooses the profile and, when ready, supplies an operational job through the [framework backup contract](https://github.com/theaussiepom/homelab/blob/693c6ce4126ab31d53ee992457bd5c45c1398cea/docs/reference/backup.md).

## Selection and field meaning

This library registers one backup profile in [stack.json](../../stack.json), using the complete [backup/pbs-client.yaml](../../backup/pbs-client.yaml) definition. Adding bare `backup:` at site root selects it. `backup: null`, `backup: {}` and `backup: {profile: pbs-client}` make the same preparation selection. Omitting the root field does not add client preparation. Booleans are not accepted. None of these forms installs a timer without an explicit `backup.job`.

| Field | Meaning and constraints |
| --- | --- |
| `type` | Required; exactly `pbs-client`. It does not select an arbitrary agent or command. |
| `software` | Required nonempty list of unique software IDs. The selected definitions must provide exactly one versioned `proxmox-backup-client` package. This profile selects the [shared PBS software definition](software-and-runtime.md#registration-software-pbs-client). |
| `configuration` | Required named map, which may be empty. Each entry has a required canonical absolute `path` other than `/` and a required `kind` of `file` or `directory`. These are guest recovery paths, not files read during compilation. |

The [configuration records](#declaration-configuration) below select the hostname, hosts file and SSH directory. When root monitoring is also selected, the framework adds its managed Zabbix agent configuration, pre-shared key and ownership receipt. The [framework profile rules](https://github.com/theaussiepom/homelab/blob/693c6ce4126ab31d53ee992457bd5c45c1398cea/docs/reference/backup.md#backup-profiles) define those reserved paths and reject conflicting selections.

## Complete example and deployment effects

The [complete operational site](../../site.backup.example.yaml) and its [guest declaration](../../examples/backup/guests/resolver.yaml) supply the destination, file-secret references, transfer policy, schedule and dedicated staging volume. Use the [offline command](../backup.md#run-the-complete-offline-example) to resolve that source and generate deployment inputs without contacting PBS or reading secrets. The example includes a job; bare profile selection is preparation only.

At first deployment, `Prepare` installs the selected client software. The `PBS agent` step records recovery coverage and, if a job is selected, installs its protected worker inputs and controller schedule. It does not execute a backup during deployment. Before enabling an operational job, prepare and review the existing server namespaces, keys, credentials, network access and any permission to pause services.

Later deployments preserve the existing credentials, group and member identities, successful recovery records and unresolved failure holds. Changed coverage becomes a new protected input generation. A previously commissioned operational job cannot be removed or reduced to preparation only through an ordinary update. Follow [later-deployment and retirement rules](https://github.com/theaussiepom/homelab/blob/693c6ce4126ab31d53ee992457bd5c45c1398cea/docs/reference/backup.md#later-deployments-and-retirement); this contract provides no automatic retirement executor. Successful source checks do not verify capture, readback or a service restore.

## Declaration records

These are all supplied fields in [backup/pbs-client.yaml](../../backup/pbs-client.yaml) after the loader removes `schema` and `kind`. `object` introduces nested fields. These are reusable definition values; the site supplies only the controls allowed by the [backup contract](https://github.com/theaussiepom/homelab/blob/693c6ce4126ab31d53ee992457bd5c45c1398cea/docs/reference/backup.md#syntax). [Declaration records](declaration-records.md) explains the notation and source comparison.

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
