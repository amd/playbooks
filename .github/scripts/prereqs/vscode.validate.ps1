# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

code --version
if (-not $?) { exit 1 }
winget list --id Microsoft.VisualStudioCode -e --accept-source-agreements | Out-Null
exit $LASTEXITCODE
