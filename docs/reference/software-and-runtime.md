# Software, runtime and shared declarations

[Documentation index](../README.md) · [Reference index](README.md)

[stack.json](../../stack.json) is the single library index for named software, runtime, health, authentication, monitoring, assets and policy fragments. [images.json](../../images.json) is the image-version/policy catalogue. Profile pages link their selected names; a site does not define another registry or version policy.

## Software selections

A software entry selects exact packages, public signed repository definitions, app-local image roles, or a combination of these. The resolver combines guest package and repository selections in the order first selected. It rejects conflicting versions. Image roles belong to their app instance, so separate instances can use the same local role name without overwriting each other.

| Selection | Packages | Image role → catalogue ID | Public repository |
| --- | --- | --- | --- |
| <a id="registration-software-docker"></a>`software.docker` | `docker.io=26.1.5+dfsg1-9+deb13u1`<br>`docker-cli=26.1.5+dfsg1-9+deb13u1`<br>`docker-compose=2.26.1-4` | None | None |
| <a id="registration-software-curl"></a>`software.curl` | `curl=8.14.1-2+deb13u7` | None | None |
| <a id="registration-software-network-tools"></a>`software.network-tools` | `iproute2=6.15.0-1` | None | None |
| <a id="registration-software-yaml-parser"></a>`software.yaml-parser` | `python3-yaml=6.0.2-1+b2` | None | None |
| <a id="registration-software-mariadb-client"></a>`software.mariadb-client` | `mariadb-client-core=1:11.8.6-0+deb13u1` | None | None |
| <a id="registration-software-postgresql"></a>`software.postgresql` | `postgresql-16=16.10-1.pgdg13+1`<br>`postgresql-client-16=16.10-1.pgdg13+1`<br>`libpq5=16.10-1.pgdg13+1` | None | `postgresql` |
| <a id="registration-software-mariadb"></a>`software.mariadb` | `mariadb-server=1:12.3.3+maria~deb13`<br>`mariadb-client=1:12.3.3+maria~deb13` | None | `mariadb` |
| <a id="registration-software-influxdb"></a>`software.influxdb` | `influxdb2=2.7.12-1`<br>`influxdb2-cli=2.7.5-1` | None | `influxdata` |
| <a id="registration-software-homeassistant-images"></a>`software.homeassistant-images` | None | `homeassistant` → `homeassistant` | None |
| <a id="registration-software-node-red-images"></a>`software.node_red-images` | None | `node_red` → `node_red` | None |
| <a id="registration-software-bitwarden-images"></a>`software.bitwarden-images` | None | `bitwarden` → `bitwarden` | None |
| <a id="registration-software-cloudbeaver-images"></a>`software.cloudbeaver-images` | None | `cloudbeaver` → `cloudbeaver`, `auth_gateway` → `auth_gateway` | None |
| <a id="registration-software-pihole-images"></a>`software.pihole-images` | None | `pihole` → `pihole` | None |
| <a id="registration-software-unbound-images"></a>`software.unbound-images` | None | `unbound` → `unbound` | None |
| <a id="registration-software-authentik-images"></a>`software.authentik-images` | None | `server` → `authentik`, `worker` → `authentik`, `redis` → `redis` | None |
| <a id="registration-software-traefik-images"></a>`software.traefik-images` | None | `traefik` → `traefik` | None |
| <a id="registration-software-zabbix-images"></a>`software.zabbix-images` | None | `zabbix_server` → `zabbix_server`, `zabbix_web` → `zabbix_web` | None |
| <a id="registration-software-mqtt-images"></a>`software.mqtt-images` | None | `mqtt` → `mqtt` | None |
| <a id="registration-software-mqtt-explorer-images"></a>`software.mqtt_explorer-images` | None | `mqtt_explorer` → `mqtt_explorer`, `explorer_gateway` → `traefik` | None |
| <a id="registration-software-music-assistant-images"></a>`software.music_assistant-images` | None | `music_assistant` → `music_assistant` | None |
| <a id="registration-software-pegaprox-images"></a>`software.pegaprox-images` | None | `pegaprox` → `pegaprox` | None |
| <a id="registration-software-zigbee2mqtt-images"></a>`software.zigbee2mqtt-images` | None | `zigbee2mqtt` → `zigbee2mqtt` | None |
| <a id="registration-software-winet-images"></a>`software.winet-images` | None | `winet` → `winet` | None |
| <a id="registration-software-homeassistant-public-images"></a>`software.homeassistant-public-images` | None | `homeassistant` → `homeassistant_public` | None |
| <a id="registration-software-node-red-public-images"></a>`software.node_red-public-images` | None | `node_red` → `node_red_public` | None |


