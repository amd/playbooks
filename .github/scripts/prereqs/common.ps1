# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

# Shared helpers for prereq scripts. Dot-source with: . "$PSScriptRoot\common.ps1"

# Start without inheriting this step's output pipe; an inheriting child stalls the step past its timeout.
function Start-Detached {
  [CmdletBinding(SupportsShouldProcess)]
  param([Parameter(Mandatory)][string]$FilePath, [string[]]$ArgumentList)
  $params = @{ FilePath = $FilePath; WindowStyle = 'Hidden'; PassThru = $true }
  if ($ArgumentList) { $params.ArgumentList = $ArgumentList }
  if ($PSCmdlet.ShouldProcess($FilePath, 'Start detached')) { Start-Process @params }
}

function Test-Port {
  param([Parameter(Mandatory)][int]$Port)
  [bool](Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue)
}

function Wait-Port {
  param([Parameter(Mandatory)][int]$Port, [int]$TimeoutSeconds = 60)
  $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
  while (-not (Test-Port $Port)) {
    if ((Get-Date) -ge $deadline) { return $false }
    Start-Sleep -Seconds 2
  }
  return $true
}
