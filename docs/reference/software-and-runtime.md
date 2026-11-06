# Software, runtime and shared declarations

[Documentation index](../README.md) · [Reference index](README.md)

[stack.json](../../stack.json) is the single library index for named software, runtime, health, authentication, monitoring, assets and policy fragments. [images.json](../../images.json) is the image-version/policy catalogue. Profile pages link their selected names; a site is not another registry or version authority.

## Software selections

A software entry selects exact packages, public signed repository definitions and/or app-local image roles. Guest packages/repositories aggregate without changing order of first selection; conflicting versions refuse. Image roles remain app-scoped, so separate app instances do not overwrite each other's local role name.

| Selection | Packages | Image role → catalogue ID | Public repository |
| --- | --- | --- | --- |
| `docker` | `docker.io=26.1.5+dfsg1-9+deb13u1`<br>`docker-cli=26.1.5+dfsg1-9+deb13u1`<br>`docker-compose=2.26.1-4` | None | None |
| `curl` | `curl=8.14.1-2+deb13u7` | None | None |
| `network-tools` | `iproute2=6.15.0-1` | None | None |
| `yaml-parser` | `python3-yaml=6.0.2-1+b2` | None | None |
| `mariadb-client` | `mariadb-client-core=1:11.8.6-0+deb13u1` | None | None |
| `postgresql` | `postgresql-16=16.10-1.pgdg13+1`<br>`postgresql-client-16=16.10-1.pgdg13+1`<br>`libpq5=16.10-1.pgdg13+1` | None | `postgresql` |
| `mariadb` | `mariadb-server=1:12.3.3+maria~deb13`<br>`mariadb-client=1:12.3.3+maria~deb13` | None | `mariadb` |
| `influxdb` | `influxdb2=2.7.12-1`<br>`influxdb2-cli=2.7.5-1` | None | `influxdata` |
| `homeassistant-images` | None | `homeassistant` → `homeassistant` | None |
| `node_red-images` | None | `node_red` → `node_red` | None |
| `bitwarden-images` | None | `bitwarden` → `bitwarden` | None |
| `cloudbeaver-images` | None | `cloudbeaver` → `cloudbeaver`, `auth_gateway` → `auth_gateway` | None |
| `pihole-images` | None | `pihole` → `pihole` | None |
| `unbound-images` | None | `unbound` → `unbound` | None |
| `authentik-images` | None | `server` → `authentik`, `worker` → `authentik`, `redis` → `redis` | None |
| `traefik-images` | None | `traefik` → `traefik` | None |
| `zabbix-images` | None | `zabbix_server` → `zabbix_server`, `zabbix_web` → `zabbix_web` | None |
| `mqtt-images` | None | `mqtt` → `mqtt` | None |
| `mqtt_explorer-images` | None | `mqtt_explorer` → `mqtt_explorer`, `explorer_gateway` → `traefik` | None |
| `music_assistant-images` | None | `music_assistant` → `music_assistant` | None |
| `pegaprox-images` | None | `pegaprox` → `pegaprox` | None |
| `zigbee2mqtt-images` | None | `zigbee2mqtt` → `zigbee2mqtt` | None |
| `winet-images` | None | `winet` → `winet` | None |
| `homeassistant-public-images` | None | `homeassistant` → `homeassistant_public` | None |
| `node_red-public-images` | None | `node_red` → `node_red_public` | None |


Repository signing keys come from hash-bound public assets. The three vendor assets remain exact bytes. Native configuration/HBA is rendered by typed framework adapters; arbitrary raw templates are not a configuration escape.

## Image policies

- A registry digest renders the literal selected immutable reference with the common `missing` pull policy.
- The explicit Music Assistant `latest` selection keeps its floating policy and protected upgrade checks.
- HA/Node-RED custom archive IDs require concrete site local_id/archive/archive_sha256 bindings. The public zero-valued declarations are unresolved sentinels; no public-image fallback occurs.
- Public HA/Node-RED variants select separate official image catalogue IDs. They do not replace another instance's custom image or data.

See [Images and updates](../guides/images-and-updates.md). Do not copy checksum/version constants into another site policy or documentation authority; inspect the linked manifests for exact current bytes.

## Runtime selections

Each app selects named resource/process/security requirements. The following is the complete declared runtime catalogue; values are policy, not load-test results.

