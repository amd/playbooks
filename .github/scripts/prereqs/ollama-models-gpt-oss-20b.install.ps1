# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

. "$PSScriptRoot\common.ps1"
# Start the server detached first: the ollama CLI would auto-start one that inherits this step's pipe.
if (-not (Test-Port 11434)) { Start-Detached ollama @('serve') | Out-Null }
if (-not (Wait-Port 11434 -TimeoutSeconds 60)) { exit 1 }
ollama pull gpt-oss:20b
exit $LASTEXITCODE
