#!/usr/bin/env bash
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

# Docker Desktop for Linux only needs starting; never add a second engine beside it.
if dpkg -s docker-desktop >/dev/null 2>&1; then
  XDG_RUNTIME_DIR="/run/user/$(id -u)" systemctl --user start docker-desktop || exit 1
  engine() { docker version --format '{{.Server.Version}}'; }
else
  # As the provisioning scripts do: Docker CE from get.docker.com.
  command -v dockerd >/dev/null 2>&1 || { curl -fsSL https://get.docker.com | sh || exit 1; }
  sudo usermod -aG docker "$(id -un)" || exit 1
  sudo systemctl enable --now docker || exit 1
  # The docker group reaches the runner only after its service restarts.
  engine() { sudo docker version --format '{{.Server.Version}}'; }
fi
for _ in $(seq 1 60); do
  engine >/dev/null 2>&1 && exit 0
  sleep 5
done
exit 1
