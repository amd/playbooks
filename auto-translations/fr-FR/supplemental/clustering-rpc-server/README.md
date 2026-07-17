<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Regroupement de deux Ryzen™ AI Halo avec RPC

## Vue d'ensemble

Votre Ryzen™ AI Halo est déjà capable d'exécuter de grands modèles de langage en local. Le regroupement va plus loin en combinant la mémoire GPU de plusieurs systèmes sur un réseau local, vous donnant accès à des modèles encore plus grands avec un raisonnement plus puissant, une meilleure génération de code et une compréhension multilingue plus approfondie, le tout entièrement sur votre propre matériel.

Ce playbook vous apprend à regrouper deux systèmes Ryzen AI Halo en utilisant le moteur RPC de llama.cpp et à exécuter GLM 4.7, un modèle à 358 milliards de paramètres, sur les deux machines avec l'accélération AMD ROCm™.

## Ce que vous apprendrez

- Comment étendre l'allocation VRAM sur les systèmes Ryzen AI Halo
- Installer llama.cpp avec la prise en charge de ROCm et RPC
- Configurer un worker RPC et lancer l'inférence distribuée sur deux nœuds
- Exécuter un modèle à 358 milliards de paramètres sur deux systèmes Ryzen AI Halo en réseau

## Configuration de la mémoire

> **Remarque** : Effectuez cette étape sur la Machine 1 et la Machine 2.

<!-- @os:windows -->
Sous Windows, pour exécuter des modèles plus grands nécessitant davantage de mémoire, nous devons utiliser l'allocation AMD Variable Graphics Memory (iGPU VRAM).

Pour ce faire, ouvrez le panneau de contrôle AMD Software: Adrenalin Edition et naviguez vers : `Performance > Tuning > AMD Variable Graphics Memory`. Définissez la valeur sur **96 Go**. Veuillez redémarrer le système pour que les modifications prennent effet.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Sous Linux, ROCm utilise un pool de mémoire système partagée, et ce pool est configuré par défaut à la moitié de la mémoire système.

Cette quantité peut être augmentée en modifiant le paramètre de page du Translation Table Manager (TTM) du noyau, en suivant les instructions ci-dessous. AMD recommande de définir la VRAM dédiée minimale dans le BIOS (0,5 Go).

* Installez l'utilitaire pipx et ajoutez le chemin des wheels installées par pipx dans le chemin de recherche système.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Installez la wheel amd-debug-tools depuis PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Exécutez l'outil amd-ttm pour interroger les paramètres actuels de la mémoire partagée.
  ```bash
  amd-ttm
  ```

* Reconfigurez les paramètres de mémoire partagée à **120 Go** :
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

Ce playbook nécessite deux unités Ryzen AI Halo et un commutateur Ethernet, connectés en topologie étoile avec chaque unité câblée directement au commutateur.

| Composant | Quantité | Description |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Nœuds de calcul formant le cluster |
| Commutateur Ethernet 10 Gbps | 1 | Commutateur central permettant la communication multi-nœuds Ryzen AI Halo (au moins 2 ports) |
| Câble Ethernet | 2 | Connecte chaque unité Halo au commutateur (Cat 7 ou supérieur recommandé) |

> **Remarque** : Deux ports du commutateur Ethernet sont nécessaires pour connecter les deux unités Ryzen AI Halo. Un troisième port est requis si vous accédez au modèle depuis une machine cliente distincte plutôt que depuis l'une des unités Halo.

### Logiciels
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Veuillez installer :
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) avec la charge de travail **Développement Desktop en C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Configuration physique du matériel

> **Remarque** : Effectuez cette étape sur la Machine 1 et la Machine 2.

Connectez chaque unité Ryzen AI Halo au commutateur Ethernet à l'aide d'un câble Cat 7 (ou supérieur). Cela établit la liaison 10 Gbps utilisée pour la communication haute vitesse entre les nœuds.
<!-- @os:linux -->
### 1. Identifier les interfaces réseau

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

