#!/usr/bin/env bash
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

set -o pipefail
# Distro node packages conflict with NodeSource's; remove the installed ones first.
mapfile -t distro < <(dpkg-query -W -f='${db:Status-Abbrev} ${Package}\n' nodejs npm libnode-dev libnode72 node-corepack 2>/dev/null | awk '$1 ~ /^ii/ {print $2}')
if [ "${#distro[@]}" -gt 0 ]; then
  sudo apt-get remove -y --purge "${distro[@]}" || exit 1
  sudo apt-get autoremove -y
fi
curl -fsSL https://deb.nodesource.com/setup_24.x | sudo -E bash - || exit 1
sudo apt-get install -y --allow-downgrades --allow-change-held-packages nodejs \
  && node --version && npm --version
