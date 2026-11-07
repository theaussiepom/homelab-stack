# Share or separate guests

[Documentation index](../README.md) · [Examples](../examples/README.md)

Placement is a site choice, subject to actual app ownership and listener/resource contracts. Moving YAML between files does not move data or a running service.

## One app is useful on its own

The [minimal site](../../site.example.yaml) contains one Unbound app. Pi-hole is not forced. The [alternate site](../../examples/site.second.yaml) includes HA without Node-RED or any unselected integration. WiNet and Zigbee are independent profiles; WiNet does not inherit a serial capability.

## Repeat a supported profile

The alternate source declares `local_primary`, `local_backup` and `remote_primary`. The [two local instances](../../examples/second/apps/) share a guest while selecting distinct loopback publications; the remote instance lives on a separate guest.

| Instance | Placement | Publication |
| --- | --- | --- |
| local_primary | resolver-east | loopback port 5335 |
| local_backup | resolver-east | loopback port 5336 |
| remote_primary | resolver-west | loopback port 5335 on that other guest |

The instance ID, derived or explicit runtime/service/project/network identities and sockets are distinct. `properties.publish_port` changes both guest-loopback TCP/UDP ports while the private container listener remains port 53. A cosmetic display label is not an identity override.

## Share a Compose project explicitly

A guest may declare named `compose_projects`, and retained app identities bind to the selected project and owned service roles. Helpers remain with their app: CloudBeaver owns its auth gateway; Explorer owns its gateway; Authentik owns server/worker/Redis. Shared project membership is not a dependency and does not authorize restarting peers.

The compiler rejects overlapping service/network identities, writable storage namespaces and incompatible publications. Native service definitions also reject conflicts between fixed unit names, configuration paths and accounts. PostgreSQL and MariaDB can pass these checks together; PostgreSQL and InfluxDB currently use a conflicting fixed group identity. Having enough memory alone does not establish that two services can share a guest.

## Know the limits

- Unbound and namespace-aware Cloud/Explorer helpers have focused repeated-instance source/helper tests.
- Pi-hole has one fixed managed-record sidecar per guest.
- Zigbee supports one registered serial coordinator per guest and uses fixed settings and identity files.
- Fixed host listeners, such as HA on 8123, Node-RED on 1880 and MQTT on 1883, prevent an identical co-located listener.
- Native services keep their supported conventional unit/data/config layouts; there is no setting for moving multiple clusters between these locations.

Consult each [profile page](../reference/README.md). Distinct writable mounts, credential owners and custody paths remain necessary even where listener placement is valid. Source/helper support is not a claim that every same-guest combination has been deployed.

## Change placement safely

A new source layout can choose different placement for a new owned instance. An ordinary update of an installed app cannot silently relocate its stable identity, storage, project or credentials. Review the resolved plan and the affected instance's support before a change; a refused ownership move is not repaired with `lifecycle: fresh`.
