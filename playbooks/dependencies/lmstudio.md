<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### LM Studio

<!-- @os:windows -->

1. Download the installer from here: [https://lmstudio.ai/download](https://lmstudio.ai/download)
2. Install. 
> Tip: After installing, launch LM Studio once to initialize the CLI (`lms`).

<!-- @test:id=lmstudio-cli-windows timeout=60 hidden=True -->
```powershell
lms --help
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
1. Download the appimage from here: [https://lmstudio.ai/download?os=linux](https://lmstudio.ai/download?os=linux)
2. run `sudo apt install libfuse2`  
3. run `cd ~/Downloads`  
4. run `chmod +x LM-Studio-*.AppImage`  
5. run `./LM-Studio-*.AppImage`  

<!-- @test:id=lmstudio-cli-linux timeout=60 hidden=True -->
```bash
lms --help
```
<!-- @test:end --> 
<!-- @os:end -->
