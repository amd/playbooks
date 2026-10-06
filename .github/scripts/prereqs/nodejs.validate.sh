#!/usr/bin/env bash
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

hash -r 2>/dev/null
NODEBIN="$(command -v node || echo none)"
echo "node=$NODEBIN npm=$(command -v npm || echo none)"
{ node --version && npm --version; } || exit 1
case "$NODEBIN" in
  */linuxbrew/*) echo 'homebrew node accepted'; exit 0 ;;
esac
node -e 'process.exit(parseInt(process.versions.node.split(".")[0],10) >= 24 ? 0 : 1)'
