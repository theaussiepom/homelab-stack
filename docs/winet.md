# WiNet on Radios

The Radios profile runs Zigbee2MQTT and WiNet in one guest deployment job. Preparation runs
once, followed by separate Zigbee2MQTT and WiNet steps, then one selected Zabbix
agent step. Radios depends on the MQTT guest, so the broker can serve telemetry
without waiting for Home Automation to finish. WiNet has no serial device,
browser endpoint or persistent database. Zigbee's coordinator and data remain
unchanged. The guest has 1 GiB RAM: 512 MiB for Zigbee2MQTT, 256 MiB for WiNet and
256 MiB reserved for Debian.

The WiNet image is selected by the authoritative [image catalog](../images.json).
Its existing upstream artifact policy is intentional. This repository does not
publish that image, and image selection is not a claim of vulnerability-free code.

Private `paths.winet_options` selects an existing controller-owned mode-0600
options JSON file, outside Git. Supply explicit inverter credentials, polling,
analytics, site totals, discovery prefix and the declared MQTT endpoint. Existing
MQTT credentials must be preserved when changing the broker address. The file is
hashed with deployment inputs, rendered privately and mounted read-only at
`/data/options.json`. The renderer rejects extra inverters, custom certificate
fields, plaintext inverter transport and endpoint drift.

The consumer-bound IoT interface has no default gateway or new inbound rule. PVE
`net2` declares an HTTPS egress limit to the selected inverter's TCP443 telemetry. Package/image HTTP
and HTTPS egress is bound to management `net0` and its selected source address;
it cannot provide an alternate allowance on the IoT interface, even when a
process selects the management source IP. MQTT uses the existing backend interface
and declared broker. Public addresses are examples; the site supplies retained
addresses and MACs.

Before adding a tagged interface, deliberately authorize the existing deployment
identity to use that exact Proxmox SDN VLAN path. The built-in `PVESDNUser` role
includes `SDN.Audit` and `SDN.Use`; a non-propagating grant can target
`/sdn/zones/localnetwork/<bridge>/<vlan>` without granting other VLANs. A firewall
rule does not grant API permission to attach its network. Preserve every failed
attempt and hold if this permission is missing; any fresh CD needs explicit
review and adoption of the exact failure evidence, rather than an automatic retry.

Consumers must verify physical bridge/VLAN membership and effective firewall
enforcement. Ordinary guest CD does not enable cluster-wide controls, and declared
rules alone are not evidence that traffic is filtered.

The pinned upstream `getProperties.ts` HTTPS request and `winetHandler.ts` WSS
client both set `rejectUnauthorized: false`. `ssl: true` encrypts those initial
connections but does not authenticate the inverter certificate. A device able to
intercept traffic on the IoT link could obtain the configured inverter credentials.
The upstream WS fallback uses TCP8082, which the declared IoT policy does not permit.
This selected-image limitation requires explicit consumer acceptance. It does not
change Proxmox, browser TLS or a host trust store. Do not describe the inverter
connection as certificate-authenticated TLS.

The container health check reads the broker's retained publisher and inverter
availability. After deployment, independently confirm fresh sensor messages and
Home Assistant entities; retained availability alone does not prove fresh readings.
