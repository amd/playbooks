<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### LM Studio

<!-- @os:windows -->

<!-- @device:halo_box -->
O LM Studio pode ser instalado a partir do **AMD Ryzen™ AI Developer Center**. Aceda ao separador **Updates** e instale o LM Studio caso ainda não esteja presente.

Se o seu sistema tiver modelos pré-instalados, navegue até Settings > General > Models Directory. Em seguida, altere o caminho para `C:\Users\Public\models`

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_windows_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
1. Transfira o instalador aqui: [https://lmstudio.ai/download](https://lmstudio.ai/download)
2. Instale. 
<!-- @device:end -->

> **Modelos:** Se o seu sistema tiver vindo com o modelo deste playbook pré-instalado, aponte o LM Studio para o diretório de modelos pré-instalados acima para o utilizar. Caso contrário, transfira o modelo a partir do separador **Discover** do LM Studio (ícone de pesquisa) antes de continuar.

> Dica: Após a instalação, inicie o LM Studio uma vez para inicializar a CLI (`lms`).

<!-- @test:id=lmstudio-cli-windows timeout=60 hidden=True -->
```powershell
lms --help
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
> Nota: Pode optar por instalar o .deb ou o AppImage. 
1. Transfira o appimage aqui: [https://lmstudio.ai/download?os=linux](https://lmstudio.ai/download?os=linux)
2. execute `sudo apt install libfuse2`  
3. execute `cd ~/Downloads`  
4. execute `chmod +x LM-Studio-*.AppImage`  
5. execute `./LM-Studio-*.AppImage`  
> Dica: Após a instalação, inicie o LM Studio uma vez para inicializar a CLI (`lms`).

<!-- @device:halo_box -->
Se o seu sistema tiver modelos pré-instalados, navegue até Settings > General > Models Directory. Em seguida, altere o caminho para `/var/cache/models`.

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_linux_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

> **Modelos:** Se o seu sistema tiver vindo com o modelo deste playbook pré-instalado, aponte o LM Studio para o diretório de modelos pré-instalados acima para o utilizar. Caso contrário, transfira o modelo a partir do separador **Discover** do LM Studio (ícone de pesquisa) antes de continuar.

<!-- @test:id=lmstudio-cli-linux timeout=60 hidden=True -->
```bash
lms --help
```
<!-- @test:end --> 
<!-- @os:end -->