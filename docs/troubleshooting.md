# Troubleshoot a composition

[Documentation index](README.md) · [Tests](testing.md)

Start with the failed layer. A source error, workflow dependency, package or service failure, DNS lookup, TLS route and browser login each need their own evidence. Keep the exact selected revisions and failed output; do not infer a broker or database failure from an unclassified UI error.

| Symptom / diagnostic | Check | Safe next step |
| --- | --- | --- |
| component.fields / component.properties | Check the declared kind, unknown keys, required app properties and whether a source reference contains a complete declaration. | Correct the input using the profile page and canonical type. Arbitrary override settings are not accepted. |
| component.reference / component.connection-required | Check the referenced map keys, endpoints and roles, and whether each selected required connection exists. | Follow each reference to its declaration. A physical app role must bind to a named guest NIC, not a literal address. |
| component.source | Check for a path outside the source root, a symlink, competing YAML or JSON files with the same stem, a wrong type header or a missing complete file. | Keep one complete file of the correct kind within the source root. Recursive includes and partial overlays are unsupported. |
| component.memory-budget | Add the memory reserved for containers, native services and the operating system, and compare it with guest memory. | Adjust the template or app allocations within their supported limits. Reservations are requirements, not measured usage. |
| component.listener-conflict / placement refusal | Check whether listeners use the same address and port in the same network namespace, or services use the same identity. | Choose a supported placement with distinct identities and listeners. Advertising a different endpoint does not isolate an existing listener. |
| component.readiness-cycle / disabled dependency | Follow the explicit dependencies and check for a cycle or a required producer that is missing or disabled. | Correct the intended order or required selection. Do not remove a safety check to make the configuration pass. |
| component.synthetic-binding / image-binding | Check for example allocations, empty keys or placeholder archive values in source intended for deployment. | Supply the actual allocations, public keys and image inputs that you have verified for your site. Offline examples cannot serve as deployment inputs unchanged. |
| Retained owner / private material refusal | Compare the pointer to the latest successful receipt, fixed deployment inputs, protected app payload (AppPayload), backend, storage owner and existing credentials with their recorded values. | Preserve both current and failed evidence and follow the site's reviewed failure procedure. Selecting fresh cannot repair ownership or authorize adoption. |
| HOLD / pending / same-run refusal | Check whether the attempt was interrupted, belongs to another operation, has changed inputs or state, or has already used its run identity. | Stop automatic retries and preserve the exact records. A new Git commit does not authorize releasing a hold. |
| Generated workflow stale | Compare the selected source, resolved model and source revision with those used to generate the committed workflow. | Run the workflow generator from the selected source. Do not hand-edit generated jobs. |
| Source passes but service fails | Inspect the running service's logs and status, selected image and configuration, then distinguish health, authentication and routing failures. | Use the site’s authorized read-only diagnostic procedure to identify the failing operation. Passing source checks does not establish the cause. |

Exact codes and nested property paths come from the selected framework. This table groups common causes; a refusal remains authoritative even when its wording differs.

## App-specific checks

- [Unbound](reference/apps/unbound.md): check the loopback service role and publish_port. A new instance must not mount an empty configuration directory.
- [Pi-hole](reference/apps/pihole.md): check the required upstream role and target. Changes to existing managed DNS records must match the exact records owned by the previous deployment.
- [CloudBeaver](reference/apps/cloudbeaver.md): publish only the gateway. Check the HomeLab-managed workspace, OpenID Connect authentication, and selected database and driver capabilities.
- [Explorer](reference/apps/mqtt_explorer.md): check the existing authentication outpost, selected broker target and alias, managed account or existing credential, and ownership of the saved profile.
- [Node-RED](reference/apps/node_red-custom.md): choose the correct public or custom-image variant. The existing-installation profile requires its settings and health-check scripts and authentication setup.
- [Bitwarden](reference/apps/bitwarden.md): check the immutable official image and preserve the existing private environment, database and installation ownership.
- [Zigbee](reference/apps/zigbee2mqtt.md): check the registered coordinator and the records preserving the existing network identity; never initialize a coordinator to make health pass.

Use [source checks](testing.md) to establish a reproducible source defect. Container startup, protocol fixtures and a green sub-job do not establish target service acceptance. No command on this page changes a target or grants a retry.

## MQTT probe refusal

`component.secret-required at apps.broker.properties` can mean the broker's probe role is missing or names a non-file source. This is the selected MQTT adapter's effective requirement even though profile metadata says optional. Follow [Probe binding](reference/apps/mqtt.md#mqtt-probe), restore the valid file-source reference in the [complete broker entry](reference/apps/mqtt.md#complete-broker-entry), then resolve the complete source and generate its deployment files. The adapter reports its properties context; do not infer that a literal `properties.probe` field exists. Source checks do not read the probe record or prove broker authentication.
