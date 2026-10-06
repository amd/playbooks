#!/usr/bin/env bash
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

set -o pipefail
# Add the Microsoft source only if none exists: a second one with a different Signed-By breaks apt.
if [ ! -f /etc/apt/sources.list.d/vscode.list ] && [ ! -f /etc/apt/sources.list.d/vscode.sources ]; then
  sudo apt-get update || exit 1
  sudo apt-get install -y wget gpg || exit 1
  sudo install -d -m 0755 /etc/apt/keyrings || exit 1
  wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor \
    | sudo tee /etc/apt/keyrings/microsoft.gpg >/dev/null || exit 1
  sudo chmod 0644 /etc/apt/keyrings/microsoft.gpg || exit 1
  echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/repos/code stable main" \
    | sudo tee /etc/apt/sources.list.d/vscode.list >/dev/null || exit 1
fi
sudo apt-get update || exit 1
sudo apt-get install -y code
