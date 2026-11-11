# Public image options

See [Images and updates](guides/images-and-updates.md) for the authoritative image/archive policy and update effects.

- [Standard Home Assistant](reference/apps/homeassistant.md) versus [custom archive](reference/apps/homeassistant-custom.md).
- [Standard Node-RED](reference/apps/node_red.md) versus [custom archive/retained OIDC](reference/apps/node_red-custom.md).
- [Bitwarden](reference/apps/bitwarden.md) uses the exact official image digest selected by the library. Its private runtime environment is supplied separately.

Public variants never silently replace custom archives, data, palettes or authentication. Each profile page states what source and controller checks establish and what still needs verification during installation.
