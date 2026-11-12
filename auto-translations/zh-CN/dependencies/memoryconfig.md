<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

## 安装 AMD Software: Adrenalin Edition

从 [amd.com/en/products/software/adrenalin.html](https://www.amd.com/en/products/software/adrenalin.html) 下载并安装最新版 **AMD Software: Adrenalin Edition**。

<!-- @os:windows -->
> **注意：** 安装程序可能不会创建开始菜单快捷方式。如果你找不到它，可以从
> `C:\Program Files\AMD\CNext\CNext\RadeonSoftware.exe` 手动启动。

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

<!-- @device:halo_box,halo,grgh,stx,krk -->
## 高级：增加 GPU 内存（可选）

为了运行某些更大的模型或更长的上下文，你可能需要增加分配给 GPU 的内存。这些设备使用统一内存——GPU 与系统共享 RAM——因此这意味着让 GPU 占用更多的共享内存池。请为操作系统保留大约 20% 的系统 RAM。此步骤为可选项；默认分配对大多数工作负载来说已经足够。

<!-- @os:windows -->
在 Windows 上，通过 **AMD Software: Adrenalin Edition** 调整内存：打开它并导航到 **Performance → Tuning → AMD Variable Graphics Memory**。设置你需要的值，然后重启以使更改生效。

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

> **备用方法（BIOS）。** 如果你的系统在 Adrenalin 中没有显示 Variable Graphics Memory 选项（部分 OEM 系统会隐藏该选项），可以改为在系统 BIOS/UEFI 中设置 **UMA Frame Buffer Size**：重启，进入设置（通常是 **Del**、**F2** 或 **Esc**），找到 **UMA Frame Buffer Size**——也可能标记为 *Integrated Graphics* 或 *dedicated GPU memory*，通常位于 **Advanced** 或 **AMD CBS → NBIO Common Options** 下——将其设置为你需要的大小，保存并重启。菜单名称因厂商而异，部分 BIOS 也可能不提供此选项。
<!-- @os:end -->

<!-- @os:linux -->
<!-- @device:halo_box -->
在 AMD Ryzen™ AI Halo 上，通过预装的 **AMD Ryzen™ AI Developer Center** 调整共享内存：打开它，进入 **Settings** 标签页，在 **Graphics Performance Settings** 下增大 **Shared Video Memory** 滑块。点击 **Apply Changes** 并重启以使更改生效。

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:halo,grgh,stx,krk -->
在 Linux 上，提高共享 **GTT/TTM** 池的大小，以便 GPU 能够映射更多的系统内存。AMD 建议在 BIOS 中将专用显存的最小值设置为（0.5 GB），这样最大容量就可以作为共享内存使用。

1. 安装 `amd-debug-tools` 辅助工具：

   ```bash
   sudo apt install pipx
   pipx ensurepath
   pipx install amd-debug-tools
   ```

2. 查询当前共享内存限制：

   ```bash
   amd-ttm
   ```

3. 提高该限制（单位为 GB——请选择一个能为操作系统留出余量的大小）：

   ```bash
   amd-ttm --set <NUM>
   ```

4. 重启以使更改生效。

> **注意：** `amd-ttm` 是当前的工具；未来会移植到 `amd-smi`。
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:end -->