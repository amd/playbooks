#!/usr/bin/env bash
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

# Distro node packages conflict with NodeSource's; remove them first (absent ones are fine).
sudo apt-get remove -y --purge nodejs npm libnode-dev libnode72 node-corepack 2>/dev/null
sudo apt-get autoremove -y 2>/dev/null
curl -fsSL https://deb.nodesource.com/setup_24.x | sudo -E bash - \
  && sudo apt-get install -y --allow-downgrades --allow-change-held-packages nodejs \
  && node --version && npm --version
