<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ComfyUI

<!-- @os:windows -->

1. Scarica l'ultimo programma di installazione di ComfyUI per Windows da [download.comfy.org](https://download.comfy.org/windows/nsis/x64).
2. Scegli la tua configurazione hardware: Seleziona `AMD ROCm`.
3. Scegli dove installare ComfyUI: Usa il percorso predefinito o la cartella che preferisci.
4. Impostazioni dell'app Desktop: Consigliamo di deselezionare "Automatic Updates" per assicurarti di utilizzare la versione consigliata di questa app.
5. Premi "Next" per avviare l'installazione.

<!-- @os:end -->

<!-- @os:linux -->
#### Clona ComfyUI
```bash
git clone https://github.com/Comfy-Org/ComfyUI.git
```

#### (Facoltativo) Effettua il checkout di una versione specifica
```bash
git checkout v0.19.2
```

#### Installa i requisiti di ComfyUI

Con l'ambiente virtuale Python attivato, esegui:
```bash
cd ComfyUI
pip install -r requirements.txt
```

> **Nota**: Consulta [ComfyUI GitHub](https://github.com/comfy-org/ComfyUI) per ulteriori informazioni.

<!-- @os:end -->