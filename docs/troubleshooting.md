# Troubleshoot a composition

[Documentation index](README.md) · [Tests](testing.md)

Start with the failed layer. A source error, workflow dependency, package/service health failure, DNS/TLS route and browser login are different facts. Keep the exact selected revisions and failed output; do not infer a broker/database failure from an unclassified UI error.

| Symptom / diagnostic | Check | Safe next step |
| --- | --- | --- |
| component.fields / component.properties | Wrong kind, unknown key, missing app-specific property or an incomplete source reference | Use the profile page and canonical type; do not add an override bag |
| component.reference / component.connection-required | Wrong map key, missing endpoint/role or selected required connection | Follow the reference chain; app roles name NIC bindings, not addresses |
| component.source | Escape/symlink, ambiguous YAML/JSON siblings, wrong typed header or missing complete file | Keep one confined logical file and correct kind; no recursive include/overlay |
| component.memory-budget | Selected container/native reservations plus effective OS reserve exceed guest memory | Review template/app resource allocations; do not call the numbers measured usage |
| component.listener-conflict / placement refusal | Actual socket, namespace or service identity overlaps | Use supported distinct placement/identities; an endpoint advertisement is not isolation |
| component.readiness-cycle / disabled dependency | Explicit dependency cycle or missing selected producer | Fix actual intended ordering, not by removing a safety gate |
| component.synthetic-binding / image-binding | Example allocations, empty keys or unresolved archive sentinels in admitted source | Supply the consuming site's qualified facts; source-only examples are not deployment inputs |
| Retained owner / private material refusal | Changed canonical/static/AppPayload/backend, storage owner or credential material | Preserve current and failed evidence; use the site's reviewed procedure, never a fresh flag/adoption waiver |
| HOLD / pending / same-run refusal | Interrupted or foreign attempt, changed binding/state, consumed run | Stop automatic replay. Preserve exact records; a new Git commit is not hold-release authority |
| Generated workflow stale | Source/model/ref differs from committed generated body | Run the real generator from the selected source; do not hand-edit generated jobs |
| Source passes but service fails | Actual native logs/status, selected image/config, health/auth/route layer | Diagnose the actual failed boundary through the site's authorized read path |

Exact codes and nested property paths come from the selected framework. This table groups common causes; a refusal remains authoritative even when its wording differs.

## App-specific checks

- [Unbound](reference/apps/unbound.md): loopback service role, publish_port, no fresh empty config mount.
- [Pi-hole](reference/apps/pihole.md): required upstream role/target and exact previous-owned DNS selection.
- [CloudBeaver](reference/apps/cloudbeaver.md): gateway-only publication, owned workspace, OIDC and selected database/driver capability.
- [Explorer](reference/apps/mqtt_explorer.md): required outpost, exact selected broker target/alias, account or existing credential and saved-profile ownership.
- [Node-RED](reference/apps/node_red.md): correct public/custom variant, retained wrappers and auth strategy.
- [Bitwarden](reference/apps/bitwarden.md): immutable official image and preserved private environment/database/installation ownership.
- [Zigbee](reference/apps/zigbee2mqtt.md): registered coordinator and unchanged network evidence; never initialize a coordinator to make health pass.

Use [source checks](testing.md) to establish a reproducible source defect. Container startup, protocol fixtures and a green sub-job do not establish target service acceptance. No command on this page changes a target or grants a retry.
