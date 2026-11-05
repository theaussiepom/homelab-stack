# Connect local filtering and recursive DNS

[Documentation index](../README.md) · [Examples](README.md) · [Connection guide](../guides/connect-apps.md)

This is a complete **source-only retained composition**: Pi-hole and Unbound share one guest, with an explicit loopback upstream/readiness connection and a DNS-only exposure. It demonstrates the typed source contract, not a fresh installation or adoption of an existing DNS server. Real deployment would require the genuine matching current guest/app owners and data directories.

## Prepare the files

Use the isolated environment from [First configuration](../guides/first-configuration.md); STACK, FRAMEWORK and PYTHON are defined there. Create a new local source directory:

```sh
SOURCE_WORK="$(mktemp -d)"
SOURCE_WORK="$(cd "$SOURCE_WORK" && pwd -P)"
mkdir "$SOURCE_WORK/connections" "$SOURCE_WORK/exposures"
printf '%s\n' "$SOURCE_WORK"
```

Save the following three complete files beneath that directory. Paths in source references are relative to the site root. There are no partial overlays or recursive includes. Guest/app bodies are inline here so the full required composition is visible.

## site.yaml

```yaml
schema: homelab-components-v1
kind: site
contexts:
  lab:
    backend: proxmox-lxc
    node: example-node
    api_endpoint:
      external: proxmox
    trust:
      ca_file: /etc/example/ca.pem
      known_hosts: /etc/example/known_hosts
    credentials:
      api_token: api
      ssh_private_key: ssh
    paths:
      state_root: /var/lib/example/state
      backup_directory: /mnt/example/backups
      backup_mount: /mnt/example
      backup_source: nas.example.invalid:/backups
    protected_guests: []
    ssh_public_keys: []
    dns_servers:
    - external: resolver
networks:
  services:
    context: lab
    cidr: 198.18.20.0/24
    bridge: vmbr-example
    vlan: 220
    gateway: 198.18.20.1
storage:
  local:
    context: lab
    pool: example-local
guests:
  resolver:
    context: lab
    template: base
    lifecycle: retained
    identity:
      vmid: 610
      hostname: example-resolver
    template_file_id: example:vztmpl/debian.tar.zst
    root_storage: local
    interfaces:
      primary:
        network: services
        slot: 0
        mac: 02:00:00:20:00:10
        address:
          mode: static
          value: 198.18.20.10
        default_route: true
        ipv6: manual
    network_policy:
    - policy: deployment
      endpoints:
        runner:
          external: runner
    - policy: downloads
      address_groups:
        internet: internet
    - policy: recursive_dns
      address_groups:
        internet: internet
    control_interface: primary
    root_paths:
      pihole_config:
        path: /srv/example/pihole
      unbound_config:
        path: /srv/example/unbound
    compose_projects:
      dns:
        name: example-dns
        file: compose-dns.yml
apps:
  recursive_dns:
    profile: unbound
    guest: resolver
    lifecycle: retained
    interfaces:
      service:
        scope: guest-loopback
      private:
        scope: app-network
        network: default
    identity:
      phase: recursive_dns
      runtime_id: recursive_dns
      project: dns
      services:
        unbound: recursive_dns
      networks:
        default: recursive_private
    storage:
      config:
        root_path: unbound_config
        subpath: ''
  filtering:
    profile: pihole
    guest: resolver
    lifecycle: retained
    identity:
      phase: filtering
      runtime_id: filtering
      project: dns
      services:
        pihole: filtering
      networks: {}
    interfaces:
      service:
        interface: primary
      upstream:
        scope: guest-loopback
    storage:
      config:
        root_path: pihole_config
        subpath: ''
domains:
  filtering: dns.example.invalid
external_endpoints:
  proxmox:
    protocol: https
    address: 192.0.2.10
    port: 8006
  resolver:
    protocol: udp
    address: 192.0.2.53
    port: 53
  runner:
    protocol: tcp
    address: 198.18.20.2
    port: 22
secret_sources:
  api:
    type: file
    path: /run/example/api-token
  ssh:
    type: file
    path: /run/example/ssh-key
connections:
  filtering_upstream:
    source: connections/filtering-upstream.yaml
exposures:
  filtering_dns:
    source: exposures/filtering-dns.yaml
address_groups:
  internet:
    members:
    - 0.0.0.0/0
policies:
  network:
    deployment:
      rules:
      - direction: in
        proto: tcp
        source:
          endpoint: runner
        port:
          endpoint: runner
        comment: Deployment SSH
    downloads:
      rules:
      - direction: out
        proto: tcp
        port: 80,443
        destination:
          address_group: internet
        comment: Package and image downloads
    recursive_dns:
      rules:
      - direction: out
        proto: udp
        port: '53'
        destination:
          address_group: internet
        comment: Recursive DNS
      - direction: out
        proto: tcp
        port: '53'
        destination:
          address_group: internet
        comment: Recursive DNS
  transport: {}
  tls: {}
  middlewares: {}
  authentication: {}
```

## connections/filtering-upstream.yaml

```yaml
schema: homelab-components-v1
kind: connection
consumer:
  app: filtering
  connection: upstream
target:
  app: recursive_dns
  endpoint: dns_udp
source_interface: upstream
readiness: start
```

## exposures/filtering-dns.yaml

```yaml
schema: homelab-components-v1
kind: exposure
type: dns
endpoint:
  app: filtering
  endpoint: web
domain: filtering
resolver: filtering
```

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
