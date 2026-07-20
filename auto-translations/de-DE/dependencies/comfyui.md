<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ComfyUI

<!-- @os:windows -->

1. Laden Sie das neueste ComfyUI-Installationsprogramm für Windows von [download.comfy.org](https://download.comfy.org/windows/nsis/x64) herunter.
2. Wählen Sie Ihre Hardwarekonfiguration: Wählen Sie `AMD ROCm`.
3. Wählen Sie den Installationsort für ComfyUI: Verwenden Sie den Standardpfad oder einen bevorzugten Ordner.
4. Desktop-App-Einstellungen: Wir empfehlen, die Option „Automatic Updates“ zu deaktivieren, um sicherzustellen, dass Sie die empfohlene Version dieser App verwenden.
5. Klicken Sie auf „Next“, um die Installation zu starten.

<!-- @os:end -->

<!-- @os:linux -->
#### ComfyUI klonen
```bash
git clone https://github.com/Comfy-Org/ComfyUI.git
```

#### (Optional) Eine bestimmte Version auschecken
```bash
git checkout v0.19.2
```

#### ComfyUI-Voraussetzungen installieren

Führen Sie bei aktivierter Python-Virtual-Environment Folgendes aus:
```bash
cd ComfyUI
pip install -r requirements.txt
```

> **Hinweis**: Weitere Informationen finden Sie unter [ComfyUI GitHub](https://github.com/comfy-org/ComfyUI).

<!-- @os:end -->