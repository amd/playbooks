<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ComfyUI

<!-- @os:windows -->

1. Prenesite najnovejši Windows namestitveni program ComfyUI s [download.comfy.org](https://download.comfy.org/windows/nsis/x64).
2. Izberite konfiguracijo strojne opreme: Izberite `AMD ROCm`.
3. Izberite, kam namestiti ComfyUI: Uporabite privzeto pot ali svojo želeno mapo.
4. Nastavitve namizne aplikacije: Priporočamo, da odznačite »Samodejne posodobitve«, da zagotovite uporabo priporočene različice te aplikacije.
5. Pritisnite »Naprej«, da začnete namestitev.

<!-- @os:end -->

<!-- @os:linux -->
#### Klonirajte ComfyUI
```bash
git clone https://github.com/Comfy-Org/ComfyUI.git
```

#### (Neobvezno) Izberite določeno različico
```bash
git checkout v0.19.2
```

#### Namestite zahteve ComfyUI

Z aktiviranim virtualnim okoljem Python zaženite:
```bash
cd ComfyUI
pip install -r requirements.txt
```

> **Opomba**: Za več informacij glejte [ComfyUI GitHub](https://github.com/comfy-org/ComfyUI).

<!-- @os:end -->