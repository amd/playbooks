# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

. "$PSScriptRoot\common.ps1"
$apps = @((Join-Path $env:LOCALAPPDATA 'Programs\LM Studio\LM Studio.exe'), (Join-Path $env:ProgramFiles 'LM Studio\LM Studio.exe'))
function Find-App { $apps | Where-Object { Test-Path $_ } | Select-Object -First 1 }
$lms = Join-Path $env:USERPROFILE '.lmstudio\bin\lms.exe'
if (-not (Find-App)) {
  # As the provisioning scripts do.
  $p = Start-Detached winget @('install', '-e', '--id', 'ElementLabs.LMStudio', '--accept-package-agreements', '--accept-source-agreements', '--silent')
  $p.WaitForExit()
  if (-not (Find-App)) { exit 1 }
}
# LM Studio installs its lms CLI on first launch.
if (-not (Test-Path $lms)) {
  if (-not (Get-Process 'LM Studio' -ErrorAction SilentlyContinue)) { Start-Detached (Find-App) @('--run-as-service') | Out-Null }
  for ($i = 0; $i -lt 60 -and -not (Test-Path $lms); $i++) { Start-Sleep -Seconds 5 }
  if (-not (Test-Path $lms)) { exit 1 }
}
# As the provisioning scripts do: start LM Studio's daemon and server at logon.
$task = 'LM Studio Server'
if (-not (Get-ScheduledTask -TaskName $task -ErrorAction SilentlyContinue)) {
  $command = "& { `$env:PATH = '$(Split-Path $lms);' + `$env:PATH; lms daemon up; lms server start --port 1234 }"
  $action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -NonInteractive -Command `"$command`""
  # The identity the OS reports: on these workgroup machines $env:USERDOMAIN does not resolve.
  $principal = New-ScheduledTaskPrincipal -UserId ([Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Highest
  $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
  Register-ScheduledTask -TaskName $task -Action $action -Trigger (New-ScheduledTaskTrigger -AtLogOn) -Principal $principal -Settings $settings -Force | Out-Null
}
if (Get-ScheduledTask -TaskName $task -ErrorAction SilentlyContinue) { exit 0 }
exit 1
