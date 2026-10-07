# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

# Presence only, as in the provisioning scripts: upgrading a working Node.js can break npm globals such as n8n.
node --version
if (-not $?) { exit 1 }
npm --version | Out-Null
if (-not $?) { exit 1 }
exit 0
