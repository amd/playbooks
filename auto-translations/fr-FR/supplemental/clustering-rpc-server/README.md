<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traduction automatique.** Cette page a été traduite automatiquement depuis l'anglais et n'a pas été relue par un traducteur humain. Elle peut contenir des erreurs, et certaines instructions, commandes, téléchargements, disponibilités de produits ou autres contenus peuvent varier selon la langue ou la région. En cas d'incohérence ou de divergence, la version originale en anglais du playbook fait foi et prévaut.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Mise en cluster de deux Ryzen™ AI Halo avec RPC

## Présentation

Votre Ryzen™ AI Halo est déjà capable d'exécuter des grands modèles de langage en local. La mise en cluster va encore plus loin en combinant la mémoire GPU de plusieurs systèmes sur un réseau local, vous donnant accès à des modèles encore plus grands, dotés d'un raisonnement plus solide, d'une meilleure génération de code et d'une compréhension multilingue plus approfondie, le tout entièrement sur votre propre matériel.

Ce playbook vous apprend à mettre en cluster deux systèmes Ryzen AI Halo à l'aide du moteur RPC de llama.cpp et à exécuter GLM 4.7, un modèle de 358 milliards de paramètres, sur les deux machines avec l'accélération AMD ROCm™.

## Ce que vous allez apprendre

- Comment étendre l'allocation de VRAM sur les systèmes Ryzen AI Halo
- Installer llama.cpp avec la prise en charge de ROCm et RPC
- Configurer un worker RPC et lancer l'inférence distribuée sur deux nœuds
- Exécuter un modèle de 358 milliards de paramètres sur deux systèmes Ryzen AI Halo mis en réseau

## Configuration de la mémoire

> **Remarque** : Effectuez cette étape sur la machine 1 et la machine 2.

<!-- @os:windows -->
Sous Windows, pour exécuter des modèles plus volumineux nécessitant davantage de mémoire, nous devons utiliser l'allocation AMD Variable Graphics Memory (VRAM iGPU).

Cela peut être fait en ouvrant le panneau de configuration AMD Software: Adrenalin Edition et en accédant à : `Performance > Tuning > AMD Variable Graphics Memory`. Définissez la valeur sur **96 Go**. Veuillez redémarrer le système pour que les modifications prennent effet.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Sous Linux, ROCm utilise un pool de mémoire système partagé, et ce pool est configuré par défaut à la moitié de la mémoire système.

Cette quantité peut être augmentée en modifiant le paramètre de pages du Translation Table Manager (TTM) du noyau, à l'aide des instructions suivantes. AMD recommande de définir la VRAM dédiée minimale dans le BIOS (0,5 Go).

* Installez l'utilitaire pipx et ajoutez le chemin des wheels installés par pipx au chemin de recherche du système.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Installez le wheel amd-debug-tools depuis PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Exécutez l'outil amd-ttm pour interroger les paramètres actuels de la mémoire partagée.
  ```bash
  amd-ttm
  ```

* Reconfigurez les paramètres de mémoire partagée sur **120 Go** :
  ```bash
  amd-ttm --set 120
  ```

* Redémarrez le système pour que les modifications prennent effet.


<!-- @os:end -->
<!-- @device:halo_box -->
## Vérifier les mises à jour logicielles

<!-- @require:software-update -->
<!-- @device:end -->
## Prérequis

### Matériel

Ce playbook nécessite deux unités Ryzen AI Halo et un commutateur Ethernet, connectés en topologie en étoile, chaque unité étant reliée directement au commutateur.

| Composant | Quantité | Description |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Nœuds de calcul formant le cluster |
| Commutateur Ethernet 10 Gbps | 1 | Commutateur central permettant la communication multi-nœuds entre les unités Ryzen AI Halo (au moins 2 ports) |
| Câble Ethernet | 2 | Relie chaque unité Halo au commutateur (Cat 7 ou supérieur recommandé) |

> **Remarque** : Deux ports du commutateur Ethernet sont nécessaires pour connecter les deux unités Ryzen AI Halo. Un troisième port est nécessaire si vous accédez au modèle depuis une machine cliente distincte plutôt que depuis l'une des unités Halo.

### Logiciels
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Veuillez installer :
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) avec la charge de travail **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Configuration matérielle physique

> **Remarque** : Effectuez cette étape sur la machine 1 et la machine 2.

Connectez chaque unité Ryzen AI Halo au commutateur Ethernet à l'aide d'un câble Cat 7 (ou supérieur). Cela établit la liaison 10 Gbps utilisée pour la communication à haute vitesse entre les nœuds.
<!-- @os:linux -->
### 1. Déterminer les interfaces réseau

Sur chaque machine, trouvez le nom de son interface réseau et notez-le (il sera désigné ci-dessous par `IFNAME`). Exécutez :

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Cela affiche directement le nom de l'interface, par exemple :

