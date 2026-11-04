# Public image options

The library offers explicit public profiles for a new Home Assistant or
Node-RED instance. Their software selections reference the official public
images declared in `images.json`. Selecting one does not replace another
instance's retained image or data.

| Profile | Image selection | Configuration |
| --- | --- | --- |
| `homeassistant` | Retained archive | Explicit retained integrations and capabilities |
| `homeassistant-public` | Official public image | New configuration; integrations selected separately |
| `node_red` | Retained archive | Explicit retained settings, palette and authentication |
| `node_red-public` | Official public image | Standard `/data`; no retained settings wrapper |

A new HA instance selects `homeassistant-public`, its guest and web interface,
and a config storage binding. Node-RED, recorder, MQTT, InfluxDB, Authentik and
ingress are separate selections. The mDNS helper additionally requires its
explicit runtime capability, Home interface and startup binding. Its network
capability is absent from the base HA runtime.

A new Node-RED instance selects `node_red-public` and its data binding. A public
image does not imply compatibility with custom nodes, credentials or retained
authentication settings. Authentication and exposure must be chosen explicitly;
an unselected strategy is not replaced by a different one during deployment.

The public profiles declare create-only directory initialization for HA config
(0:0) and Node-RED data (1000:1000), mode 0700, beneath a proven provider volume.
The framework changes ownership/mode only on the just-created directory through
its owned descriptor. A retained binding is unchanged; an existing unowned leaf
is refused. The profile owns this finite capability, with no instance override
or recursive ownership repair. Source declarations and vendor startup fixtures
do not establish actual deployment acceptance.

The official [HA container guide](https://www.home-assistant.io/installation/linux/)
and [Node-RED Docker guide](https://nodered.org/docs/getting-started/docker)
describe their image startup and persistence contracts. Hardware, custom nodes
and login integrations need their own selected capabilities and validation.

An unresolved retained archive refuses deployment. The compiler never substitutes
a public image for it. Public options use their declared catalogue selection;
there is no arbitrary registry override or automatic fallback.