| Runtime | Owned workloads / settings | Guest requirements |
| --- | --- | --- |
| `container-host` | No workload limits | `nesting=True`, `keyctl=False` |
| `homeassistant` | `homeassistant`: `memory_mib=2048`, `pids_limit=512`, `cpu_limit=2` | None |
| `node_red` | `node_red`: `memory_mib=1024`, `pids_limit=256`, `cpu_limit=1`, `user=node-red` | None |
| `bitwarden` | `bitwarden`: `memory_mib=1536`, `pids_limit=256`, `cpu_limit=1` | None |
| `cloudbeaver` | `cloudbeaver`: `memory_mib=1536`, `pids_limit=512`, `cpu_limit=1`, `cap_drop=['ALL']`, `user=8978:8978`, `no_new_privileges=True`<br>`auth_gateway`: `memory_mib=128`, `pids_limit=128`, `cpu_limit=1`, `read_only=True`, `cap_drop=['ALL']`, `user=65532:65532`, `no_new_privileges=True` | None |
| `pihole` | `pihole`: `memory_mib=256`, `pids_limit=128`, `cpu_limit=1` | None |
| `unbound` | `unbound`: `memory_mib=256`, `pids_limit=128`, `cpu_limit=1` | None |
| `authentik` | `server`: `memory_mib=768`, `pids_limit=256`, `cpu_limit=1`, `user=1000`<br>`worker`: `memory_mib=768`, `pids_limit=256`, `cpu_limit=1`, `user=1000`<br>`redis`: `memory_mib=128`, `pids_limit=256`, `cpu_limit=1` | None |
| `traefik` | `traefik`: `memory_mib=512`, `pids_limit=256`, `cpu_limit=1` | None |
| `zabbix` | `zabbix_server`: `memory_mib=768`, `pids_limit=256`, `cpu_limit=1`<br>`zabbix_web`: `memory_mib=512`, `pids_limit=256`, `cpu_limit=1` | None |
| `mqtt` | `mqtt`: `memory_mib=256`, `pids_limit=128`, `cpu_limit=1` | None |
| `mqtt_explorer` | `mqtt_explorer`: `memory_mib=256`, `pids_limit=128`, `cpu_limit=1`, `read_only=True`, `cap_drop=['ALL']`, `user=1001:1001`, `no_new_privileges=True`<br>`explorer_gateway`: `memory_mib=128`, `pids_limit=128`, `cpu_limit=1`, `read_only=True`, `cap_drop=['ALL']`, `user=65532:65532`, `no_new_privileges=True` | None |
| `music_assistant` | `music_assistant`: `memory_mib=1536`, `pids_limit=512`, `cpu_limit=2` | None |
| `pegaprox` | `pegaprox`: `memory_mib=1536`, `pids_limit=256`, `cpu_limit=2`, `read_only=True`, `cap_drop=['ALL']`, `tmpfs=['/tmp:rw,nosuid,nodev,size=64m']`, `no_new_privileges=True` | `os_reserve_mib=512` |
| `zigbee2mqtt` | `zigbee2mqtt`: `memory_mib=512`, `pids_limit=128`, `cpu_limit=2` | None |
| `winet` | `winet`: `memory_mib=256`, `pids_limit=128`, `cpu_limit=1` | None |
| `homeassistant-mdns` | `homeassistant`: `cap_add=['NET_ADMIN']` | None |
| `native-postgresql` | Native `1792MiB` | None |
| `native-mariadb` | Native `768MiB` | None |
| `native-influxdb` | Native `1792MiB` | None |


A site may use the closed app.resources.containers resource allocation fields for owned services; this is not a user/capability/command override. The compiler sums container and native memory, applies effective OS reserve and rejects unsupported mixed native namespaces. It does not infer zero native cost or unlimited capacity.

## Health and monitoring

`adapter-ready` is the named `{type:adapter, check:readiness}` health profile. The framework expands each app's bounded checks; profiles do not supply arbitrary shell commands. Actual health/readiness is distinct from user login, SQL/MQTT data flow and service acceptance.

| Monitoring profile | Selected workload types |
| --- | --- |
| `linux-agent` | `linux` |
| `docker-agent` | `docker` |
| `postgresql-agent` | `postgresql` |
| `mariadb-agent` | `mysql` |
| `influxdb-agent` | `influxdb` |


Template linux and app-specific monitoring selections take effect only through the root selected Zabbix capability. Omission leaves it unselected; `zabbix:` selects the unique configured server, and `{server: ID}` chooses explicitly when needed. Existing monitoring ownership and generated credentials remain separate from arbitrary app password input.

## Authentication requirements

| Requirement | Type | Profile floor |
| --- | --- | --- |
| `cloudbeaver-oidc` | `cloudbeaver-oidc` | Required |
| `node-red-retained-oidc` | `node-red-retained-oidc` | Required |
| `zabbix-saml` | `zabbix-saml` | Optional |


These declare requirement types; concrete provider/client/secret metadata belongs to named site policies. A URL does not create a provider, grant authorization or imply a readiness wait.

## Optional network fragments

The library has no automatic access policy. A site explicitly selects each fragment and binds its typed roles. The two DNS fragments preserve distinct UDP-first/TCP-first order; names do not imply their rows are interchangeable.

| Fragment | Ordered rows | Roles to bind |
| --- | --- | --- |
| `mqtt_backend_ingress` | 1 | `interfaces:kernel`, `interface:destination`, `interface:source` |
| `http_backend_egress` | 1 | `interface:source`, `endpoint:destination` |
| `resolver_dns_udp_first` | 4 | `endpoint:fallback_dns`, `endpoint:primary_dns` |
| `source_bound_package_image_provider_web_egress` | 1 | `interfaces:kernel`, `interface:source` |
| `resolver_dns_tcp_first` | 4 | `endpoint:fallback_dns`, `endpoint:primary_dns` |
| `package_repository_web_egress` | 1 | None |
| `package_image_provider_web_egress` | 1 | None |


Across these seven fragments there are 13 ordered rows. Bindings do not union, deduplicate, sort or broaden them. Package download intent does not replace package-signature verification. Named address groups are ordered value reuse, not an inferred grant or dependency. See [Connect apps](../guides/connect-apps.md) and the framework policy reference for exact row syntax.
