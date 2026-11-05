# Connect apps and select readiness

[Documentation index](../README.md) · [Interfaces](multiple-interfaces.md)

A connection selects a named consumer role and a named app endpoint or declared external target. It supplies resolved values. Readiness, access policy, transport trust and account privileges are separate explicit choices.

## Local DNS: a complete connection fragment

The following is a **connection fragment**, not a complete site. It assumes app `filtering` selects Pi-hole, app `recursive_dns` selects Unbound on the same guest, and Pi-hole's `upstream` interface role uses guest-loopback:

```yaml
connections:
  filtering_upstream:
    consumer:
      app: filtering
      connection: upstream
    target:
      app: recursive_dns
      endpoint: dns_udp
    source_interface: upstream
    readiness: start
```

The target endpoint supplies127.0.0.1:5335 from the Unbound profile/instance. `source_interface` selects Pi-hole's already bound role. `readiness:start` explicitly orders the producer before the consumer. Omitting readiness removes that wait; it does not change the target value. An external upstream can be selected without Unbound; readiness requires a managed app target.

See the [source-only local DNS composition](../examples/local-dns.md) for complete declared objects and validation. The framework owns its whole-source connection/exposure reader and path rules; this guide does not introduce a merge language.

## MQTT and a saved hostname

A broker endpoint such as `{app: broker, endpoint: backend}` supplies the runtime target. A connection's hostname can select a named DNS exposure, or a supported named host alias, independently of that address. This preserves a saved hostname without forcing the GUI through a frontend route.

Explorer additionally needs a required broker account/credential and a required existing HTTP outpost; it cannot derive either from the broker's presence. Same-guest managed `mqtt-client` selects deliberately broad all-topic read/write access. An explicit existing credential uses its separate private source and does not create an account. See [Explorer](../reference/apps/mqtt_explorer.md) and [MQTT](../reference/apps/mqtt.md).

## Database connections

HA's recorder/metrics and CloudBeaver's database roles are optional until selected. The site binds physical source roles and named endpoints, then chooses allowed readiness/account/transport fields. Metadata-only Cloud connections let users supply credentials. Managed administration selects a separate explicit account and capability.

CloudBeaver PostgreSQL administration requires TLS/SCRAM/channel binding; its MariaDB-admin variant requires the library-owned Connector/J capability and PARSEC verify-full transport. PostgreSQL SUPERUSER and MariaDB global ALL with GRANT are powerful intentional privileges, not consequences of a URL. Read the two [Cloud profile pages](../reference/apps/cloudbeaver.md).

## Readiness and traffic are different

| Declaration | Meaning |
| --- | --- |
| Context DNS endpoint | Value for OS configuration; no inferred wait |
| Guest readiness stage:preparation | Explicit prerequisite sourced from the guest control interface |
| Connection readiness:start/configure | One of the profile role's allowed explicit ordering choices |
| Network policy binding | Explicit traffic intent; selected cross-guest traffic must satisfy source/target admission |
| Authentication URL | Login metadata; no inferred identity-provider startup wait |

Cross-guest dependencies produce guest-job needs; same-guest dependencies order app steps. Cycles refuse. Disabling a required producer does not repair a dependency. Policy rows preserve order and comments; address groups preserve their exact ordered members, without union or deduplication.

## Expose a service separately

A DNS exposure selects endpoint, domain and resolver. It does not create an HTTP/TCP proxy route. An HTTP exposure additionally names ingress, TLS and selected middleware/backend transport. An app origin and a saved broker hostname can refer to that exposure without copying its domain.

Do not publish a private helper listener directly to avoid a required gateway. Choose the app's advertised supported endpoint and preserve its authentication boundary. Actual DNS, TLS and sign-in verification follow separately authorized deployment.
