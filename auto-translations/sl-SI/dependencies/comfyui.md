<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ComfyUI

<!-- @os:windows -->

1. Prenesite najnovejšo namestitveno datoteko ComfyUI za Windows s spletnega mesta [download.comfy.org](https://download.comfy.org/windows/nsis/x64).
2. Izberite svojo strojno konfiguracijo: izberite `AMD ROCm`.
3. Izberite mesto namestitve ComfyUI: uporabite privzeto pot ali mapo po vaši izbiri.
4. Nastavitve namizne aplikacije: priporočamo, da odznačite »Automatic Updates«, da zagotovite uporabo priporočene različice te aplikacije.
5. Pritisnite »Next«, da začnete namestitev.

<!-- @os:end -->

<!-- @os:linux -->
#### Kloniranje ComfyUI
```bash
git clone https://github.com/Comfy-Org/ComfyUI.git
```

#### (Neobvezno) Preklop na določeno različico
```bash
git checkout v0.19.2
```

#### Namestitev zahtev za ComfyUI

Ko je virtualno okolje Python aktivirano, zaženite:
```bash
cd ComfyUI
pip install -r requirements.txt
```

> **Opomba**: Za več informacij glejte [ComfyUI GitHub](https://github.com/comfy-org/ComfyUI).

<!-- @os:end -->