> **Remarque** : Remplacez `<IFNAME>` par le nom de l'interface obtenu à l'étape [1. Identifier les interfaces réseau](#1-determine-network-interfaces)

Vous devriez voir une vitesse de `10000Mb/s` :

```bash
	Speed: 10000Mb/s
```

> **Remarque** : Si la vitesse est inférieure à `10000Mb/s` ou si la liaison ne s'établit pas, vérifiez la connexion du câble et confirmez que le port du commutateur est configuré à 10 Gbps. Certains commutateurs nécessitent de désactiver la négociation automatique et de définir la vitesse de liaison manuellement ; consultez la documentation de votre commutateur.

<!-- @os:end -->

<!-- @os:windows -->
### Vérifier la vitesse de liaison réseau

Sur chaque machine, vérifiez la vitesse de liaison de vos interfaces réseau :

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Votre interface Ethernet devrait être `Up` et fonctionner à `10 Gbps` :

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Remarque** : Si la vitesse est inférieure à `10 Gbps` ou si la liaison ne s'établit pas, vérifiez la connexion du câble et confirmez que le port du commutateur est configuré à 10 Gbps. Certains commutateurs nécessitent de désactiver la négociation automatique et de définir la vitesse de liaison manuellement ; consultez la documentation de votre commutateur.

<!-- @os:end -->

## Installation de llama.cpp

> **Remarque** : Effectuez cette étape sur la Machine 1 et la Machine 2.

Deux options d'installation sont disponibles :

- [Option 1 : Lemonade SDK (Recommandé)](#option-1-lemonade-sdk-recommended) - binaires pré-compilés, configuration la plus rapide
- [Option 2 : Compilation manuelle depuis les sources](#option-2-manual-source-build) - compilation depuis les sources avec un contrôle total sur les options de compilation

### Option 1 : Lemonade SDK (Recommandé)

Le Lemonade SDK fournit des builds nocturnes de llama.cpp avec l'accélération AMD ROCm 7, ciblant des GPU tels que gfx1151 (Strix Halo / Ryzen AI Max+ 395) et d'autres architectures Radeon récentes.

<!-- @os:windows -->
#### Étape 1 : Télécharger les binaires pré-compilés

Accédez à la page de la dernière version et téléchargez l'archive correspondant à votre plateforme et à votre cible GPU :

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Téléchargez le fichier nommé `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (où `xxxx` est le numéro de build).

#### Étape 2 : Extraire les binaires

Décompressez l'archive téléchargée :

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Ce répertoire contient désormais des builds de `llama-cli.exe`, `llama-server.exe` et `rpc-server.exe` avec ROCm activé, précompilés pour votre système Ryzen AI Halo.

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
#### Étape 1 : Télécharger les binaires pré-compilés

Accédez à la page de la dernière version et téléchargez l'archive correspondant à votre plateforme et à votre cible GPU :

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Téléchargez le fichier nommé `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (où `xxxx` est le numéro de build).

#### Étape 2 : Extraire et préparer les binaires

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Ce répertoire contient désormais des builds de `llama-cli`, `llama-server` et `rpc-server` avec ROCm activé, précompilés pour votre système Ryzen AI Halo.

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
Avec llama.cpp préparé sur chaque nœud, passez à [Téléchargement du modèle](#downloading-the-model).

### Option 2 : Compilation manuelle depuis les sources

<!-- @os:windows -->
#### Étape 1 : Compiler llama.cpp

Ouvrez l'**Invite de commandes des outils natifs x64** (installée avec Visual Studio Build Tools) et clonez le dépôt :

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Ajoutez HIP à votre chemin et compilez avec la prise en charge de ROCm et RPC :

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Option de compilation | Objectif |
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

#### Étape 3 : Ajouter HIP à votre chemin utilisateur

L'étape de compilation ci-dessus a défini `%HIP_PATH%\bin` uniquement pour la session en cours. Pour rendre les bibliothèques HIP disponibles dans n'importe quel terminal (pas seulement l'Invite de commandes des outils natifs x64), ajoutez-le définitivement à votre `PATH` utilisateur :

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Avec llama.cpp préparé sur chaque nœud, passez à [Téléchargement du modèle](#downloading-the-model).
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

| Option de compilation | Objectif |
|-----------|---------|
| `-DGGML_HIP=ON` | Active la pile logicielle ROCm |
| `-DGGML_RPC=ON` | Active RPC pour l'inférence distribuée |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | Active rocWMMA pour une Flash Attention améliorée sur les GPU AMD |
| `-DAMDGPU_TARGETS="gfx1151"` | Cible le GPU Ryzen AI Halo (Radeon 8060s) |

Pour plus d'options de compilation, consultez la [documentation de compilation de llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

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

Avec llama.cpp préparé sur chaque nœud, passez à [Téléchargement du modèle](#downloading-the-model).
<!-- @os:end -->

## Téléchargement du modèle

Ce playbook utilise [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), un modèle à 358 milliards de paramètres en quantification `Q4_K_XL` provenant de [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). À cette quantification, le modèle nécessite environ 205 Go de stockage et tient dans la mémoire GPU combinée de deux nœuds Ryzen AI Halo.

Téléchargez les fichiers GGUF à l'aide de la CLI Hugging Face :
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

> **Remarque** : Le téléchargement du modèle doit être effectué sur la Machine 1 (le contrôleur). Les nœuds workers RPC n'ont pas besoin d'une copie locale des fichiers du modèle.

## Lancement du modèle sur le cluster

Le moteur RPC (Remote Procedure Call) de llama.cpp permet à une seule instance de llama.cpp de décharger des couches du modèle vers des workers distants via le réseau. Une machine agit comme **contrôleur** (Machine 1), gérant la tokenisation, la planification et l'orchestration. L'autre machine exécute un **serveur RPC** léger (Machine 2) qui expose sa mémoire GPU et sa puissance de calcul au contrôleur.

Au chargement, llama.cpp fragmente le modèle sur les deux nœuds. Une fois chargé, l'inférence se déroule comme si elle s'exécutait sur un seul accélérateur. RPC gère les transferts de tenseurs et la synchronisation en arrière-plan.

### Étape 1 : Démarrer le serveur RPC (Machine 2)

Sur la Machine 2, démarrez le serveur RPC pour exposer ses ressources GPU au contrôleur :
<!-- @os:linux -->
```bash
./rpc-server -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
.\rpc-server.exe -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

| Option | Objectif |
|------|---------|
| `-p` | Port sur lequel diffuser le serveur RPC |
| `-c` | Active un cache local pour les grands tenseurs, évitant les transferts réseau répétés lors du chargement du modèle |
| `--host` | Adresse IP à laquelle lier le serveur RPC (`0.0.0.0` pour toutes les interfaces) |

Pour plus d'options, consultez la [documentation RPC de llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Étape 2 : Lancer le modèle (Machine 1)

Avec le serveur RPC en cours d'exécution sur la Machine 2, lancez l'inférence depuis la Machine 1 en utilisant soit `llama-cli` soit `llama-server`.

#### llama-cli

`llama-cli` fournit une interface en ligne de commande pour interagir directement avec le modèle. Il est idéal pour les benchmarks, le débogage et l'expérimentation de bas niveau.

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

> **Trouver `<RPC_WORKER_IP>`** : Sur la Machine 2, exécutez `hostname -I | awk '{print $1}'` pour trouver son adresse IP locale.
<!-- @os:end -->

<!-- @os:windows -->
> **Remarque** : Exécutez cette commande dans Terminal (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --rpc <RPC_WORKER_IP>:50053
```

> **Trouver `<RPC_WORKER_IP>`** : Sur la Machine 2, exécutez `ipconfig | findstr /C:"IPv4"` dans Terminal (Powershell) pour trouver son adresse IP locale.

<!-- @os:end -->

Une fois en cours d'exécution, `llama-cli` affiche la progression du chargement du modèle et entre dans une invite interactive où vous pouvez discuter directement avec le modèle :

![llama-cli exécutant GLM 4.7 sur deux nœuds](assets/llama-cli-example.png)

#### llama-server

`llama-server` expose le même moteur d'inférence via un processus serveur persistant avec une interface web intégrée et une API HTTP compatible OpenAI. Il s'agit de l'interface privilégiée pour les déploiements de longue durée, l'accès multi-utilisateurs et l'intégration avec des outils externes.

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

> **Trouver `<RPC_WORKER_IP>`** : Sur la Machine 2, exécutez `hostname -I | awk '{print $1}'` pour trouver son adresse IP locale.
<!-- @os:end -->

<!-- @os:windows -->
> **Remarque** : Exécutez cette commande dans Terminal (Powershell).

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

> **Trouver `<RPC_WORKER_IP>`** : Sur la Machine 2, exécutez `ipconfig | findstr /C:"IPv4"` dans Terminal (Powershell) pour trouver son adresse IP locale.
<!-- @os:end -->

Une fois démarré, ouvrez `http://<HOST_IP>:8081` dans votre navigateur pour accéder à l'interface web intégrée. Celle-ci fournit une interface de chat basée sur le navigateur pour interagir avec le modèle :

![Interface web llama-server exécutant GLM 4.7 sur deux nœuds](assets/llama-server-example.png)

<!-- @os:linux -->
> **Trouver `<HOST_IP>`** : Sur la Machine 1, exécutez `hostname -I | awk '{print $1}'` pour trouver son adresse IP locale.
<!-- @os:end -->

<!-- @os:windows -->
> **Trouver `<HOST_IP>`** : Sur la Machine 1, exécutez `ipconfig | findstr /C:"IPv4"` dans Terminal (Powershell) pour trouver son adresse IP locale.
<!-- @os:end -->

#### Référence des paramètres

| Option | Objectif |
|------|---------|
| `-m` | Chemin vers le fichier de modèle GGUF (utilisez le premier fragment, `00001-of-00005`) |
| `-c` | Taille du contexte en tokens. Des valeurs plus élevées utilisent plus de mémoire |
| `-fa on` | Active la Flash Attention rocWMMA pour de meilleures performances sur les GPU AMD |
| `-ngl 999` | Décharge toutes les couches du modèle vers le GPU |
| `--no-mmap` | Désactive le memory-mapping, réduisant les temps de chargement lorsque la taille du modèle dépasse la RAM système mais tient dans la VRAM |
| `--host` | IP à laquelle lier `llama-server` (uniquement pour `llama-server`) |
| `--port` | Port sur lequel servir l'API HTTP (uniquement pour `llama-server`) |
| `--rpc` | Liste séparée par des virgules des points de terminaison des workers RPC (`IP:port`) |

Pour l'utilisation complète des paramètres, consultez la [documentation de llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) et la [documentation de llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Étapes suivantes

- **Connecter des applications tierces** : `llama-server` expose une API compatible OpenAI. Pointez n'importe quelle application compatible OpenAI (telle que Open WebUI) vers `http://<HOST_IP>:8081` avec une clé API fictive (par exemple, `none`) pour vous connecter à votre cluster
- **Explorer d'autres modèles** : Parcourez les GGUF quantifiés sur [Hugging Face](https://huggingface.co/models?search=gguf) pour trouver des modèles qui tiennent dans la mémoire GPU combinée de votre cluster
- **Passer à quatre nœuds** : Ajoutez deux autres systèmes Ryzen AI Halo comme workers RPC supplémentaires pour accéder à des modèles à l'échelle du trillion de paramètres. Passez des points de terminaison supplémentaires à `--rpc` sous forme de liste séparée par des virgules (par exemple, `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)