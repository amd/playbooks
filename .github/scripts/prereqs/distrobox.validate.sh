#!/usr/bin/env bash
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

export PATH="$HOME/.local/bin:$PATH"
podman --version && { distrobox version 2>/dev/null || distrobox --version; } && pipx --version
