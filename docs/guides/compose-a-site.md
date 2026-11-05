# Compose a site

[Documentation index](../README.md) · [Catalogue](../reference/README.md)

Use this guide after the [source-only tutorial](first-configuration.md). Its `STACK`, `FRAMEWORK` and `PYTHON` variables refer to clean selected source checkouts and the isolated interpreter. A site supplies allocations; this library supplies requirements. Do not edit a profile to insert a real VMID, address, credential or installation history.

## 1. Choose independent apps

Select [profiles](../reference/README.md) by lifecycle and integrations. For example, the maintained [alternate site](../../examples/site.second.yaml) selects three `unbound` instances and one `homeassistant-public` instance. It does not select Node-RED, a database, MQTT, identity or ingress.

A profile is a reusable declaration in this library's `apps/`. A site's `apps` entry is a named instance of that profile. These are different document kinds.

## 2. Give each guest its facts

A complete guest chooses context, template, lifecycle, persistent VMID/hostname, template file, root storage, named NICs and control interface. Optional resource/startup/security fields inherit from the [template](../reference/templates.md). Declare extra volumes or supported root-filesystem data paths explicitly.

The [alternate HA guest](../../examples/second/guests/home-app.yaml) is a complete example. It needs more memory than the base default because the HA reservation and OS reserve must fit. Its named `apps` volume is not an app profile or a command to import existing data.

Physical NIC slots and MACs are persistent provider identity. One effective default route is required; a selected DHCP interface already contributes that route. Keep static secondary NICs explicit and do not infer a route from an app's web role.

## 3. Bind each app

The complete [HA instance](../../examples/second/apps/home.yaml) is:

```yaml
schema: homelab-components-v1
kind: app
profile: homeassistant-public
guest: home-app
lifecycle: fresh
interfaces:
  web:
    interface: primary
storage:
  config:
    volume: apps
    subpath: homeassistant
```

`home-app`, `primary` and `apps` refer to the complete guest above. The writable config initializer belongs to the public profile; it creates only the absent app subdirectory beneath the proved volume. It does not recursively change an existing directory's owner.

Roles omitted here are optional and unselected. Adding a recorder or broker connection requires its corresponding physical source role, selected endpoint and explicit network policy. It does not appear automatically because another app exists.

## 4. Keep source files complete

The site's root keeps stable map keys and can select complete typed files:

```yaml
guests:
  home-app:
    source: second/guests/home-app.yaml
apps:
  home:
    source: second/apps/home.yaml
```

This is the exact shape used by the alternate site. The path is relative to that site's file directory, not the referenced file's directory. The leaf has its own schema/kind and complete body. It is not a partial overlay, template or recursive include.

## 5. Select relationships deliberately

- [Interface roles](multiple-interfaces.md) identify the source/destination socket context.
- [Connections](connect-apps.md) select existing endpoints and optional explicit readiness/account/transport choices.
- Exposures select managed DNS or HTTP ingress; a broker DNS record does not create a TCP router.
- Network fragments are separately selected, role-bound access intent. Value references grant nothing.
- Root Zabbix is selected only when desired; omission does not enroll agents. `zabbix:` selects the unique configured server, or `{server: APP_ID}` disambiguates it.

## 6. Validate the whole site

With the tutorial environment:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py"   --stack "$STACK" --site "$STACK/examples/site.second.yaml" --check
```

Compilation checks the combined identities, budgets, listeners, storage and graph. It is stronger than validating each app separately, but still source-only. For an installed site, preserve current receipts/state/private material and use its own generated protected workflow. [Images and updates](images-and-updates.md) explains the update boundary.
