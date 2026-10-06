# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

if (-not (Get-Process LemonadeServer -ErrorAction SilentlyContinue)) {
  Start-Process "$env:LOCALAPPDATA\lemonade_server\bin\LemonadeServer.exe"
}
for ($i = 0; $i -lt 45; $i++) {
  if ((curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/health) -match 'ok') { exit 0 }
  Start-Sleep -Seconds 2
}
exit 1
