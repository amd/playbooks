# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

# Native Node.js and npm, major >= 24 like the Linux check (current n8n requires it).
$v = node --version
if (-not $?) { exit 1 }
npm --version | Out-Null
if (-not $?) { exit 1 }
Write-Output "node $v"
if ([int]($v.TrimStart('v').Split('.')[0]) -ge 24) { exit 0 }
exit 1
