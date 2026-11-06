# Connect local filtering and recursive DNS

[Documentation index](../README.md) · [Examples](README.md) · [Connection guide](../guides/connect-apps.md)

This is a complete **source-only retained composition**: Pi-hole and Unbound share one guest, with an explicit loopback upstream/readiness connection and a DNS-only exposure. It demonstrates the typed source contract, not a fresh installation or adoption of an existing DNS server. Real deployment would require the genuine matching current guest/app owners and data directories.

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

Expect one guest and two resolved apps. The app phases are recursive_dns before filtering, after preparation. The selected upstream supplies `127.0.0.1:5335`; explicit readiness orders the producer. The DNS exposure selects one record for the filtering web endpoint and does not create an HTTP proxy route, ACME certificate or client firewall permission.

Both apps keep explicit retained project/service/network/data identities. The profiles remain independently selectable: use the standalone Unbound starter for a fresh no-storage example, or select a declared external upstream for Pi-hole instead. A blank directory is not a substitute for the retained configuration shown here.

## Useful changes and expected refusals

- Set `recursive_dns.properties.publish_port` to `5336`: its TCP/UDP loopback publications and the resolved connection target both change through the existing endpoint, without copying an address/port into the consumer.
- Change the connection target endpoint to missing: the existing reference validator refuses it.
- Use Pi-hole's physical service role as source_interface for the loopback target: the connection-scope validator refuses it; guest loopback must be explicit.
- Omit readiness: the endpoint value remains, but the explicit startup edge disappears. This is not a repair for an unwanted dependency or access-policy failure.

All addresses, trust/credential references and provider facts are synthetic. Do not run this as an admitted deployment. Compilation neither reads those credential contents nor changes a target.
