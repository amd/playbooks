<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ComfyUI

<!-- @os:windows -->

1. Preuzmite najnoviju Windows ComfyUI instalaciju sa [download.comfy.org](https://download.comfy.org/windows/nsis/x64).
2. Izaberite vašu hardversku konfiguraciju: Izaberite `AMD ROCm`.
3. Izaberite gde želite da instalirate ComfyUI: Koristite podrazumevanu putanju ili željeni folder.
4. Podešavanja desktop aplikacije: Preporučujemo da isključite opciju "Automatic Updates" kako biste bili sigurni da koristite preporučenu verziju ove aplikacije.
5. Pritisnite "Next" da biste započeli instalaciju.

<!-- @os:end -->

<!-- @os:linux -->
#### Kloniranje ComfyUI
```bash
git clone https://github.com/Comfy-Org/ComfyUI.git
```

#### (Opciono) Preuzimanje određene verzije
```bash
git checkout v0.19.2
```

#### Instaliranje ComfyUI zahteva

Sa aktiviranim Python virtuelnim okruženjem, pokrenite:
```bash
cd ComfyUI
pip install -r requirements.txt
```

> **Napomena**: Pogledajte [ComfyUI GitHub](https://github.com/comfy-org/ComfyUI) za više informacija.

<!-- @os:end -->