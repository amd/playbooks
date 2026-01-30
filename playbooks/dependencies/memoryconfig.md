### Memory configuration for running large models

<!-- @os:windows -->

On Windows, to run larger models that require higher memory, we need to use the AMD Variable Graphics Memory (iGPU VRAM) allocation. Although 64 GB is adequate for most workloads, running the largest models with high context may require 96 GB.

This can be done by opening AMD Software: Adrenalin™ Edition control panel and navigating to: `Performance > Tuning > AMD Variable Graphics Memory`.  Please reboot the system for the changes to take effect.

<!-- @os:end -->

<!-- @os:linux -->

On Linux, ROCm utilizes a shared system memory pool, and this pool is configured by default to half the system memory.

This amount can be increased by changing the kernel’s Translation Table Manager (TTM) page setting, with the following instructions. AMD recommends setting the minimum dedicated VRAM in the BIOS (0.5GB)

* Install the pipx utility and add the path for pipx installed wheels into the system search path.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Install the amd-debug-tools wheel from PyPi.
  ```bash
  pipx install amd-debug-tools
  ```

* Run the amd-ttm tool to query the current settings for shared memory.
  ```bash
  amd-ttm
  ```

* Reconfigure shared memory settings by using the --set argument (units in GB).
  ```bash
  amd-ttm --set <NUM>
  ```

* Reboot the system for changes to take effect.


For `amd-ttm` usage examples, see the [ROCm documentation](https://rocm.docs.amd.com/projects/radeon-ryzen/en/docs-7.0.2/docs/install/installryz/native_linux/install-ryzen.html#amd-ttm-usage-examples).

<!-- @os:end -->
