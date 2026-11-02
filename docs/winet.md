# WiNet on Radios

Radios guest209 runs Zigbee2MQTT and WiNet in one guest deployment job. Preparation runs
once, followed by separate Zigbee2MQTT and WiNet steps, then one selected Zabbix
agent step. Radios depends on the MQTT guest, so the broker can serve telemetry
without waiting for Home Automation to finish. WiNet has no serial device,
browser endpoint or persistent database. Zigbee's coordinator and data remain
unchanged. The guest has 1 GiB RAM: 512 MiB for Zigbee2MQTT, 256 MiB for WiNet and
256 MiB reserved for Debian.

The WiNet image is published outside this repository at
[theaussiepom/winet-extractor](https://github.com/theaussiepom/home-assistant-repo/pkgs/container/winet-extractor).
Its immutable digest is in `images.json`. This is unmodified upstream 0.5.0
snapshot source at `6cd07d24fdaa01b89eb082dea43241c9fd3c0b98`, not a released 0.5.0
version and not the earlier custom certificate image. Its publication review
records the existing upstream dependency advisories; publication is not a claim
that the image has no vulnerabilities.

Private `paths.winet_options` selects an existing controller-owned mode-0600
options JSON file, outside Git. Supply explicit inverter credentials, polling,
analytics, site totals, discovery prefix and the declared MQTT endpoint. Existing
MQTT credentials must be preserved when changing the broker address. The file is
hashed with deployment inputs, rendered privately and mounted read-only at
`/data/options.json`. The renderer rejects extra inverters, custom certificate
fields, plaintext inverter transport and endpoint drift.

The added VLAN 107 interface has no default gateway or new inbound rule. PVE
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

The reference host carries VLAN107 on `vmbr1` through its service/IoT uplink;
`vmbr0` is the management uplink and carries only VLANs15/25. Match the physical
bridge VLAN membership before adoption. A guest firewall declaration also needs
active cluster firewall enforcement to take effect. Ordinary guest CD does not
enable that cluster-wide control, and configured rules alone are not evidence
that traffic is filtered.

The pinned upstream `getProperties.ts` HTTPS request and `winetHandler.ts` WSS
client both set `rejectUnauthorized: false`. `ssl: true` encrypts those initial
connections but does not authenticate the inverter certificate. A device able to
intercept traffic on the IoT link could obtain the configured inverter credentials.
The upstream WS fallback uses TCP8082, which the declared IoT policy does not permit.
The operator explicitly selected the unmodified upstream image and deferred the
former custom certificate work for this integration; its private adoption record
retains that decision. This policy does not change Proxmox, UDM, browser TLS or a
host trust store. Do not describe it as verified inverter TLS. Strict inverter
certificate authentication remains deferred, rather than silently inherited from
the earlier custom image.

The container health check reads the broker's retained publisher and inverter
availability. After deployment, independently confirm fresh sensor messages and
Home Assistant entities; retained availability alone does not prove fresh readings.
