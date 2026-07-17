<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ComfyUI

<!-- @os:windows -->

1. Ladda ner den senaste Windows ComfyUI-installationsfilen från [download.comfy.org](https://download.comfy.org/windows/nsis/x64).
2. Välj din hårdvarukonfiguration: Välj `AMD ROCm`.
3. Välj var du vill installera ComfyUI: Använd standardsökvägen eller din föredragna mapp.
4. Inställningar för skrivbordsappen: Vi rekommenderar att du avmarkerar "Automatic Updates" för att säkerställa att du använder den rekommenderade versionen av appen.
5. Tryck på "Next" för att påbörja installationen.

<!-- @os:end -->

<!-- @os:linux -->
#### Klona ComfyUI
```bash
git clone https://github.com/Comfy-Org/ComfyUI.git
```

#### (Valfritt) Checka ut en specifik version
```bash
git checkout v0.19.2
```

#### Installera ComfyUI-krav

Med den virtuella Python-miljön aktiverad, kör:
```bash
cd ComfyUI
pip install -r requirements.txt
```

> **Obs**: Se [ComfyUI GitHub](https://github.com/comfy-org/ComfyUI) för mer information.

<!-- @os:end -->