Repository signing keys come from hash-bound public assets. The three vendor assets remain exact bytes. Framework adapters generate native service configuration and PostgreSQL host-based authentication (HBA) rules from typed inputs. They do not accept arbitrary templates as a way around those inputs.

## Image policies

- A registry digest produces the exact selected immutable image reference. Its `missing` pull policy downloads the image only when it is absent locally.
- The explicit Music Assistant `latest` selection keeps its floating policy and protected upgrade checks.
- Home Assistant and Node-RED custom archive selections require the site to supply local_id, archive and archive_sha256. The public zero values are placeholders, and HomeLab does not substitute a public image for them.
- Public HA/Node-RED variants select separate official image catalogue IDs. They do not replace another instance's custom image or data.

See [Images and updates](../guides/images-and-updates.md). Do not copy checksum/version constants into another site policy or documentation authority; inspect the linked manifests for exact current bytes.

## Runtime selections

Each app selects named resource limits, process settings and security requirements. The following is the complete declared runtime catalogue; the values define resource and security requirements, not measured performance.

| Runtime | Owned workloads / settings | Guest requirements |
| --- | --- | --- |
| <a id="registration-runtime-profiles-container-host"></a>`runtime_profiles.container-host` | No workload limits | `nesting=True`, `keyctl=False` |
| <a id="registration-runtime-profiles-homeassistant"></a>`runtime_profiles.homeassistant` | `homeassistant`: `memory_mib=2048`, `pids_limit=512`, `cpu_limit=2` | None |
| <a id="registration-runtime-profiles-node-red"></a>`runtime_profiles.node_red` | `node_red`: `memory_mib=1024`, `pids_limit=256`, `cpu_limit=1`, `user=node-red` | None |
| <a id="registration-runtime-profiles-bitwarden"></a>`runtime_profiles.bitwarden` | `bitwarden`: `memory_mib=1536`, `pids_limit=256`, `cpu_limit=1` | None |
| <a id="registration-runtime-profiles-cloudbeaver"></a>`runtime_profiles.cloudbeaver` | `cloudbeaver`: `memory_mib=1536`, `pids_limit=512`, `cpu_limit=1`, `cap_drop=['ALL']`, `user=8978:8978`, `no_new_privileges=True`<br>`auth_gateway`: `memory_mib=128`, `pids_limit=128`, `cpu_limit=1`, `read_only=True`, `cap_drop=['ALL']`, `user=65532:65532`, `no_new_privileges=True` | None |
| <a id="registration-runtime-profiles-pihole"></a>`runtime_profiles.pihole` | `pihole`: `memory_mib=256`, `pids_limit=128`, `cpu_limit=1` | None |
| <a id="registration-runtime-profiles-unbound"></a>`runtime_profiles.unbound` | `unbound`: `memory_mib=256`, `pids_limit=128`, `cpu_limit=1` | None |
| <a id="registration-runtime-profiles-authentik"></a>`runtime_profiles.authentik` | `server`: `memory_mib=768`, `pids_limit=256`, `cpu_limit=1`, `user=1000`<br>`worker`: `memory_mib=768`, `pids_limit=256`, `cpu_limit=1`, `user=1000`<br>`redis`: `memory_mib=128`, `pids_limit=256`, `cpu_limit=1` | None |
| <a id="registration-runtime-profiles-traefik"></a>`runtime_profiles.traefik` | `traefik`: `memory_mib=512`, `pids_limit=256`, `cpu_limit=1` | None |
| <a id="registration-runtime-profiles-zabbix"></a>`runtime_profiles.zabbix` | `zabbix_server`: `memory_mib=768`, `pids_limit=256`, `cpu_limit=1`<br>`zabbix_web`: `memory_mib=512`, `pids_limit=256`, `cpu_limit=1` | None |
| <a id="registration-runtime-profiles-mqtt"></a>`runtime_profiles.mqtt` | `mqtt`: `memory_mib=256`, `pids_limit=128`, `cpu_limit=1` | None |
| <a id="registration-runtime-profiles-mqtt-explorer"></a>`runtime_profiles.mqtt_explorer` | `mqtt_explorer`: `memory_mib=256`, `pids_limit=128`, `cpu_limit=1`, `read_only=True`, `cap_drop=['ALL']`, `user=1001:1001`, `no_new_privileges=True`<br>`explorer_gateway`: `memory_mib=128`, `pids_limit=128`, `cpu_limit=1`, `read_only=True`, `cap_drop=['ALL']`, `user=65532:65532`, `no_new_privileges=True` | None |
| <a id="registration-runtime-profiles-music-assistant"></a>`runtime_profiles.music_assistant` | `music_assistant`: `memory_mib=1536`, `pids_limit=512`, `cpu_limit=2` | None |
| <a id="registration-runtime-profiles-pegaprox"></a>`runtime_profiles.pegaprox` | `pegaprox`: `memory_mib=1536`, `pids_limit=256`, `cpu_limit=2`, `read_only=True`, `cap_drop=['ALL']`, `tmpfs=['/tmp:rw,nosuid,nodev,size=64m']`, `no_new_privileges=True` | `os_reserve_mib=512` |
| <a id="registration-runtime-profiles-zigbee2mqtt"></a>`runtime_profiles.zigbee2mqtt` | `zigbee2mqtt`: `memory_mib=512`, `pids_limit=128`, `cpu_limit=2` | None |
| <a id="registration-runtime-profiles-winet"></a>`runtime_profiles.winet` | `winet`: `memory_mib=256`, `pids_limit=128`, `cpu_limit=1` | None |
| <a id="registration-runtime-profiles-homeassistant-mdns"></a>`runtime_profiles.homeassistant-mdns` | `homeassistant`: `cap_add=['NET_ADMIN']` | None |
| <a id="registration-runtime-profiles-native-postgresql"></a>`runtime_profiles.native-postgresql` | Native `1792MiB` | None |
| <a id="registration-runtime-profiles-native-mariadb"></a>`runtime_profiles.native-mariadb` | Native `768MiB` | None |
| <a id="registration-runtime-profiles-native-influxdb"></a>`runtime_profiles.native-influxdb` | Native `1792MiB` | None |


