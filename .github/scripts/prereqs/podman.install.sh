#!/usr/bin/env bash
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

sudo apt-get update || exit 1
sudo apt-get install -y podman podman-compose || exit 1
# Best-effort: docker-compose-plugin only exists in Docker's apt repo.
sudo apt-get install -y docker-compose-plugin || true
# As the provisioning scripts do: the runner's system service has no session bus, so use cgroupfs.
conf="$HOME/.config/containers/containers.conf"
if [ ! -f "$conf" ]; then
  mkdir -p "$(dirname "$conf")" || exit 1
  printf '[engine]\ncgroup_manager = "cgroupfs"\nevents_logger = "file"\n' > "$conf" || exit 1
fi
