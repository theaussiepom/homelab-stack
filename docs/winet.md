# WiNet on the radio guest

Guest 209 runs Zigbee2MQTT and WiNet in one guest deployment job. Preparation runs
once, followed by separate Zigbee2MQTT and WiNet steps. WiNet has no serial device,
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

The added VLAN 107 interface has no default gateway or new inbound rule. Its new
rule selects the inverter over HTTPS/WSS port 443; MQTT uses the existing backend
interface and the broker's declared endpoint. Public addresses are examples; the
site supplies the actual retained addresses and MAC. Upstream encrypted transport
does not provide the former custom certificate verification.

The container health check reads the broker's retained publisher and inverter
availability. After deployment, independently confirm fresh sensor messages and
Home Assistant entities; retained availability alone does not prove fresh readings.
