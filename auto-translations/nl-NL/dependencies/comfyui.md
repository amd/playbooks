<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ComfyUI

<!-- @os:windows -->

1. Download de nieuwste ComfyUI-installer voor Windows van [download.comfy.org](https://download.comfy.org/windows/nsis/x64).
2. Kies uw hardwareconfiguratie: Selecteer `AMD ROCm`.
3. Kies waar u ComfyUI wilt installeren: Gebruik het standaardpad of uw gewenste map.
4. Instellingen voor de desktopapp: We raden aan om "Automatische updates" uit te schakelen, zodat u zeker weet dat u de aanbevolen versie van deze app gebruikt.
5. Klik op "Volgende" om de installatie te starten.

<!-- @os:end -->

<!-- @os:linux -->
#### Clone ComfyUI
```bash
git clone https://github.com/Comfy-Org/ComfyUI.git
```

#### (Optioneel) Een specifieke versie uitchecken
```bash
git checkout v0.19.2
```

#### Installeer de ComfyUI-vereisten

Voer het volgende uit met de geactiveerde Python-virtuele omgeving:
```bash
cd ComfyUI
pip install -r requirements.txt
```

> **Opmerking**: Zie [ComfyUI GitHub](https://github.com/comfy-org/ComfyUI) voor meer informatie.

<!-- @os:end -->