A site may allocate resources to the app’s services through the accepted `app.resources.containers` fields. These fields do not allow changes to the process user, capabilities or commands. The compiler adds the memory required by containers and native services, reserves memory for the operating system, and rejects native services whose fixed names conflict. Native services count toward the budget, and guest capacity is finite.

## Health and monitoring

`adapter-ready` is the named `{type:adapter, check:readiness}` health profile. The framework expands each app's bounded checks; profiles do not supply arbitrary shell commands. A passing health check does not prove that user login, SQL or MQTT data exchange, or other intended service behavior works.

| Monitoring profile | Selected workload types |
| --- | --- |
| <a id="registration-monitoring-profiles-linux-agent"></a>`monitoring_profiles.linux-agent` | `linux` |
| <a id="registration-monitoring-profiles-docker-agent"></a>`monitoring_profiles.docker-agent` | `docker` |
| <a id="registration-monitoring-profiles-postgresql-agent"></a>`monitoring_profiles.postgresql-agent` | `postgresql` |
| <a id="registration-monitoring-profiles-mariadb-agent"></a>`monitoring_profiles.mariadb-agent` | `mysql` |
| <a id="registration-monitoring-profiles-influxdb-agent"></a>`monitoring_profiles.influxdb-agent` | `influxdb` |


