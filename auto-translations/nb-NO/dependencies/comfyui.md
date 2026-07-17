<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ComfyUI

<!-- @os:windows -->

1. Last ned den nyeste Windows ComfyUI-installasjonsprogrammet fra [download.comfy.org](https://download.comfy.org/windows/nsis/x64).
2. Velg maskinvareoppsettet ditt: Velg `AMD ROCm`.
3. Velg hvor du vil installere ComfyUI: Bruk standardbanen eller din foretrukne mappe.
4. Innstillinger for skrivebordsapp: Vi anbefaler å fjerne avmerkingen for "Automatic Updates" for å sikre at du bruker den anbefalte versjonen av denne appen.
5. Trykk "Next" for å starte installasjonen.

<!-- @os:end -->

<!-- @os:linux -->
#### Klon ComfyUI
```bash
git clone https://github.com/Comfy-Org/ComfyUI.git
```

#### (Valgfritt) Sjekk ut en bestemt versjon
```bash
git checkout v0.19.2
```

#### Installer ComfyUI-krav

Med det virtuelle Python-miljøet aktivert, kjør:
```bash
cd ComfyUI
pip install -r requirements.txt
```

> **Merk**: Se [ComfyUI GitHub](https://github.com/comfy-org/ComfyUI) for mer informasjon.

<!-- @os:end -->