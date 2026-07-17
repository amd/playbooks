<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ComfyUI

<!-- @os:windows -->

1. Töltse le a legújabb Windows ComfyUI telepítőt a [download.comfy.org](https://download.comfy.org/windows/nsis/x64) oldalról.
2. Válassza ki a hardverkonfigurációját: Válassza az `AMD ROCm` lehetőséget.
3. Válassza ki, hova telepítse a ComfyUI-t: Használja az alapértelmezett elérési utat vagy a kívánt mappát.
4. Asztali alkalmazás beállításai: Javasoljuk, hogy törölje a jelölést az „Automatikus frissítések" lehetőségnél, hogy biztosan az alkalmazás ajánlott verzióját használja.
5. Kattintson a „Tovább" gombra a telepítés megkezdéséhez.

<!-- @os:end -->

<!-- @os:linux -->
#### A ComfyUI klónozása
```bash
git clone https://github.com/Comfy-Org/ComfyUI.git
```

#### (Opcionális) Egy adott verzió kiválasztása
```bash
git checkout v0.19.2
```

#### A ComfyUI követelményeinek telepítése

Az aktivált Python virtuális környezettel futtassa a következőt:
```bash
cd ComfyUI
pip install -r requirements.txt
```

> **Megjegyzés**: További információért lásd a [ComfyUI GitHub](https://github.com/comfy-org/ComfyUI) oldalt.

<!-- @os:end -->