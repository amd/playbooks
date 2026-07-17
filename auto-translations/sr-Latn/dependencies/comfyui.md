<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ComfyUI

<!-- @os:windows -->

1. Preuzmite najnoviji Windows ComfyUI instalater sa [download.comfy.org](https://download.comfy.org/windows/nsis/x64).
2. Odaberite konfiguraciju hardvera: Izaberite `AMD ROCm`.
3. Odaberite gde da instalirate ComfyUI: Koristite podrazumevanu putanju ili željenu fasciklu.
4. Podešavanja aplikacije za radnu površinu: Preporučujemo da poništite izbor opcije "Automatic Updates" kako biste bili sigurni da koristite preporučenu verziju ove aplikacije.
5. Pritisnite "Next" da biste započeli instalaciju.

<!-- @os:end -->

<!-- @os:linux -->
#### Kloniranje ComfyUI
```bash
git clone https://github.com/Comfy-Org/ComfyUI.git
```

#### (Opciono) Prebacivanje na određenu verziju
```bash
git checkout v0.19.2
```

#### Instalacija zahteva za ComfyUI

Sa aktiviranim Python virtuelnim okruženjem, pokrenite:
```bash
cd ComfyUI
pip install -r requirements.txt
```

> **Napomena**: Pogledajte [ComfyUI GitHub](https://github.com/comfy-org/ComfyUI) za više informacija.

<!-- @os:end -->