<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

## Install AMD Software: Adrenalin Edition

Download and install the latest **AMD Software: Adrenalin Edition** from
[amd.com/en/products/software/adrenalin.html](https://www.amd.com/en/products/software/adrenalin.html).

<!-- @os:windows -->
> **Note:** The installer may not create a Start menu shortcut. If you can't find
> it, launch it manually from
> `C:\Program Files\AMD\CNext\CNext\RadeonSoftware.exe`.

<!-- CI-only presence check: confirm Adrenalin is installed at the documented
     path. Hidden from the website; non-failing so a runner without Adrenalin
     does not block unrelated playbooks. -->
<!-- @test:id=adrenalin-installed-windows timeout=60 hidden=True continue_on_error=true -->
```powershell
if (Test-Path "C:\Program Files\AMD\CNext\CNext\RadeonSoftware.exe") {
  Write-Host "OK: AMD Software Adrenalin Edition is installed"
} else {
  Write-Error "RadeonSoftware.exe not found at C:\Program Files\AMD\CNext\CNext"
  exit 1
}
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- CI-only presence check: there is no Adrenalin on Linux, so confirm the GPU
     is reachable via ROCm instead. Hidden from the website; non-failing. -->
<!-- @test:id=gpu-visible-linux timeout=60 hidden=True continue_on_error=true -->
```bash
if command -v rocminfo >/dev/null 2>&1 && rocminfo | grep -q gfx; then
  echo "OK: GPU visible to ROCm"
else
  echo "GPU not visible via rocminfo" >&2
  exit 1
fi
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
## Advanced: increasing GPU memory (optional)

You may need to increase the memory allocated to the GPU to run certain larger
models or longer contexts. These devices use unified memory — the GPU shares
system RAM — so this means letting the GPU claim more of that shared pool. Leave
roughly 20% of system RAM for the operating system. This step is optional; the
default allocation is enough for most workloads.

> **Note:** This is configured in the system BIOS/UEFI. Some system vendors lock
> the memory configuration, so the setting may not be available on every machine.

<!-- @os:windows -->
On Windows, set the **UMA Frame Buffer Size** (dedicated graphics memory) in the
system BIOS/UEFI:

1. Reboot and enter setup (usually **Del**, **F2**, or **Esc** during startup).
2. Find **UMA Frame Buffer Size** — also labeled *Integrated Graphics* or
   *dedicated GPU memory*, often under **Advanced** or **AMD CBS → NBIO Common
   Options**. Menu names vary by system vendor.
3. Set it to the size you need (for large models, the maximum available, e.g. 96 GB).
4. Save and reboot.
<!-- @os:end -->

<!-- @os:linux -->
On Linux, keep the BIOS carve-out small and raise the shared **GTT/TTM** pool
instead — the GPU maps system RAM dynamically, so a large fixed BIOS reservation
just wastes memory.

1. **BIOS/UEFI:** reboot, enter setup (**Del**, **F2**, or **Esc**), find **UMA
   Frame Buffer Size** (*Integrated Graphics* / dedicated VRAM; often under
   **Advanced** or **AMD CBS → NBIO Common Options**), and set it to the **minimum**
   (512 MB if offered, otherwise the lowest value such as 2 GB). Save and reboot.
   Menu names vary by vendor.

2. Install the `amd-debug-tools` helper:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   pipx install amd-debug-tools
   ```

3. Query the current shared-memory limit:

   ```bash
   amd-ttm
   ```

4. Raise it (value in GB — pick a size that leaves headroom for the OS):

   ```bash
   amd-ttm --set <NUM>
   ```

5. Reboot for the change to take effect.

> **Note:** Requires kernel **6.16.9 or newer**. Older kernels cap GPU-visible
> memory at about 15.5 GB regardless of this setting.
<!-- @os:end -->

<!-- @device:end -->
