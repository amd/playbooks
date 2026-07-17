<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade

#### Installation de Lemonade

<!-- @os:windows -->
Téléchargez le dernier installateur depuis [lemonade-server.ai](https://github.com/lemonade-sdk/lemonade/releases/latest/download/lemonade.msi) et exécutez le fichier `.msi`.

Après l'installation :
- Le CLI `lemonade` est automatiquement ajouté au PATH de votre système
- Le serveur Lemonade est censé s'exécuter automatiquement en arrière-plan

Vous pouvez également effectuer une installation silencieuse depuis la ligne de commande :
```cmd
msiexec /i lemonade-server-minimal.msi /qn
```
<!-- @os:end -->

<!-- @os:linux -->
**Ubuntu :**
```bash
sudo add-apt-repository ppa:lemonade-team/stable
sudo apt install lemonade-server
```

**Arch Linux (AUR) :**
```bash
yay -S lemonade-server
```

Pour les autres distributions ou pour installer depuis les sources, consultez les [options d'installation complètes](https://lemonade-server.ai/docs/guide/install/).
<!-- @os:end -->


#### Vérification de l'installation de Lemonade

Ouvrez un terminal et exécutez :
```bash
lemonade --version
```

Vous devriez voir une sortie similaire à :
```
lemonade version x.y.z
```

Si vous voyez un numéro de version, Lemonade est correctement installé et prêt à l'emploi.

Pour référence rapide, voici les commandes CLI Lemonade courantes :

| Commande | Ce qu'elle fait |
| --- | --- |
| `lemonade --help` | Affiche toutes les commandes et options disponibles. |
| `lemonade --version` | Affiche la version de Lemonade installée. |
| `lemonade status` | Confirme si le serveur Lemonade est en cours d'exécution et accessible. L'URL de base de l'API compatible OpenAI par défaut est `http://localhost:13305/api/v1`. |
| `lemonade list` | Liste les modèles disponibles pour votre configuration Lemonade. |
| `lemonade pull <MODEL_NAME>` | Télécharge un modèle sans le lancer. |
| `lemonade run <MODEL_NAME>` | Télécharge le modèle si nécessaire, puis le démarre pour l'inférence/le chat. |
| `lemonade run <MODEL_NAME> --llamacpp rocm` | Démarre un modèle llama.cpp avec le backend ROCm. |
| `lemonade run <MODEL_NAME> --llamacpp vulkan` | Démarre un modèle llama.cpp avec le backend Vulkan. |
| `lemonade config` | Affiche les valeurs de configuration actuelles de Lemonade. |
| `lemonade config set llamacpp.backend=rocm` | Définit le backend llama.cpp par défaut sur ROCm. |

Pour les dernières options du serveur Lemonade ou pour le dépannage, veuillez consulter la [documentation officielle de Lemonade](https://lemonade-server.ai/docs/lemonade-cli/).