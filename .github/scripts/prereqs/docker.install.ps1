# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

. "$PSScriptRoot\common.ps1"
# The runners install Docker Desktop per user; winget installs it machine-wide.
$dirs = @((Join-Path $env:LOCALAPPDATA 'Programs\DockerDesktop'), (Join-Path $env:ProgramFiles 'Docker\Docker'))
function Find-Docker { $dirs | Where-Object { Test-Path (Join-Path $_ 'Docker Desktop.exe') } | Select-Object -First 1 }
$dir = Find-Docker
if (-not $dir) {
  # As the provisioning scripts do; winget's manifest also accepts the license and picks WSL 2.
  $p = Start-Detached winget @('install', '-e', '--id', 'Docker.DockerDesktop', '--accept-package-agreements', '--accept-source-agreements', '--silent')
  $p.WaitForExit()
  $dir = Find-Docker
  if (-not $dir) { exit 1 }
}
# A fresh install puts docker on the machine PATH, which this process predates.
$env:Path = (Join-Path $dir 'resources\bin') + ';' + $env:Path
# docker desktop start also recovers from docker desktop stop, which launching the app did not.
$start = Start-Detached (Join-Path $dir 'resources\bin\docker.exe') @('desktop', 'start')
if (-not $start.WaitForExit(300000) -or $start.ExitCode -ne 0) { Start-Detached (Join-Path $dir 'Docker Desktop.exe') | Out-Null }
for ($i = 0; $i -lt 60; $i++) {
  docker version --format '{{.Server.Version}}' 2>$null | Out-Null
  if ($LASTEXITCODE -eq 0) { exit 0 }
  Start-Sleep -Seconds 5
}
exit 1
