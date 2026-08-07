<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->
<!--
Shared Lemonade server readiness gate. Adopt it with an "@require:lemonade-ready" tag placed
immediately before any step that talks to the Lemonade server, so the step waits for the
server instead of failing with "Could not connect to Lemonade server". Waits only; the
server is expected to auto-start. This file intentionally renders nothing on the website
(only hidden test blocks below), so adopters need no github-only wrapper.
-->

<!-- @os:windows -->
<!-- @test:id=lemonade-ready-windows timeout=300 hidden=True -->
```powershell
$health = $null
for ($i = 0; $i -lt 120; $i++) {
  $health = curl.exe -sf --max-time 2 http://127.0.0.1:13305/api/v1/health
  if ($health) { break }
  Start-Sleep -Seconds 1
}
if (-not $health) { throw "Lemonade server not ready on http://127.0.0.1:13305/api/v1/health" }
Write-Host "OK: Lemonade server is ready"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-ready-linux timeout=300 hidden=True -->
```bash
set -euo pipefail
health=""
for i in $(seq 1 120); do
  health="$(curl -sf --max-time 2 http://127.0.0.1:13305/api/v1/health || true)"
  if [ -n "$health" ]; then break; fi
  sleep 1
done
if [ -z "$health" ]; then
  echo "Lemonade server not ready on http://127.0.0.1:13305/api/v1/health"
  exit 1
fi
echo "OK: Lemonade server is ready"
```
<!-- @test:end -->
<!-- @os:end -->
