<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ComfyUI

<!-- @os:windows -->

1. Download den nyeste Windows ComfyUI-installationsfil fra [download.comfy.org](https://download.comfy.org/windows/nsis/x64).
2. Vælg din hardwareopsætning: Vælg `AMD ROCm`.
3. Vælg, hvor ComfyUI skal installeres: Brug standardstien eller din foretrukne mappe.
4. Desktop App-indstillinger: Vi anbefaler, at du fravælger "Automatic Updates" for at sikre, at du bruger den anbefalede version af denne app.
5. Tryk på "Next" for at starte installationen.

<!-- @os:end -->

<!-- @os:linux -->
#### Klon ComfyUI
```bash
git clone https://github.com/Comfy-Org/ComfyUI.git
```

#### (Valgfrit) Vælg en bestemt version
```bash
git checkout v0.19.2
```

#### Installer ComfyUI-krav

Med det virtuelle Python-miljø aktiveret skal du køre:
```bash
cd ComfyUI
pip install -r requirements.txt
```

> **Bemærk**: Se [ComfyUI GitHub](https://github.com/comfy-org/ComfyUI) for mere information.

<!-- @os:end -->