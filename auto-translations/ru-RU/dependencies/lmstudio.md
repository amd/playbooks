<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### LM Studio

<!-- @os:windows -->

<!-- @device:halo_box -->
LM Studio можно установить из **AMD Ryzen™ AI Developer Center**. Перейдите на вкладку **Updates** и установите LM Studio, если она ещё не установлена.

Чтобы LM Studio могла видеть предустановленные модели, перейдите в Settings > General > Models Directory. Затем измените путь на `C:\Users\Public\models`

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_windows_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
1. Скачайте установщик отсюда: [https://lmstudio.ai/download](https://lmstudio.ai/download)
2. Установите. 
<!-- @device:end -->

> Совет: После установки запустите LM Studio один раз, чтобы инициализировать CLI (`lms`).

<!-- @test:id=lmstudio-cli-windows timeout=60 hidden=True -->
```powershell
lms --help
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
> Примечание: Вы можете установить либо .deb, либо AppImage. 
1. Скачайте appimage отсюда: [https://lmstudio.ai/download?os=linux](https://lmstudio.ai/download?os=linux)
2. выполните `sudo apt install libfuse2`  
3. выполните `cd ~/Downloads`  
4. выполните `chmod +x LM-Studio-*.AppImage`  
5. выполните `./LM-Studio-*.AppImage`  
> Совет: После установки запустите LM Studio один раз, чтобы инициализировать CLI (`lms`).

<!-- @device:halo_box -->
Чтобы LM Studio могла видеть предустановленные модели, перейдите в Settings > General > Models Directory. Затем измените путь на `/var/cache/models`.

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_linux_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @test:id=lmstudio-cli-linux timeout=60 hidden=True -->
```bash
lms --help
```
<!-- @test:end --> 
<!-- @os:end -->