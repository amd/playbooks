<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### LM Studio

<!-- @os:windows -->

<!-- @device:halo_box -->
LM Studio can be installed from the **AMD Ryzen™ AI Developer Center**. Go to the **Updates** tab and install LM Studio if it is not already present.

If your system has pre-installed models, navigate to Settings > General > Models Directory. Then change the path to `C:\Users\Public\models`

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_windows_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
1. Download the installer from here: [https://lmstudio.ai/download](https://lmstudio.ai/download)
2. Install. 
<!-- @device:end -->

> **Models:** If your system came with this playbook's model pre-installed, point LM Studio at the pre-installed models directory above to use it. Otherwise, download the model from LM Studio's **Discover** tab (search icon) before continuing.

> Tip: After installing, launch LM Studio once to initialize the CLI (`lms`).

<!-- @test:id=lmstudio-cli-windows timeout=60 hidden=True -->
```powershell
lms --help
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
> Note: You can choose to install either the .deb or the AppImage. 
1. Download the appimage from here: [https://lmstudio.ai/download?os=linux](https://lmstudio.ai/download?os=linux)
2. run `sudo apt install libfuse2`  
3. run `cd ~/Downloads`  
4. run `chmod +x LM-Studio-*.AppImage`  
5. run `./LM-Studio-*.AppImage`  
> Tip: After installing, launch LM Studio once to initialize the CLI (`lms`).

<!-- @device:halo_box -->
If your system has pre-installed models, navigate to Settings > General > Models Directory. Then change the path to `/var/cache/models`.

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_linux_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

> **Models:** If your system came with this playbook's model pre-installed, point LM Studio at the pre-installed models directory above to use it. Otherwise, download the model from LM Studio's **Discover** tab (search icon) before continuing.

<!-- @test:id=lmstudio-cli-linux timeout=60 hidden=True -->
```bash
lms --help
```
<!-- @test:end --> 
<!-- @os:end -->
