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
      endpoint: dns_udp_endpoint
    source_interface: upstream_interface
    readiness: start
```

The target endpoint supplies 127.0.0.1:5335 from the selected Unbound instance. `source_interface` selects Pi-hole's already bound role. `readiness:start` explicitly orders the producer before the consumer. Omitting readiness removes that wait; it does not change the target value. An external upstream can be selected without Unbound; readiness requires a managed app target.

See the [source-only local DNS composition](../examples/local-dns.md) for the complete declarations and validation command. The framework reads complete connection and exposure files using its documented path rules. These files cannot be used as partial overlays.

## MQTT and a saved hostname

A broker endpoint such as `{app: broker, endpoint: backend_endpoint}` supplies the runtime target. A connection's hostname can select a named DNS exposure, or a supported named host alias, independently of that address. This preserves a saved hostname without forcing the GUI through a frontend route.

Explorer also requires a broker account or credential and an existing HTTP authentication outpost. Selecting a broker does not supply either prerequisite. Same-guest managed `mqtt-client` selects deliberately broad all-topic read/write access. An explicit existing credential uses its separate private source and does not create an account. See [Explorer](../reference/apps/mqtt_explorer.md) and [MQTT](../reference/apps/mqtt.md).

## Database connections

Home Assistant's recorder and metrics roles, and CloudBeaver's database roles, are optional until selected. The site binds each required source role to a physical guest interface, selects the named target endpoint, and chooses the supported readiness, account and transport options. CloudBeaver connections that supply only connection settings let users enter their own credentials. Managed administration selects a separate explicit account and capability.

CloudBeaver PostgreSQL administration requires TLS, SCRAM authentication and channel binding; its MariaDB-admin variant requires the library-owned Connector/J capability and PARSEC verify-full transport. PostgreSQL SUPERUSER and MariaDB global ALL with GRANT are powerful intentional privileges, not consequences of a URL. Read the two [Cloud profile pages](../reference/apps/cloudbeaver.md).

## Readiness and traffic are different

| Declaration | Meaning |
| --- | --- |
| Context DNS endpoint | Supplies the DNS value for OS configuration; it does not make deployment wait. |
| Guest readiness stage:preparation | Checks an explicitly selected prerequisite through the guest’s control interface. |
| Connection readiness:start/configure | Explicitly makes the consumer wait for a stage supported by the profile’s connection role. |
| Network policy binding | Declares the intended traffic; selected connections between guests must pass the checks for access at both their source and target. |
| Authentication URL | Supplies login metadata; it does not make deployment wait for the identity provider to start. |

When dependent apps run on different guests, the generated guest jobs wait for each other as required. Apps on the same guest run in the required step order. The compiler rejects dependency cycles. Disabling a required producer does not repair a dependency. Policy rows preserve order and comments; address groups preserve their exact ordered members, without union or deduplication.

## Expose a service separately

A DNS exposure selects endpoint, domain and resolver. It does not create an HTTP/TCP proxy route. An HTTP exposure additionally names ingress, TLS, and the selected middleware and backend transport. An app origin and a saved broker hostname can refer to that exposure without copying its domain.

Do not publish a private helper listener directly to avoid a required gateway. Choose the app's advertised supported endpoint and preserve its authentication boundary. Actual DNS, TLS and sign-in verification follow separately authorized deployment.
