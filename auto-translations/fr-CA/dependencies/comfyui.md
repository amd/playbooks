<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ComfyUI

<!-- @os:windows -->

1. Téléchargez la dernière version de l'installateur ComfyUI pour Windows à partir de [download.comfy.org](https://download.comfy.org/windows/nsis/x64).
2. Choisissez votre configuration matérielle : sélectionnez `AMD ROCm`.
3. Choisissez où installer ComfyUI : utilisez le chemin par défaut ou le dossier de votre choix.
4. Paramètres de l'application de bureau : nous vous recommandons de désélectionner « Mises à jour automatiques » afin de vous assurer que vous utilisez la version recommandée de cette application.
5. Appuyez sur « Suivant » pour commencer l'installation.

<!-- @os:end -->

<!-- @os:linux -->
#### Cloner ComfyUI
```bash
git clone https://github.com/Comfy-Org/ComfyUI.git
```

#### (Facultatif) Extraire une version précise
```bash
git checkout v0.19.2
```

#### Installer les prérequis de ComfyUI

Une fois l'environnement virtuel Python activé, exécutez :
```bash
cd ComfyUI
pip install -r requirements.txt
```

> **Remarque** : Consultez [ComfyUI GitHub](https://github.com/comfy-org/ComfyUI) pour en savoir plus.

<!-- @os:end -->