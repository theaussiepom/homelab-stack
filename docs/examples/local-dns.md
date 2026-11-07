# Connect local filtering and recursive DNS

[Documentation index](../README.md) · [Examples](README.md) · [Connection guide](../guides/connect-apps.md)

You can compile this complete example offline to see how Pi-hole and Unbound share one guest. Their connection uses guest loopback and explicitly makes Pi-hole wait for Unbound; the exposure publishes DNS only. Deployment requires an existing HomeLab-managed guest and apps with matching ownership records and data directories. This example cannot install a new DNS server or adopt one that HomeLab does not manage.

## Prepare the files

Use the isolated environment from [First configuration](../guides/first-configuration.md); STACK, FRAMEWORK and PYTHON are defined there. Create a new local source directory:

```sh
SOURCE_WORK="$(mktemp -d)"
SOURCE_WORK="$(cd "$SOURCE_WORK" && pwd -P)"
cp -R "$STACK/examples/catalogue/local-dns/." "$SOURCE_WORK/"
printf '%s\n' "$SOURCE_WORK"
```

The copy contains the three complete files linked below. Those YAML files are the single maintained source authority and are compiled by the documentation tests; this guide does not keep a second copy. Source references are relative to the site root. There are no partial overlays or recursive includes.

## site.yaml

Complete maintained source: [site.yaml](../../examples/catalogue/local-dns/site.yaml).

## connections/filtering-upstream.yaml

Complete maintained source: [connections/filtering-upstream.yaml](../../examples/catalogue/local-dns/connections/filtering-upstream.yaml).

## exposures/filtering-dns.yaml

Complete maintained source: [exposures/filtering-dns.yaml](../../examples/catalogue/local-dns/exposures/filtering-dns.yaml).

## Validate and understand the result

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py"   --stack "$STACK" --site "$SOURCE_WORK/site.yaml" --check
```

Expect one guest and two resolved apps. After preparation, `recursive_dns` runs before `filtering`. The selected upstream gives Pi-hole the address `127.0.0.1:5335`; the explicit readiness setting makes Pi-hole wait for Unbound. The DNS exposure selects one record for the filtering web endpoint and does not create an HTTP proxy route, ACME certificate or client firewall permission.

Both apps preserve their existing Compose project, service and network identities, along with the data owned by each app. The profiles remain independently selectable: use the standalone Unbound starter for an example that can create Unbound without a storage mount, or select a declared external upstream for Pi-hole instead. A blank directory is not a substitute for the retained configuration shown here.

## Useful changes and expected refusals

- Set `recursive_dns.properties.publish_port` to `5336`: its TCP/UDP loopback publications and the resolved connection target both change through the existing endpoint, without copying the address and port into the consumer.
- Change the connection target endpoint to missing: the existing reference validator refuses it.
- Use Pi-hole's physical service role as source_interface for the loopback target: the connection-scope validator refuses it; guest loopback must be explicit.
- Omit readiness: the endpoint value remains, but the requirement to wait for startup is removed. This is not a repair for an unwanted dependency or access-policy failure.

All addresses, references to trust files and credentials, and provider facts are synthetic. Do not run this as an admitted deployment. Compilation neither reads those credential contents nor changes a target.
