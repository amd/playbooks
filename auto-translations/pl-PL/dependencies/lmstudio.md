<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### LM Studio

<!-- @os:windows -->

<!-- @device:halo_box -->
LM Studio można zainstalować z **AMD Ryzen™ AI Developer Center**. Przejdź do zakładki **Updates** i zainstaluj LM Studio, jeśli nie jest jeszcze zainstalowane.

Aby LM Studio mogło wykrywać wstępnie zainstalowane modele, przejdź do Settings > General > Models Directory. Następnie zmień ścieżkę na `C:\Users\Public\models`

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_windows_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
1. Pobierz instalator stąd: [https://lmstudio.ai/download](https://lmstudio.ai/download)
2. Zainstaluj.
<!-- @device:end -->

> Wskazówka: Po zainstalowaniu uruchom LM Studio raz, aby zainicjować CLI (`lms`).

<!-- @test:id=lmstudio-cli-windows timeout=60 hidden=True -->
```powershell
lms --help
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
> Uwaga: Możesz wybrać instalację pliku .deb lub AppImage.
1. Pobierz plik AppImage stąd: [https://lmstudio.ai/download?os=linux](https://lmstudio.ai/download?os=linux)
2. Uruchom `sudo apt install libfuse2`
3. Uruchom `cd ~/Downloads`
4. Uruchom `chmod +x LM-Studio-*.AppImage`
5. Uruchom `./LM-Studio-*.AppImage`
> Wskazówka: Po zainstalowaniu uruchom LM Studio raz, aby zainicjować CLI (`lms`).

<!-- @device:halo_box -->
Aby LM Studio mogło wykrywać wstępnie zainstalowane modele, przejdź do Settings > General > Models Directory. Następnie zmień ścieżkę na `/var/cache/models`.

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