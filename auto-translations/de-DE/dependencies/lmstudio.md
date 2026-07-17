<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### LM Studio

<!-- @os:windows -->

<!-- @device:halo_box -->
LM Studio kann über das **AMD Ryzen™ AI Developer Center** installiert werden. Gehen Sie zur Registerkarte **Updates** und installieren Sie LM Studio, falls es noch nicht vorhanden ist.

Um LM Studio den Zugriff auf die vorinstallierten Modelle zu ermöglichen, navigieren Sie zu Einstellungen > Allgemein > Modellverzeichnis. Ändern Sie dann den Pfad zu `C:\Users\Public\models`

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_windows_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
1. Laden Sie das Installationsprogramm hier herunter: [https://lmstudio.ai/download](https://lmstudio.ai/download)
2. Installieren Sie es.
<!-- @device:end -->

> Tipp: Starten Sie LM Studio nach der Installation einmal, um die CLI (`lms`) zu initialisieren.

<!-- @test:id=lmstudio-cli-windows timeout=60 hidden=True -->
```powershell
lms --help
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
> Hinweis: Sie können entweder das .deb-Paket oder das AppImage installieren.
1. Laden Sie das AppImage hier herunter: [https://lmstudio.ai/download?os=linux](https://lmstudio.ai/download?os=linux)
2. Führen Sie `sudo apt install libfuse2` aus
3. Führen Sie `cd ~/Downloads` aus
4. Führen Sie `chmod +x LM-Studio-*.AppImage` aus
5. Führen Sie `./LM-Studio-*.AppImage` aus
> Tipp: Starten Sie LM Studio nach der Installation einmal, um die CLI (`lms`) zu initialisieren.

<!-- @device:halo_box -->
Um LM Studio den Zugriff auf die vorinstallierten Modelle zu ermöglichen, navigieren Sie zu Einstellungen > Allgemein > Modellverzeichnis. Ändern Sie dann den Pfad zu `/var/cache/models`.

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