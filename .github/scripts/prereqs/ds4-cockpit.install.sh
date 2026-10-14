#!/usr/bin/env bash
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

export PATH="$HOME/.local/bin:$PATH"
pipx install "git+https://github.com/kyuz0/strix-halo-ds4-toolbox.git#subdirectory=ds4-strix-halo-cockpit" \
  && pipx ensurepath >/dev/null 2>&1
command -v ds4-cockpit || ls "$HOME/.local/bin/ds4-cockpit"
