<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ComfyUI

<!-- @os:windows -->

1. Töltse le a legújabb Windows ComfyUI telepítőt a [download.comfy.org](https://download.comfy.org/windows/nsis/x64) oldalról.
2. Válassza ki a hardverkonfigurációt: Válassza az `AMD ROCm` lehetőséget.
3. Válassza ki, hova szeretné telepíteni a ComfyUI-t: Használja az alapértelmezett elérési utat, vagy a kívánt mappát.
4. Asztali alkalmazás beállításai: Javasoljuk, hogy vegye ki a pipát az "Automatic Updates" opcióból, hogy biztosan az alkalmazás ajánlott verzióját használja.
5. Nyomja meg a "Next" gombot a telepítés megkezdéséhez.

<!-- @os:end -->

<!-- @os:linux -->
#### ComfyUI klónozása
```bash
git clone https://github.com/Comfy-Org/ComfyUI.git
```

#### (Opcionális) Adott verzió checkoutolása
```bash
git checkout v0.19.2
```

#### ComfyUI követelmények telepítése

Az aktivált Python virtuális környezettel futtassa a következőt:
```bash
cd ComfyUI
pip install -r requirements.txt
```

> **Megjegyzés**: További információért lásd a [ComfyUI GitHub](https://github.com/comfy-org/ComfyUI) oldalát.

<!-- @os:end -->