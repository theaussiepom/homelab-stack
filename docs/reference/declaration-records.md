# Read a declaration record

[Reference index](README.md) · [Conformance scope](../testing.md#documentation-conformance) · [Composition](../guides/compose-a-site.md)

Every registered profile and template has an exact **Declaration records** section. It inventories the complete supplied definition loaded through the real library source loader. The associated human sections explain placement, binding, lifecycle and effective requirements. A declaration's selected value is not a promise that every site instance can override it.

## Notation and coverage

`interfaces.backend.required` is the `required` field of the selected profile's named `backend` role. Dynamic role names are declaration identities, not new framework field types. `object` introduces a nonempty mapping whose children have their own records; `{}` means an explicitly empty mapping. JSON-formatted scalar/sequence cells preserve actual types: `false` is a boolean, `50` an integer, and `"50"` a string. Sequence order is preserved. Definition markers `schema` and `kind` are shown by the source document; the loader removes them before typed definition validation.

These tables cover supplied profile/template fields. The test-local map links each registered definition to its source and document; it does not repeat field lists. The checker derives fields from the real loaded definition and independently reads the authored table, comparing the two in both directions. They do **not** enumerate every optional field accepted by the framework, every procedural conditional rule, or every application property. The selected framework's [library grammar](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/library.md), [supporting types](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/supporting-types.md) and [app properties](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/app-properties.md) own that wider surface. New framework conditions still need review.

## Follow the selected field to its effect

| Declaration group | Consumer relationship and canonical owner |
| --- | --- |
| `adapter`, `display_name` | Adapter selects typed behavior and owned services; the label does not rename persistent identity. See [app instances](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/apps.md). |
| `interfaces` | Each named role states presence and allowed scope; site bindings select a NIC within the app's guest, guest loopback or a declared app network only where allowed. See [interface composition](../guides/multiple-interfaces.md) and [role types](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/supporting-types.md#profile-interface-listener-and-endpoint-types). |
| `listeners`, `endpoints` | Listener names select the socket/namespace/publication; endpoint names advertise derived values. A wildcard host socket can exceed its advertised NIC. See [connection composition](../guides/connect-apps.md) and [listener types](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/supporting-types.md#profile-interface-listener-and-endpoint-types). |
| `storage` | Required/optional roles bind explicit guest volumes/root paths and confined subpaths; a target is the container path, not a controller path. Create-only initialization never adopts an existing directory. See [storage bindings](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/storage.md#app-storage-bindings). |
| `connections` | Type and permitted readiness/account modes constrain a separately authored connection. Allowed readiness is not an automatic dependency; values grant no traffic. See [connect apps](../guides/connect-apps.md). |
| `properties` | Direct profile property keys supply defaults; explicit instance keys replace them. The selected adapter owns conditional fields and constraints; no generic recursive overlay exists. See [property types](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/app-properties.md). |
| `secrets`, `authentication` | Metadata declares private-input/reference roles. Effective adapter requirements can be stricter, as [MQTT's file probe](apps/mqtt.md#mqtt-probe) demonstrates. See [secret custody](../secrets.md). |
| `devices` | Selects a typed required/optional device role; the site owns the concrete device and qualified access. Source resolution does not verify hardware. See [Zigbee2MQTT](apps/zigbee2mqtt.md). |
| `software`, `runtime`, `health`, `monitoring` | Names resolve in the [shared catalogue](software-and-runtime.md); software and runtime selections aggregate under framework rules. A declared readiness check is not observed service readiness. |
| Template `resources`, `startup`, `security` | Complete defaults with direct-key guest replacement, subject to runtime/execution floors. See [templates](templates.md#override-and-change-effects). |

## Omission, null and empty

A profile's missing optional block is interpreted by the actual typed owner; it does not authorize a site input of null. An optional role may become required when a capability is selected. For example, MQTT's `secrets.probe.required` is false metadata while the adapter's file-source floor is mandatory. Consult the profile's binding section before applying a raw flag.

A supplied empty mapping or sequence is recorded explicitly. Template empty partial-map inheritance and list appends are documented at [template precedence](templates.md#override-and-change-effects). Site authoring remains a closed typed contract; these records do not add arbitrary environment, command, Compose, mount or configuration passthrough.

## Evidence and review

[Tests](../testing.md#documentation-conformance) compare typed cells and source paths, reject orphan/new/missing/duplicate records, and exercise real MQTT/Docker behavior. All registered profiles retain complete resolver/lowerer examples. Native service acceptance, semantic completeness, and the usefulness of explanation remain separate review responsibilities under the [documentation standard](../contributing/documentation-standard.md).
