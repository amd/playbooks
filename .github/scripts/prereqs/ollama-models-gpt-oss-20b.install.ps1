# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

. "$PSScriptRoot\common.ps1"
# Start the server detached first: the ollama CLI would auto-start one that inherits this step's pipe.
if (-not (Test-Port 11434)) { Start-Detached ollama @('serve') | Out-Null }
if (-not (Wait-Port 11434 -TimeoutSeconds 60)) { exit 1 }
ollama pull gpt-oss:20b
if ($LASTEXITCODE -eq 0) { exit 0 }
# Hugging Face fallback when the Ollama registry fails: the same MXFP4 GGUF, named as CI expects.
ollama pull hf.co/ggml-org/gpt-oss-20b-GGUF:MXFP4
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
ollama cp hf.co/ggml-org/gpt-oss-20b-GGUF:MXFP4 gpt-oss:20b
exit $LASTEXITCODE