The template’s Linux monitoring and each app’s monitoring settings take effect only when the site selects Zabbix at its root. Omission leaves it unselected; `zabbix:` selects the unique configured server, and `{server: ID}` chooses explicitly when needed. Monitoring keeps its existing ownership records and generated credentials; an arbitrary app password cannot replace them.

## Authentication requirements

| Requirement | Type | Profile floor |
| --- | --- | --- |
| <a id="registration-authentication-profiles-cloudbeaver-oidc"></a>`authentication_profiles.cloudbeaver-oidc` | `cloudbeaver-oidc` | Required |
| <a id="registration-authentication-profiles-node-red-retained-oidc"></a>`authentication_profiles.node-red-retained-oidc` | `node-red-retained-oidc` | Required |
| <a id="registration-authentication-profiles-zabbix-saml"></a>`authentication_profiles.zabbix-saml` | `zabbix-saml` | Optional |


These entries declare authentication requirements. Named site policies supply the provider, client and secret references. A URL does not create a provider, grant authorization or imply a readiness wait.

## Optional network fragments

The library has no automatic access policy. A site explicitly selects each fragment and binds its typed roles. The two DNS fragments preserve distinct UDP-first/TCP-first order; names do not imply their rows are interchangeable.

| Fragment | Ordered rows | Roles to bind |
| --- | --- | --- |
| <a id="registration-policies-network-mqtt-backend-ingress"></a>`policies.network.mqtt_backend_ingress` | 1 | `interfaces:kernel`, `interface:destination`, `interface:source` |
| <a id="registration-policies-network-http-backend-egress"></a>`policies.network.http_backend_egress` | 1 | `interface:source`, `endpoint:destination` |
| <a id="registration-policies-network-resolver-dns-udp-first"></a>`policies.network.resolver_dns_udp_first` | 4 | `endpoint:fallback_dns`, `endpoint:primary_dns` |
| <a id="registration-policies-network-source-bound-package-image-provider-web-egress"></a>`policies.network.source_bound_package_image_provider_web_egress` | 1 | `interfaces:kernel`, `interface:source` |
| <a id="registration-policies-network-resolver-dns-tcp-first"></a>`policies.network.resolver_dns_tcp_first` | 4 | `endpoint:fallback_dns`, `endpoint:primary_dns` |
| <a id="registration-policies-network-package-repository-web-egress"></a>`policies.network.package_repository_web_egress` | 1 | None |
| <a id="registration-policies-network-package-image-provider-web-egress"></a>`policies.network.package_image_provider_web_egress` | 1 | None |


These seven fragments contain 13 rules in a defined order. Binding their roles does not combine, deduplicate, sort or broaden the rules. Package download intent does not replace package-signature verification. Named address groups let rules reuse an ordered list of addresses. Selecting a group does not grant access or create a dependency. See [Connect apps](../guides/connect-apps.md) and the framework policy reference for exact row syntax.

## Health registration and public assets

The loader checks hash-bound assets as public source bytes; they are vendor repository keys, never private credentials. The normal library index remains the authority for asset path and digest.

| Registered declaration | Effect / source |
| --- | --- |
| <a id="registration-health-profiles-adapter-ready"></a>`health_profiles.adapter-ready` | [Adapter readiness selection](../../stack.json) |
| <a id="registration-assets-postgresql-repository-key"></a>`assets.postgresql-repository-key` | [Public asset](../../assets/postgresql/vendor.asc) |
| <a id="registration-assets-mariadb-repository-key"></a>`assets.mariadb-repository-key` | [Public asset](../../assets/mariadb/vendor.asc) |
| <a id="registration-assets-influxdb-repository-key"></a>`assets.influxdb-repository-key` | [Public asset](../../assets/influxdb/vendor.asc) |

The tests check for both missing and extra registered names through [documentation conformance](../testing.md#documentation-conformance). Tests compare exact profile and template field values with their typed records. The shared catalogue check covers registered names; a reviewer must still compare its nested values and procedural explanations with the source.

The compatible loader also accepts a bundle registry, but this library registers no bundles; no fixed guest/application bundle is implied. New registrations must acquire explicit catalogue and pointer records.
