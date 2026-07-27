<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### LM Studio

<!-- @os:windows -->

<!-- @device:halo_box -->
LM Studio можна встановити з **AMD Ryzen™ AI Developer Center**. Перейдіть на вкладку **Updates** та встановіть LM Studio, якщо його ще немає.

Щоб дозволити LM Studio бачити попередньо встановлені моделі, перейдіть до Settings > General > Models Directory. Потім змініть шлях на `C:\Users\Public\models`

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_windows_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
1. Завантажте інсталятор звідси: [https://lmstudio.ai/download](https://lmstudio.ai/download)
2. Встановіть. 
<!-- @device:end -->

> Порада: Після встановлення запустіть LM Studio один раз, щоб ініціалізувати CLI (`lms`).

<!-- @test:id=lmstudio-cli-windows timeout=60 hidden=True -->
```powershell
lms --help
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
> Примітка: Ви можете обрати встановлення .deb або AppImage. 
1. Завантажте appimage звідси: [https://lmstudio.ai/download?os=linux](https://lmstudio.ai/download?os=linux)
2. виконайте `sudo apt install libfuse2`  
3. виконайте `cd ~/Downloads`  
4. виконайте `chmod +x LM-Studio-*.AppImage`  
5. виконайте `./LM-Studio-*.AppImage`  
> Порада: Після встановлення запустіть LM Studio один раз, щоб ініціалізувати CLI (`lms`).

<!-- @device:halo_box -->
Щоб дозволити LM Studio бачити попередньо встановлені моделі, перейдіть до Settings > General > Models Directory. Потім змініть шлях на `/var/cache/models`.

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