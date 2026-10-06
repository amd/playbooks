#!/usr/bin/env bash
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

sudo apt-get update || exit 1
sudo apt-get install -y podman podman-compose || exit 1
# Best-effort: docker-compose-plugin only exists in Docker's apt repo.
sudo apt-get install -y docker-compose-plugin || true
