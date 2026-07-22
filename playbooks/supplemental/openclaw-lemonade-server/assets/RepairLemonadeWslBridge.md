Keep the WSL <-> Lemonade Bridge Working Automatically (Optional)
================================================================

WSL2 runs on a virtual network whose gateway IP can change after a restart
(for example after "wsl --shutdown" or a reboot). When that happens, the
Windows port proxy that lets OpenClaw (inside WSL) reach Lemonade (on Windows)
points at the old IP, and the bridge stops working.

This optional helper script detects a broken bridge and rebuilds the port
proxy and firewall rule against the current gateway IP. You can also schedule
it to run at startup and sign-in, so the bridge repairs itself automatically
and you never have to fix it by hand.

All the PowerShell steps below must be run in an elevated shell: right-click
Windows PowerShell and choose "Run as administrator".

> Lemonade Server must be running on Windows for the bridge to work. Lemonade should be running before the bridge repairs automatically after a reboot, otherwise there is nothing for the bridge to point to. The script below waits up to about 2 minutes for Lemonade to become ready before it repairs the bridge, which absorbs the normal start-up delay at boot.


1. Create the script file
-------------------------

```powershell
New-Item -ItemType Directory -Force C:\Scripts | Out-Null
notepad C:\Scripts\Repair-LemonadeWslBridge.ps1
```


2. Paste the following into the file and save it
------------------------------------------------

```powershell
$ErrorActionPreference = "Stop"
$Distro = "Ubuntu-24.04"
$LemonadePort = 13305
$PrivateRemoteRanges = @("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16")

function Test-UrlFromWindows {
  param([string]$Url)
  $oldPreference = $ErrorActionPreference
  $ErrorActionPreference = "Continue"
  try {
    curl.exe -fsS --max-time 5 $Url *> $null
    return ($LASTEXITCODE -eq 0)
  }
  finally {
    $ErrorActionPreference = $oldPreference
  }
}

function Test-UrlFromWsl {
  param([string]$Url)
  $oldPreference = $ErrorActionPreference
  $ErrorActionPreference = "Continue"
  try {
    wsl -d $Distro -- bash -lc "curl -fsS --max-time 5 '$Url' >/dev/null 2>/dev/null" *> $null
    return ($LASTEXITCODE -eq 0)
  }
  finally {
    $ErrorActionPreference = $oldPreference
  }
}

$WslGateway = (wsl -d $Distro -- bash -lc "ip route show default | sed -n 's/^default via \([^ ]*\).*/\1/p' | head -1").Trim()
if (-not $WslGateway) {
  throw "Could not determine WSL gateway IP"
}

$NativeUrl = "http://127.0.0.1:$LemonadePort/api/v1/models"
$BridgeUrl = "http://${WslGateway}:$LemonadePort/api/v1/models"
Write-Host "Current WSL gateway IP: $WslGateway"

# Wait for native Windows Lemonade to be ready before touching the bridge. At
# boot the scheduled task can start before Lemonade has finished loading, so we
# poll for up to ~2 minutes instead of failing immediately.
$nativeReady = $false
for ($i = 0; $i -lt 60; $i++) {
  if (Test-UrlFromWindows $NativeUrl) { $nativeReady = $true; break }
  Write-Host "Waiting for Lemonade to be ready at $NativeUrl ..."
  Start-Sleep -Seconds 2
}
if (-not $nativeReady) {
  throw "Native Windows Lemonade is not reachable at $NativeUrl after waiting. Make sure Lemonade Server is running and set to start automatically at login."
}
Write-Host "OK: Native Windows Lemonade is reachable"

if (Test-UrlFromWsl $BridgeUrl) {
  Write-Host "OK: The WSL Lemonade bridge is already working"
  exit 0
}
Write-Host "The WSL Lemonade bridge is not working. Recreating the port proxy and firewall rule..."

netsh interface portproxy reset
Remove-NetFirewallRule -DisplayName "Lemonade-WSL" -ErrorAction SilentlyContinue
Restart-Service iphlpsvc -Force
Set-Service iphlpsvc -StartupType Automatic

netsh interface portproxy add v4tov4 `
  listenaddress=$WslGateway listenport=$LemonadePort `
  connectaddress=127.0.0.1 connectport=$LemonadePort

New-NetFirewallRule `
  -DisplayName "Lemonade-WSL" `
  -Direction Inbound `
  -Protocol TCP `
  -LocalAddress $WslGateway `
  -LocalPort $LemonadePort `
  -RemoteAddress $PrivateRemoteRanges `
  -Action Allow | Out-Null

Start-Sleep -Seconds 2

Write-Host "Current portproxy rules:"
netsh interface portproxy show all

if (-not (Test-UrlFromWindows $BridgeUrl)) {
  throw "Windows portproxy is still not reachable at $BridgeUrl"
}
if (-not (Test-UrlFromWsl $BridgeUrl)) {
  throw "WSL still cannot reach Windows Lemonade through $BridgeUrl"
}
Write-Host "OK: WSL Lemonade bridge repaired successfully"
```


3. Run it once to confirm the bridge is healthy
-----------------------------------------------

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\Scripts\Repair-LemonadeWslBridge.ps1
```

You should see an "OK: ..." message.

> If it reports that Lemonade is not reachable even after the wait, start Lemonade Server on Windows, then run the script again.


4. (Optional) Run it automatically at startup and sign-in
---------------------------------------------------------

Register a scheduled task so the bridge is checked and repaired every time you
start or sign in to the machine:

```powershell
$TaskName = "Repair Lemonade WSL Bridge"
$ScriptPath = "C:\Scripts\Repair-LemonadeWslBridge.ps1"

$Action = New-ScheduledTaskAction `
  -Execute "powershell.exe" `
  -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$ScriptPath`""

$TriggerAtStartup = New-ScheduledTaskTrigger -AtStartup
$TriggerAtLogon = New-ScheduledTaskTrigger -AtLogOn

$Principal = New-ScheduledTaskPrincipal `
  -UserId "$env:USERDOMAIN\$env:USERNAME" `
  -LogonType Interactive `
  -RunLevel Highest

Register-ScheduledTask `
  -TaskName $TaskName `
  -Action $Action `
  -Trigger $TriggerAtStartup, $TriggerAtLogon `
  -Principal $Principal `
  -Force
```


5. Test the scheduled task
--------------------------

```powershell
Start-ScheduledTask -TaskName "Repair Lemonade WSL Bridge"
Start-Sleep -Seconds 10
Get-ScheduledTaskInfo -TaskName "Repair Lemonade WSL Bridge"
```

A "LastTaskResult" of 0 means the task ran successfully.


6. (Optional) Confirm the bridge from WSL
-----------------------------------------

Open your WSL terminal and verify that OpenClaw can reach Lemonade through the
bridge:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -fsS "http://$WINDOWS_HOST:13305/api/v1/models" >/dev/null && echo "OK: WSL can reach Lemonade"
```
