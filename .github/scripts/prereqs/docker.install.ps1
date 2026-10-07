# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

# Only starts an installed Docker Desktop and waits for its engine; installing it is out of scope.
. "$PSScriptRoot\common.ps1"
$exe = Join-Path $env:ProgramFiles 'Docker\Docker\Docker Desktop.exe'
if (-not (Test-Path $exe)) { Write-Output 'Docker Desktop is not installed'; exit 1 }
if (-not (Get-Process 'Docker Desktop' -ErrorAction SilentlyContinue)) { Start-Detached $exe | Out-Null }
for ($i = 0; $i -lt 60; $i++) {
  docker version --format '{{.Server.Version}}' 2>$null | Out-Null
  if ($LASTEXITCODE -eq 0) { exit 0 }
  Start-Sleep -Seconds 5
}
exit 1
