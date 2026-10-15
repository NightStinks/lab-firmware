# LAB. firmware

Built firmware, update feeds and the browser installer for LAB. devices, served at
https://nightstinks.github.io/lab-firmware/ (GitHub Pages). Testing builds for now.

The product source (`lab-presence`, `lab-zones`) is private. This repo only holds what has to be
public: the built `.bin` files, the manifests and the install pages.

| Path | What |
|---|---|
| `index.html`, `style.css` | Landing page and shared brand styles |
| `<product>/index.html` | Browser installer (ESP Web Tools 10.4.0, Chrome or Edge) |
| `docs/` | User docs: setup, updates, moving, reset, troubleshooting |
| `home-assistant/` | My Home Assistant buttons: add the LAB. app (`d5b43fc5_lab`), find or add sensors |
| `<product>/manifest.json` | The feed. Used by the installer and by installed sensors for updates |
| `<product>/<version>/` | Every published build, kept for rollback |
| `.github/workflows/build.yml` | Reusable build-and-publish workflow, called by each product repo on release |
| `scripts/publish.py` | Copies a build in and rewrites the manifest. Used by the workflow, or by hand |
| `scripts/setup-deploy-key.sh` | One-off: lets the product repos push here |

## How a release gets to sensors

1. A release `v<version>` is published in a product repo.
2. Its workflow calls `build.yml` here: compile with the pinned ESPHome, attach the `.bin` files to the release, add them under `<product>/<version>/` and point `manifest.json` at them.
3. Each sensor reads its `manifest.json` every 6 hours (the URL is built into the firmware as `update_url`). If the version differs from its own, Home Assistant shows "Update available".

## Rolling back

Point `<product>/manifest.json` at an older `<version>/` folder (paths and `md5`), or run
`scripts/publish.py` again with that folder's files, and push. Sensors that took the bad build
see the older version as an update. A build that crashes within about a minute of booting is
rolled back by the sensor itself (ESP-IDF app rollback).

## Before a domain exists

The feed URL lives on `nightstinks.github.io` for now. When a domain is bought, publish one
release whose `update_url` points at the new address. Units move over when they install it,
so keep this site up until every unit has.
