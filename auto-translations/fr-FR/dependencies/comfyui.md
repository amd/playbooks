<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ComfyUI

<!-- @os:windows -->

1. Téléchargez la dernière version de l'installateur ComfyUI pour Windows sur [download.comfy.org](https://download.comfy.org/windows/nsis/x64).
2. Choisissez votre configuration matérielle : sélectionnez `AMD ROCm`.
3. Choisissez l'emplacement d'installation de ComfyUI : utilisez le chemin par défaut ou le dossier de votre choix.
4. Paramètres de l'application de bureau : nous vous recommandons de désélectionner « Mises à jour automatiques » afin de vous assurer que vous utilisez la version recommandée de cette application.
5. Appuyez sur « Suivant » pour démarrer l'installation.

<!-- @os:end -->

<!-- @os:linux -->
#### Cloner ComfyUI
```bash
git clone https://github.com/Comfy-Org/ComfyUI.git
```

#### (Facultatif) Extraire une version spécifique
```bash
git checkout v0.19.2
```

#### Installer les prérequis de ComfyUI

Une fois l'environnement virtuel Python activé, exécutez :
```bash
cd ComfyUI
pip install -r requirements.txt
```

> **Remarque** : Consultez [ComfyUI GitHub](https://github.com/comfy-org/ComfyUI) pour plus d'informations.

<!-- @os:end -->