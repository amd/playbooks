#!/usr/bin/env bash
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

# Validate checks the live health endpoint, so installing the package is not enough.
if ! command -v lemonade >/dev/null 2>&1 && ! command -v lemonade-server >/dev/null 2>&1; then
  sudo add-apt-repository -y ppa:lemonade-team/stable || exit 1
  sudo apt-get update || exit 1
  sudo apt-get install -y lemonade-server || exit 1
fi
sudo systemctl enable --now lemond || exit 1
for _ in $(seq 1 60); do
  curl -sf --max-time 2 http://127.0.0.1:13305/api/v1/health >/dev/null && exit 0
  sleep 2
done
exit 1
