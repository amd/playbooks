<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### LM Studio

<!-- @os:windows -->

<!-- @device:halo_box -->
LM Studio se puede instalar desde el **AMD Ryzen™ AI Developer Center**. Ve a la pestaña **Updates** e instala LM Studio si aún no está presente.

Para permitir que LM Studio vea los modelos preinstalados, navega a Settings > General > Models Directory. Luego cambia la ruta a `C:\Users\Public\models`

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_windows_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
1. Descarga el instalador desde aquí: [https://lmstudio.ai/download](https://lmstudio.ai/download)
2. Instálalo.
<!-- @device:end -->

> Consejo: Después de instalar, inicia LM Studio una vez para inicializar la CLI (`lms`).

<!-- @test:id=lmstudio-cli-windows timeout=60 hidden=True -->
```powershell
lms --help
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
> Nota: Puedes elegir instalar el .deb o el AppImage.
1. Descarga el appimage desde aquí: [https://lmstudio.ai/download?os=linux](https://lmstudio.ai/download?os=linux)
2. ejecuta `sudo apt install libfuse2`  
3. ejecuta `cd ~/Downloads`  
4. ejecuta `chmod +x LM-Studio-*.AppImage`  
5. ejecuta `./LM-Studio-*.AppImage`  
> Consejo: Después de instalar, inicia LM Studio una vez para inicializar la CLI (`lms`).

<!-- @device:halo_box -->
Para permitir que LM Studio vea los modelos preinstalados, navega a Settings > General > Models Directory. Luego cambia la ruta a `/var/cache/models`.

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