```bash
enp191s0
```

### 2. Vérifier les vitesses de liaison réseau

Confirmez que la liaison est active et fonctionne à pleine vitesse en vérifiant la vitesse de votre interface :

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Remarque** : Remplacez `<IFNAME>` par le nom de l'interface de sortie obtenu à l'étape [1. Déterminer les interfaces réseau](#1-determine-network-interfaces)

Vous devriez voir une vitesse de `10000Mb/s` :

```bash
	Speed: 10000Mb/s
```

> **Remarque** : Si la vitesse est inférieure à `10000Mb/s` ou si la liaison ne s'établit pas, vérifiez le branchement du câble et confirmez que le port du commutateur est configuré sur 10 Gbps. Certains commutateurs nécessitent que la négociation automatique soit désactivée et que la vitesse de liaison soit définie manuellement ; consultez la documentation de votre commutateur.

<!-- @os:end -->

<!-- @os:windows -->
### Vérifier la vitesse de liaison réseau

Sur chaque machine, vérifiez la vitesse de liaison de vos interfaces réseau :

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Votre interface Ethernet doit être `Up` et fonctionner à `10 Gbps` :

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Remarque** : Si la vitesse est inférieure à `10 Gbps` ou si la liaison ne s'établit pas, vérifiez le branchement du câble et confirmez que le port du commutateur est configuré sur 10 Gbps. Certains commutateurs nécessitent que la négociation automatique soit désactivée et que la vitesse de liaison soit définie manuellement ; consultez la documentation de votre commutateur.

<!-- @os:end -->

## Installation de llama.cpp

> **Remarque** : Effectuez cette étape sur la machine 1 et la machine 2.

Deux options d'installation sont disponibles :

- [Option 1 : Lemonade SDK (recommandée)](#option-1-lemonade-sdk-recommended) - binaires précompilés, configuration la plus rapide
- [Option 2 : Compilation manuelle des sources](#option-2-manual-source-build) - compilation à partir des sources avec un contrôle total sur les indicateurs de compilation

### Option 1 : Lemonade SDK (recommandée)

Le Lemonade SDK fournit des builds nocturnes de llama.cpp avec l'accélération AMD ROCm 7, ciblant des GPU tels que gfx1151 (Strix Halo / Ryzen AI Max+ 395) et d'autres architectures Radeon récentes.

<!-- @os:windows -->
#### Étape 1 : Télécharger les binaires précompilés

Accédez à la page de la dernière version et téléchargez l'archive correspondant à votre plateforme et à votre cible GPU :

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Téléchargez le fichier nommé `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (où `xxxx` correspond au numéro de build).

#### Étape 2 : Extraire les binaires

Décompressez l'archive téléchargée :

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Ce répertoire contient désormais des builds compatibles ROCm de `llama-cli.exe`, `llama-server.exe` et `rpc-server.exe`, précompilés pour votre système Ryzen AI Halo.

#### Étape 3 : Vérifier la détection du GPU

```bash
.\llama-cli.exe --list-devices
```

Sortie attendue :

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```
<!-- @os:end -->

<!-- @os:linux -->
#### Étape 1 : Télécharger les binaires précompilés

Accédez à la page de la dernière version et téléchargez l'archive correspondant à votre plateforme et à votre cible GPU :

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Téléchargez le fichier nommé `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (où `xxxx` correspond au numéro de build).

#### Étape 2 : Extraire et préparer les binaires

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Ce répertoire contient désormais des builds compatibles ROCm de `llama-cli`, `llama-server` et `rpc-server`, précompilés pour votre système Ryzen AI Halo.

#### Étape 3 : Vérifier la détection du GPU

```bash
./llama-cli --list-devices
```

Sortie attendue :

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```
<!-- @os:end -->
Une fois llama.cpp préparé sur chaque nœud, passez à la section [Téléchargement du modèle](#downloading-the-model).

### Option 2 : Compilation manuelle à partir des sources

<!-- @os:windows -->
#### Étape 1 : Compiler llama.cpp

Ouvrez **x64 Native Tools Command Prompt** (installé avec Visual Studio Build Tools) et clonez le dépôt :

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Ajoutez HIP à votre PATH et compilez avec la prise en charge de ROCm et RPC :

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Indicateur de build | Objectif |
|-----------|---------|
| `-DGGML_HIP=ON` | Active la pile logicielle ROCm/HIP |
| `-DGGML_RPC=ON` | Active RPC pour l'inférence distribuée |
| `-DGPU_TARGETS=gfx1151` | Cible le GPU Ryzen AI Halo (Radeon 8060s) |
| `-G Ninja` | Utilise le système de build Ninja |

#### Étape 2 : Vérifier la détection du GPU

```cmd
cd rocm\bin
.\llama-cli.exe --list-devices
```

Sortie attendue :

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```

#### Étape 3 : Ajouter HIP à votre PATH utilisateur

L'étape de build ci-dessus a défini `%HIP_PATH%\bin` uniquement pour la session en cours. Pour rendre les bibliothèques HIP disponibles dans n'importe quel terminal (pas seulement dans x64 Native Tools Command Prompt), ajoutez-le de manière permanente à votre `PATH` utilisateur :

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Une fois llama.cpp préparé sur chaque nœud, passez à la section [Téléchargement du modèle](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Étape 1 : Compiler llama.cpp

Clonez le dépôt :

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Compilez avec la prise en charge de ROCm et RPC :

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DGGML_HIP_ROCWMMA_FATTN=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Indicateur de build | Objectif |
|-----------|---------|
| `-DGGML_HIP=ON` | Active la pile logicielle ROCm |
| `-DGGML_RPC=ON` | Active RPC pour l'inférence distribuée |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | Active rocWMMA pour une Flash Attention améliorée sur les GPU AMD |
| `-DAMDGPU_TARGETS="gfx1151"` | Cible le GPU Ryzen AI Halo (Radeon 8060s) |

Pour plus d'options de build, consultez la [documentation de build de llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Étape 2 : Vérifier la détection du GPU

```bash
cd rocm/bin
./llama-cli --list-devices
```

Sortie attendue :

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```

Une fois llama.cpp préparé sur chaque nœud, passez à la section [Téléchargement du modèle](#downloading-the-model).
<!-- @os:end -->

## Téléchargement du modèle

Ce guide utilise [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), un modèle de 358 milliards de paramètres dans la quantification `Q4_K_XL` proposée par [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). À cette quantification, le modèle nécessite environ 205 Go de stockage et tient dans la mémoire GPU combinée de deux nœuds Ryzen AI Halo.

Téléchargez les fichiers GGUF à l'aide du Hugging Face CLI :
<!-- @os:linux -->
```bash
pip install huggingface-hub
hf download unsloth/GLM-4.7-GGUF --include "UD-Q4_K_XL/*" --local-dir GLM-4.7-GGUF
```
<!-- @os:end -->

<!-- @os:windows -->
```cmd
python -m pip install -U huggingface-hub

$hfScripts = python -c "import sysconfig; print(sysconfig.get_path('scripts'))"
$env:Path = "$hfScripts;$env:Path"

hf download unsloth/GLM-4.7-GGUF --include "UD-Q4_K_XL/*" --local-dir GLM-4.7-GGUF
```
<!-- @os:end -->

> **Remarque** : le téléchargement du modèle doit être effectué sur la Machine 1 (le contrôleur). Les nœuds workers RPC n'ont pas besoin d'une copie locale des fichiers du modèle.

## Lancement du modèle sur le cluster

Le moteur RPC (Remote Procedure Call) de llama.cpp permet à une seule instance de llama.cpp de décharger des couches du modèle vers des workers distants via le réseau. Une machine agit en tant que **contrôleur** (Machine 1), gérant la tokenisation, la planification et l'orchestration. L'autre machine exécute un **serveur RPC** léger (Machine 2) qui expose sa mémoire GPU et sa puissance de calcul au contrôleur.

Au moment du chargement, llama.cpp répartit le modèle entre les deux nœuds. Une fois chargé, l'inférence se déroule comme si elle s'exécutait sur un seul accélérateur. RPC gère les transferts de tenseurs et la synchronisation en coulisses.

### Étape 1 : Démarrer le serveur RPC (Machine 2)

Sur la Machine 2, démarrez le serveur RPC pour exposer ses ressources GPU au contrôleur :
<!-- @os:linux -->
```bash
./ggml-rpc-server -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
.\ggml-rpc-server.exe -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

| Indicateur | Objectif |
|------|---------|
| `-p` | Port sur lequel diffuser le serveur RPC |
| `-c` | Active un cache local pour les grands tenseurs, évitant des transferts réseau répétés pendant le chargement du modèle |
| `--host` | Adresse IP à laquelle lier le serveur RPC (`0.0.0.0` pour toutes les interfaces) |

Pour plus d'options, consultez la [documentation RPC de llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Étape 2 : Lancer le modèle (Machine 1)

Une fois le serveur RPC exécuté sur la Machine 2, lancez l'inférence depuis la Machine 1 à l'aide de `llama-cli` ou `llama-server`.

#### llama-cli

`llama-cli` fournit une interface en ligne de commande pour interagir directement avec le modèle. Il est idéal pour le benchmarking, le débogage et l'expérimentation de bas niveau.

<!-- @os:linux -->
```bash
./llama-cli \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  --no-mmap \
  --rpc <RPC_WORKER_IP>:50053
```

> **Recherche de `<RPC_WORKER_IP>`** : sur la Machine 2, exécutez `hostname -I | awk '{print $1}'` pour trouver son adresse IP locale.
<!-- @os:end -->

<!-- @os:windows -->
> **Remarque** : exécutez cette commande dans Terminal (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --rpc <RPC_WORKER_IP>:50053
```

> **Recherche de `<RPC_WORKER_IP>`** : sur la Machine 2, exécutez `ipconfig | findstr /C:"IPv4"` dans Terminal (Powershell) pour trouver son adresse IP locale.

<!-- @os:end -->

Une fois en cours d'exécution, `llama-cli` affiche la progression du chargement du modèle et ouvre une invite interactive où vous pouvez discuter directement avec le modèle :

![llama-cli exécutant GLM 4.7 sur deux nœuds](assets/llama-cli-example.png)
#### llama-server

`llama-server` expose le même moteur d'inférence via un processus serveur persistant doté d'une interface web intégrée et d'une API HTTP compatible OpenAI. Il s'agit de l'interface privilégiée pour les déploiements de longue durée, l'accès multi-utilisateur et l'intégration avec des outils externes.

<!-- @os:linux -->
```bash
./llama-server \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  --no-mmap \
  --host 0.0.0.0 \
  --port 8081 \
  --rpc <RPC_WORKER_IP>:50053
```

> **Trouver `<RPC_WORKER_IP>`** : sur la Machine 2, exécutez `hostname -I | awk '{print $1}'` pour trouver son adresse IP locale.
<!-- @os:end -->

<!-- @os:windows -->
> **Remarque** : exécutez cette commande dans un Terminal (Powershell).

```powershell
.\llama-server.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --host 0.0.0.0 `
  --port 8081 `
  --rpc <RPC_WORKER_IP>:50053
```

> **Trouver `<RPC_WORKER_IP>`** : sur la Machine 2, exécutez `ipconfig | findstr /C:"IPv4"` dans un Terminal (Powershell) pour trouver son adresse IP locale.
<!-- @os:end -->

Une fois lancé, ouvrez `http://<HOST_IP>:8081` dans votre navigateur pour accéder à l'interface web intégrée. Celle-ci propose une interface de discussion basée sur le navigateur pour interagir avec le modèle :

![Interface web de llama-server exécutant GLM 4.7 sur deux nœuds](assets/llama-server-example.png)

<!-- @os:linux -->
> **Trouver `<HOST_IP>`** : sur la Machine 1, exécutez `hostname -I | awk '{print $1}'` pour trouver son adresse IP locale.
<!-- @os:end -->

<!-- @os:windows -->
> **Trouver `<HOST_IP>`** : sur la Machine 1, exécutez `ipconfig | findstr /C:"IPv4"` dans un Terminal (Powershell) pour trouver son adresse IP locale.
<!-- @os:end -->

#### Référence des paramètres

| Indicateur | Objectif |
|------|---------|
| `-m` | Chemin d'accès au fichier de modèle GGUF (utilisez le premier fragment, `00001-of-00005`) |
| `-c` | Taille du contexte en tokens. Des valeurs plus élevées utilisent davantage de mémoire |
| `-fa on` | Active Flash Attention rocWMMA pour de meilleures performances sur les GPU AMD |
| `-ngl 999` | Décharge toutes les couches du modèle vers le GPU |
| `--no-mmap` | Désactive la mise en correspondance mémoire (memory-mapping), réduisant les temps de chargement lorsque la taille du modèle dépasse la RAM système mais tient dans la VRAM |
| `--host` | IP à laquelle lier `llama-server` (`llama-server` uniquement) |
| `--port` | Port sur lequel servir l'API HTTP (`llama-server` uniquement) |
| `--rpc` | Liste des points de terminaison des workers RPC séparés par des virgules (`IP:port`) |

Pour l'usage complet des paramètres, consultez la [documentation llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) et la [documentation llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Étapes suivantes

- **Connecter des applications tierces** : `llama-server` expose une API compatible OpenAI. Pointez toute application compatible OpenAI (comme Open WebUI) vers `http://<HOST_IP>:8081` avec n'importe quelle clé API fictive (par exemple, `none`) pour vous connecter à votre cluster
- **Explorer d'autres modèles** : parcourez les GGUF quantifiés sur [Hugging Face](https://huggingface.co/models?search=gguf) pour trouver des modèles qui tiennent dans la mémoire GPU combinée de votre cluster
- **Passer à quatre nœuds** : ajoutez deux systèmes Ryzen AI Halo supplémentaires comme workers RPC additionnels pour accéder à des modèles à l'échelle du billion de paramètres. Transmettez des points de terminaison supplémentaires à `--rpc` sous forme de liste séparée par des virgules (par exemple, `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)