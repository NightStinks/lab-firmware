#!/usr/bin/env bash
# One-off: lets the private product repos' release workflows push builds here.
# Makes a new SSH key, adds the public half to lab-firmware as a write deploy key, and stores
# the private half as the LAB_FIRMWARE_DEPLOY_KEY secret in each product repo. The key is
# never written to disk outside a temp folder that is removed at the end.
set -euo pipefail

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

ssh-keygen -t ed25519 -N "" -C "lab-firmware publish" -f "$tmp/key" -q
gh repo deploy-key add "$tmp/key.pub" --repo NightStinks/lab-firmware --title "Product release workflows" --allow-write
for repo in NightStinks/lab-presence NightStinks/lab-zones; do
  gh secret set LAB_FIRMWARE_DEPLOY_KEY --repo "$repo" < "$tmp/key"
done
echo "Done. Publishing a release in lab-presence or lab-zones will now update the site."
