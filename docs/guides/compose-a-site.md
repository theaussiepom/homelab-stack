# Compose a site

[Documentation index](../README.md) · [Catalogue](../reference/README.md)

Use this checklist when extending a configuration you already understand. For your first one, follow [Design your homelab](design-your-homelab.md), which supplies the service choices, facts worksheet, complete copy and tested layout variations. Its `STACK`, `FRAMEWORK`, `PYTHON` and `SITE_ROOT` variables select your source environment and editable site. A site supplies allocations; this library supplies application requirements. Keep real VMIDs, addresses and credential references in your private site.

## 1. Choose independent apps

Select [profiles](../reference/README.md) by lifecycle and integrations. For example, the maintained [alternate site](../../examples/site.second.yaml) selects three `unbound` instances and one `homeassistant` instance. It does not select Node-RED, a database, MQTT, identity or ingress.

Before adding a profile, record its required roles, data/credential prerequisites, fixed listening addresses and ports and resource reservations from its reference page. Then choose a guest that can meet them. A profile being in the catalogue does not mean it can create an empty installation; the [newcomer choices](design-your-homelab.md#1-start-with-the-services-you-want) distinguish fresh Unbound/HA from prepared Pi-hole.

A profile is a reusable declaration in this library's `apps/`. A site's `apps` entry is a named instance of that profile. These are different document kinds.

## 2. Give each guest its facts

A complete guest chooses context, template, lifecycle, persistent VMID/hostname, template file, root storage, named NICs and control interface. `fresh` permits supported creation if absent and remains valid for later updates to the same HomeLab-managed instance; `retained` requires an already managed guest and refuses creation. App lifecycle is selected independently, so a supported fresh app may be added to an owned guest with unused identities, enough resources and supported storage. Neither policy imports foreign data. Optional resource/startup/security fields inherit from the [template](../reference/templates.md). Declare extra volumes or supported root-filesystem data paths explicitly.

The [alternate HA guest](../../examples/second/guests/home-app.yaml) is a complete example. It needs more memory than the base default because the HA reservation and OS reserve must fit. Its named `apps` volume is not an app profile or a command to import existing data.

Use the [fact-to-field worksheet](design-your-homelab.md#3-collect-your-proxmox-facts) to obtain the actual node, bridge, VLAN, subnet, template ID and pool, then reserve the guest's own VMID, MAC and address. The [shared-guest variation](design-your-homelab.md#8-try-a-different-supported-layout) shows how to combine compatible apps before installation.

Physical NIC slots and MACs are persistent provider identity. One effective default route is required; a selected DHCP interface already contributes that route. Keep static secondary NICs explicit and do not infer a route from an app's web role.

## 3. Bind each app

The complete [HA instance](../../examples/second/apps/home.yaml) is:

```yaml
schema: homelab-components-v1
kind: app
profile: homeassistant
guest: home-app
lifecycle: fresh
interfaces:
  web_interface:
    interface: primary
storage:
  config:
    volume: apps
    subpath: homeassistant
```

`home-app`, `primary` and `apps` refer to the complete guest above. The public profile can create the app’s configuration subdirectory after verifying that HomeLab owns the volume. The subdirectory must not already exist. This step does not change the file owner of an existing directory tree.

Roles omitted here are optional and unselected. Adding a recorder or broker connection requires its corresponding source role bound to a physical guest interface, selected endpoint and explicit network policy. It does not appear automatically because another app exists.

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

This is the exact shape used by the alternate site. The path is relative to that site's file directory, not the referenced file's directory. Each referenced file has its own schema/kind and complete body. It is not a partial overlay, template or recursive include.

The [complete copy step](design-your-homelab.md#4-make-a-complete-configuration-of-your-own) puts every baseline and optional source in your own directory. For another catalogue composition, copy its complete referenced directory tree before editing. Renaming a map key requires updating its consumers; use the [rename checklist](design-your-homelab.md#if-you-want-your-own-names).

## 5. Select relationships deliberately

- [Interface roles](multiple-interfaces.md) identify the source/destination socket context.
- [Connections](connect-apps.md) select existing endpoints and optional explicit readiness/account/transport choices.
- Exposures select managed DNS or HTTP ingress; a broker DNS record does not create a TCP router.
- Select network-policy fragments separately and bind their roles to site resources. Referencing an endpoint value does not permit traffic.
- Root Zabbix is selected only when desired; omission does not enroll agents. `zabbix:` selects the unique configured server, or `{server: APP_ID}` disambiguates it.

## 6. Validate the whole site

With the design tutorial's environment and your complete source copy:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK" --site "$SITE_ROOT/site.yaml" --check
```

Compilation checks the combined identities, budgets, listeners, storage and graph. It is stronger than validating each app separately, but still source-only. For an installed site, preserve current receipts/state/private material and use its own generated protected workflow. [Images and updates](images-and-updates.md) explains the update boundary.

Inspect the actual packet using [the result checkpoint](design-your-homelab.md#6-check-the-configuration-and-inspect-its-result): compare allocations, sockets, data paths and selected apps against your intended outcome. Then complete the [remaining deployment inputs](design-your-homelab.md#9-finish-with-a-deployment-preparation-list).

For a missing reusable profile, follow [Contributing](../contributing.md) and its [profile documentation template](../templates/application-profile.md). Do not invent private configuration engines or publish untested fragments as complete sites.

## Follow a web connection through the configuration

The complete [Home Assistant HTTPS example](../../examples/catalogue/home-web.yaml) selects app instance `home`, profile `homeassistant`, guest `automation`, and `lifecycle: fresh`. It binds `interfaces.web_interface` to that guest's `primary` NIC and `storage.config` to volume `apps`, subpath `homeassistant`.

The profile declares `web_interface`, TCP/8123 listener `web_listener`, and exported connection `web_endpoint` with `protocol: http`, `listener: web_listener` and `via: web_interface`. The guest supplies the address. `exposures.home_web.target: {app: home, endpoint: web_endpoint}` selects that resulting HTTP connection. `ingress: {app: edge, endpoint: https_endpoint}` and `tls: site_certificate` select the frontend and named certificate policy. The example declares the required network rules separately.

`home` is your instance name; `homeassistant` chooses the installation recipe. The app role `web_interface`, guest NIC `primary`, listener `web_listener` and exported connection `web_endpoint` have distinct names and jobs. Changing the guest address updates the resolved backend through the reference. Selecting an endpoint does not change the profile's wildcard listener, grant general access or establish service readiness. See the framework's [instance contract](https://github.com/theaussiepom/homelab/blob/ca61bfa96b848dd881239dcafdfa38985b5a70b9/docs/reference/apps.md#instance-interface-role-and-exported-endpoint) and [exposure contract](https://github.com/theaussiepom/homelab/blob/ca61bfa96b848dd881239dcafdfa38985b5a70b9/docs/reference/exposures.md).

Compile this complete example using the same selected framework as the other examples. It uses synthetic values, reads no credentials and contacts no targets. Compilation does not verify DNS, certificates, Home Assistant onboarding or service availability.
