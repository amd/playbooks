<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->
### AMD GPU Driver

<!-- @device:halo,stx,krk -->
Update to the latest AMD GPU driver using `AMD Software: Adrenalin Edition™`.

1. Open `AMD Software: Adrenalin Edition` from your Start menu or system tray.
2. Navigate to **Driver and Software**, click **Manage Updates**.
3. If an update is available, follow the prompts to download and install.
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
Install **AMD Software: Adrenalin Edition** to get the latest AMD GPU driver. For the download link and instructions, see [Install AMD Software: Adrenalin Edition](https://rocm.docs.amd.com/en/7.13.0-preview/install/rocm.html).

Once installed, you can check for updates from `AMD Software: Adrenalin Edition` > **Driver and Software** > **Manage Updates**.
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=amd-gpu-visible-windows timeout=60 hidden=True -->
```powershell
Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion
```
<!-- @test:end -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
### AMD GPU Driver

Install the AMD GPU Driver (amdgpu) using the Radeon Software for Linux (RSL) flow. For instructions for your distribution, see [Install the kernel driver](https://rocm.docs.amd.com/en/7.13.0-preview/install/rocm.html).

<!-- @device:end -->
<!-- @os:end -->
