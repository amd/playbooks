# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

. "$PSScriptRoot\common.ps1"
$exe = Join-Path $env:ProgramFiles 'Docker\Docker\Docker Desktop.exe'
if (-not (Test-Path $exe)) {
  # As the provisioning scripts do; winget's manifest also accepts the license and picks WSL 2.
  $p = Start-Detached winget @('install', '-e', '--id', 'Docker.DockerDesktop', '--accept-package-agreements', '--accept-source-agreements', '--silent')
  $p.WaitForExit()
  if (-not (Test-Path $exe)) { exit 1 }
}
if (-not (Get-Process 'Docker Desktop' -ErrorAction SilentlyContinue)) { Start-Detached $exe | Out-Null }
# A fresh install puts docker on the machine PATH, which this process predates.
$env:Path = (Join-Path $env:ProgramFiles 'Docker\Docker\resources\bin') + ';' + $env:Path
for ($i = 0; $i -lt 60; $i++) {
  docker version --format '{{.Server.Version}}' 2>$null | Out-Null
  if ($LASTEXITCODE -eq 0) { exit 0 }
  Start-Sleep -Seconds 5
}
exit 1
