<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ComfyUI

<!-- @os:windows -->

1. Téléchargez le dernier installateur ComfyUI pour Windows depuis [download.comfy.org](https://download.comfy.org/windows/nsis/x64).
2. Choisissez votre configuration matérielle : Sélectionnez `AMD ROCm`.
3. Choisissez où installer ComfyUI : Utilisez le chemin par défaut ou votre dossier préféré.
4. Paramètres de l'application de bureau : Nous recommandons de décocher « Mises à jour automatiques » pour vous assurer d'utiliser la version recommandée de cette application.
5. Appuyez sur « Suivant » pour commencer l'installation.

<!-- @os:end -->

<!-- @os:linux -->
#### Cloner ComfyUI
```bash
git clone https://github.com/Comfy-Org/ComfyUI.git
```

#### (Optionnel) Basculer vers une version spécifique
```bash
git checkout v0.19.2
```

#### Installer les dépendances de ComfyUI

Avec l'environnement virtuel Python activé, exécutez :
```bash
cd ComfyUI
pip install -r requirements.txt
```

> **Remarque** : Consultez [ComfyUI GitHub](https://github.com/comfy-org/ComfyUI) pour plus d'informations.

<!-- @os:end -->