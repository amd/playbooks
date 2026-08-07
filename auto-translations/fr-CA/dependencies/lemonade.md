<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade

#### Installation de Lemonade

<!-- @os:windows -->
Téléchargez le dernier programme d'installation depuis [lemonade-server.ai](https://github.com/lemonade-sdk/lemonade/releases/latest/download/lemonade.msi) et exécutez le fichier `.msi`. 

Une fois l'installation terminée :
- Le CLI `lemonade` est ajouté automatiquement à votre PATH système
- Le serveur Lemonade devrait démarrer automatiquement en arrière-plan

Vous pouvez également effectuer une installation silencieuse à partir de la ligne de commande :
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

Pour d'autres distributions ou pour installer à partir des sources, consultez les [options d'installation complètes](https://lemonade-server.ai/docs/guide/install/).
<!-- @os:end -->


#### Vérification de l'installation de Lemonade

Ouvrez un terminal et exécutez :
```bash
lemonade --version
```

Vous devriez voir une sortie semblable à :
```
lemonade version x.y.z
```

Si un numéro de version s'affiche, Lemonade est correctement installé et prêt à l'emploi.

Pour référence rapide, voici les commandes CLI Lemonade courantes :

| Commande | Ce qu'elle fait |
| --- | --- |
| `lemonade --help` | Affiche toutes les commandes et options disponibles. |
| `lemonade --version` | Affiche la version de Lemonade installée. |
| `lemonade status` | Confirme si le serveur Lemonade est en cours d'exécution et accessible. L'URL de base par défaut de l'API compatible OpenAI est `http://localhost:13305/api/v1`. |
| `lemonade list` | Répertorie les modèles disponibles pour votre configuration Lemonade. |
| `lemonade pull <MODEL_NAME>` | Télécharge un modèle sans le lancer. |
| `lemonade run <MODEL_NAME>` | Télécharge le modèle si nécessaire, puis le démarre pour l'inférence/le clavardage. |
| `lemonade run <MODEL_NAME> --llamacpp rocm` | Démarre un modèle llama.cpp avec le moteur d'exécution ROCm. |
| `lemonade run <MODEL_NAME> --llamacpp vulkan` | Démarre un modèle llama.cpp avec le moteur d'exécution Vulkan. |
| `lemonade config` | Affiche les valeurs de configuration actuelles de Lemonade. |
| `lemonade config set llamacpp.backend=rocm` | Définit le moteur d'exécution llama.cpp par défaut sur ROCm. |

Pour connaître les dernières options du serveur Lemonade ou pour le dépannage, veuillez consulter la [documentation officielle de Lemonade](https://lemonade-server.ai/docs/lemonade-cli/).