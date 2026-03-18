### AMD GPU Driver

<!-- @os:windows -->

Update to the latest AMD GPU driver using AMD Software: Adrenalin Edition:

1. Open **AMD Software: Adrenalin Edition** from your Start menu or system tray.
2. Navigate to **Driver and Software**, click **Manage Updates**.
4. If an update is available, follow the prompts to download and install.

<!-- @test:id=amd-gpu-visible-windows timeout=60 hidden=True -->
```powershell
Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->

Download and install the latest AMD GPU driver for Linux:

1. Visit the [AMD Linux Drivers](https://amd.com/en/support/download/linux-drivers.html) page.
2. Follow the installation instructions provided on the download page.

<!-- @test:id=amd-gpu-visible-linux timeout=60 hidden=True -->
```bash
set -euo pipefail
sudo -n apt-get update -y
sudo -n apt-get install -y rocm-smi
rocm-smi
rocm-smi --showproductname
test -d /opt/rocm
test -e /opt/rocm/lib/libroctx64.so.4 -o -e /opt/rocm/lib/libroctx64.so
```
<!-- @test:end --> 
<!-- @os:end -->
