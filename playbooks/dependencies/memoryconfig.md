### Memory configuration for running large models

<!-- @os:windows -->

On Windows, to run larger models that require higher memory, we need to use the AMD Variable Graphics Memory (iGPU VRAM) allocation. 

> Note: 64 GB is adequate for most workloads but if you want to run the largest models with high context, you will need to set it to 96 GB.  

This can be done by opening AMD Software: Adrenalin™ Edition control panel and navigating to: Performance > Tuning > AMD Variable Graphics Memory.  Please reboot the system for the changes to take effect.

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


#### amd-ttm Usage Examples

##### Query effective memory settings in the current kernel
```bash
amd-ttm
💻 Current TTM pages limit: 16469033 pages (62.82 GB)
💻 Total system memory: 125.65 GB
```

##### Set usable shared memory
```bash
❯ amd-ttm --set 100
🐧 Successfully set TTM pages limit to 26214400 pages (100.00 GB)
🐧 Configuration written to /etc/modprobe.d/ttm.conf
○ NOTE: You need to reboot for changes to take effect.
Would you like to reboot the system now? (y/n): y
```

##### Clear TTM setting and revert to kernel defaults
```bash
❯ amd-ttm --clear
🐧 Configuration /etc/modprobe.d/ttm.conf removed
Would you like to reboot the system now? (y/n): y
```

<!-- @os:end -->
