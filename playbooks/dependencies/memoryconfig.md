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

<!-- @os:windows -->
On Windows, adjust the memory in **AMD Software: Adrenalin Edition**: open it and
navigate to **Performance → Tuning → AMD Variable Graphics Memory**. Set the value
you need and reboot for the change to take effect.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

> **Backup method (BIOS).** If your system does not show the Variable Graphics
> Memory option in Adrenalin (some OEM systems hide it), set the **UMA Frame
> Buffer Size** in the system BIOS/UEFI instead: reboot, enter setup (usually
> **Del**, **F2**, or **Esc**), find **UMA Frame Buffer Size** — also labeled
> *Integrated Graphics* or *dedicated GPU memory*, often under **Advanced** or
> **AMD CBS → NBIO Common Options** — set it to the size you need, save, and
> reboot. Menu names vary by vendor, and some BIOS do not expose it either.
<!-- @os:end -->

<!-- @os:linux -->
<!-- @device:halo_box -->
On the AMD Ryzen™ AI Halo, adjust the shared memory in the pre-installed
**AMD Ryzen™ AI Developer Center**: open it, go to the **Settings** tab, and under
**Graphics Performance Settings** increase the **Shared Video Memory** slider.
Click **Apply Changes** and reboot for the change to take effect.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:halo,stx,krk -->
On Linux, raise the shared **GTT/TTM** pool so the GPU can map more system memory.
AMD recommends setting the minimum dedicated VRAM in the BIOS (0.5 GB) so the
maximum is available as shared memory.

1. Install the `amd-debug-tools` helper:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   pipx install amd-debug-tools
   ```

2. Query the current shared-memory limit:

   ```bash
   amd-ttm
   ```

3. Raise it (value in GB — pick a size that leaves headroom for the OS):

   ```bash
   amd-ttm --set <NUM>
   ```

4. Reboot for the change to take effect.

> **Note:** `amd-ttm` is the current tool; this will eventually be ported to
> `amd-smi`.
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:end -->
