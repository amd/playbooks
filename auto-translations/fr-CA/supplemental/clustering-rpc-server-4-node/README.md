<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traduction automatique.** Cette page a été traduite automatiquement de l'anglais et n'a pas été révisée par un humain. Elle peut contenir des erreurs, et certaines instructions, commandes, options de téléchargement, disponibilités de produits ou autres contenus peuvent varier selon la langue ou la région. En cas d'incompatibilité ou de divergence, la version originale anglaise du playbook fait foi.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Regroupement en grappe de quatre Ryzen™ AI Halo avec RPC

## Aperçu

Votre Ryzen™ AI Halo est déjà capable d'exécuter des grands modèles de langage localement. Le regroupement en grappe pousse cela encore plus loin en combinant la mémoire GPU de plusieurs systèmes sur un réseau local, vous donnant accès à des modèles encore plus grands avec un raisonnement plus solide, une meilleure génération de code et une compréhension multilingue plus approfondie, le tout entièrement sur votre propre matériel.

Ce guide pratique vous enseigne comment regrouper en grappe quatre systèmes Ryzen AI Halo à l'aide du moteur RPC de llama.cpp et exécuter Kimi K2.6, un grand modèle de mélange d'experts (mixture-of-experts), sur les quatre machines avec l'accélération AMD ROCm™.

## Ce que vous apprendrez

- Comment étendre l'allocation de VRAM sur les systèmes Ryzen AI Halo
- L'installation de llama.cpp avec la prise en charge de ROCm et RPC
- La configuration des travailleurs RPC et le lancement de l'inférence distribuée sur quatre nœuds
- L'exécution d'un modèle à 1 billion de paramètres sur quatre systèmes Ryzen AI Halo en réseau

## Configuration de la mémoire

> **Remarque** : Effectuez cette étape sur les quatre machines (Machine 1 à Machine 4).

<!-- @os:windows -->
Sous Windows, pour exécuter des modèles plus volumineux nécessitant davantage de mémoire, nous devons utiliser l'allocation de mémoire graphique variable AMD (VRAM du iGPU).

Cela peut être fait en ouvrant le panneau de configuration AMD Software: Adrenalin Edition et en naviguant vers : `Performance > Tuning > AMD Variable Graphics Memory`. Réglez la valeur à **96 Go**. Veuillez redémarrer le système pour que les changements prennent effet.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Sous Linux, ROCm utilise un bassin de mémoire système partagé, et ce bassin est configuré par défaut à la moitié de la mémoire système.

Cette quantité peut être augmentée en modifiant le paramètre de pages du gestionnaire de table de traduction (TTM) du noyau, à l'aide des instructions suivantes. AMD recommande de définir la VRAM dédiée minimale dans le BIOS (0,5 Go).

* Installez l'utilitaire pipx et ajoutez le chemin des roues (wheels) installées par pipx au chemin de recherche du système.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Installez la roue amd-debug-tools depuis PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Exécutez l'outil amd-ttm pour interroger les paramètres actuels de la mémoire partagée.
  ```bash
  amd-ttm
  ```

* Reconfigurez les paramètres de la mémoire partagée à **120 Go** :
  ```bash
  amd-ttm --set 120
  ```

* Redémarrez le système pour que les changements prennent effet.


<!-- @os:end -->
<!-- @device:halo_box -->
## Vérification des mises à jour logicielles

<!-- @require:software-update -->
<!-- @device:end -->
## Prérequis

### Matériel

Ce guide pratique nécessite quatre unités Ryzen AI Halo et un commutateur Ethernet, connectés en topologie en étoile, chaque unité étant câblée directement au commutateur.

| Composant | Quantité | Description |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | Nœuds de calcul formant la grappe |
| Commutateur Ethernet 10 Gbit/s | 1 | Commutateur central permettant la communication multinœuds entre les Ryzen AI Halo (au moins 4 ports) |
| Câble Ethernet | 4 | Relie chaque unité Halo au commutateur (Cat 7 ou supérieur recommandé) |

> **Remarque** : Quatre ports de commutateur Ethernet sont nécessaires pour connecter les quatre unités Ryzen AI Halo. Un cinquième port est nécessaire si vous accédez au modèle à partir d'une machine cliente distincte plutôt qu'à partir de l'une des unités Halo.

### Logiciel
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

> **Remarque** : Effectuez cette étape sur les quatre machines (Machine 1 à Machine 4).

Connectez chaque unité Ryzen AI Halo au commutateur Ethernet à l'aide d'un câble Cat 7 (ou supérieur). Cela établit la liaison 10 Gbit/s utilisée pour la communication à haute vitesse entre les nœuds.
<!-- @os:linux -->
### 1. Déterminer les interfaces réseau

Sur chaque machine, trouvez le nom de son interface réseau et notez-le (il sera désigné ci-dessous sous le nom `IFNAME`). Exécutez :

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Cela affiche le nom de l'interface directement, par exemple :

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

> **Remarque** : Si la vitesse est inférieure à `10000Mb/s` ou que la liaison ne s'établit pas, vérifiez le branchement du câble et confirmez que le port du commutateur est configuré à 10 Gbit/s. Certains commutateurs exigent que la négociation automatique soit désactivée et que la vitesse de liaison soit réglée manuellement; consultez la documentation de votre commutateur.

<!-- @os:end -->

<!-- @os:windows -->
### Vérifier la vitesse de la liaison réseau

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

> **Remarque** : Si la vitesse est inférieure à `10 Gbps` ou que la liaison ne s'établit pas, vérifiez le branchement du câble et confirmez que le port du commutateur est configuré à 10 Gbit/s. Certains commutateurs exigent que la négociation automatique soit désactivée et que la vitesse de liaison soit réglée manuellement; consultez la documentation de votre commutateur.

<!-- @os:end -->

## Installation de llama.cpp

> **Remarque** : Effectuez cette étape sur les quatre machines (Machine 1 à Machine 4).

Deux options d'installation sont offertes :

- [Option 1 : Lemonade SDK (recommandée)](#option-1-lemonade-sdk-recommended) - binaires précompilés, configuration la plus rapide
- [Option 2 : Compilation manuelle depuis les sources](#option-2-manual-source-build) - compilation depuis les sources avec contrôle complet des indicateurs de compilation

### Option 1 : Lemonade SDK (recommandée)

Le Lemonade SDK fournit des versions nocturnes de llama.cpp avec l'accélération AMD ROCm 7, ciblant des GPU tels que gfx1151 (Strix Halo / Ryzen AI Max+ 395) et d'autres architectures Radeon récentes.

<!-- @os:windows -->
#### Étape 1 : Téléchargement des binaires précompilés

Accédez à la page de la dernière version et téléchargez l'archive correspondant à votre plateforme et à la cible GPU :

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Téléchargez le fichier nommé `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (où `xxxx` correspond au numéro de version).

#### Étape 2 : Extraction des binaires

Décompressez l'archive téléchargée :

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Ce répertoire contient maintenant des versions compilées avec ROCm de `llama-cli.exe`, `llama-server.exe` et `ggml-rpc-server.exe`, précompilées pour votre système Ryzen AI Halo.

#### Étape 3 : Vérification de la détection du GPU

```bash
.\llama-cli.exe --list-devices
```

Résultat attendu :

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```
<!-- @os:end -->

<!-- @os:linux -->
#### Étape 1 : Téléchargement des binaires précompilés

Accédez à la page de la dernière version et téléchargez l'archive correspondant à votre plateforme et à la cible GPU :

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Téléchargez le fichier nommé `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (où `xxxx` correspond au numéro de version).

#### Étape 2 : Extraction et préparation des binaires

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Ce répertoire contient maintenant des versions compilées avec ROCm de `llama-cli`, `llama-server` et `rpc-server`, précompilées pour votre système Ryzen AI Halo.

#### Étape 3 : Vérification de la détection du GPU

```bash
./llama-cli --list-devices
```

Résultat attendu :

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```
<!-- @os:end -->
Une fois llama.cpp préparé sur chaque nœud, passez à la section [Téléchargement du modèle](#downloading-the-model).

### Option 2 : Compilation manuelle des sources

<!-- @os:windows -->
#### Étape 1 : Compilation de llama.cpp

Ouvrez la fenêtre **x64 Native Tools Command Prompt** (installée avec Visual Studio Build Tools) et clonez le dépôt :

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Ajoutez HIP à votre chemin d'accès et compilez avec la prise en charge de ROCm et de RPC :

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Indicateur de compilation | But |
|-----------|---------|
| `-DGGML_HIP=ON` | Active la pile logicielle ROCm/HIP |
| `-DGGML_RPC=ON` | Active le RPC pour l'inférence distribuée |
| `-DGPU_TARGETS=gfx1151` | Cible le GPU Ryzen AI Halo (Radeon 8060s) |
| `-G Ninja` | Utilise le système de compilation Ninja |

#### Étape 2 : Vérification de la détection du GPU

```cmd
cd rocm\bin
.\llama-cli.exe --list-devices
```

Résultat attendu :

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```

#### Étape 3 : Ajout de HIP à votre chemin d'accès utilisateur

L'étape de compilation ci-dessus a défini `%HIP_PATH%\bin` pour la session en cours uniquement. Pour rendre les bibliothèques HIP accessibles dans tout terminal (et pas seulement dans le x64 Native Tools Command Prompt), ajoutez-le de façon permanente à votre `PATH` utilisateur :

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Une fois llama.cpp préparé sur chaque nœud, passez à la section [Téléchargement du modèle](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Étape 1 : Compilation de llama.cpp

Clonez le dépôt :

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Compilez avec la prise en charge de ROCm et de RPC :

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Indicateur de compilation | But |
|-----------|---------|
| `-DGGML_HIP=ON` | Active la pile logicielle ROCm |
| `-DGGML_RPC=ON` | Active le RPC pour l'inférence distribuée |
| `-DAMDGPU_TARGETS="gfx1151"` | Cible le GPU Ryzen AI Halo (Radeon 8060s) |

Pour en savoir plus sur les options de compilation, consultez la [documentation de compilation de llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Étape 2 : Vérification de la détection du GPU

```bash
cd rocm/bin
./llama-cli --list-devices
```

Résultat attendu :

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

Ce guide pratique utilise [Kimi K2.6](https://huggingface.co/moonshotai/Kimi-K2.6) dans la quantification `UD-Q2_K_XL` provenant de [Unsloth](https://huggingface.co/unsloth/Kimi-K2.6-GGUF/tree/main/UD-Q2_K_XL). Cette quantification tient dans la mémoire GPU combinée de quatre nœuds Ryzen AI Halo.

Téléchargez les fichiers GGUF à l'aide de l'interface en ligne de commande Hugging Face :
<!-- @os:linux -->
```bash
pip install huggingface-hub
hf download unsloth/Kimi-K2.6-GGUF --include "UD-Q2_K_XL/*" --local-dir Kimi-K2.6-GGUF
```
<!-- @os:end -->

<!-- @os:windows -->
```cmd
python -m pip install -U huggingface-hub

$hfScripts = python -c "import sysconfig; print(sysconfig.get_path('scripts'))"
$env:Path = "$hfScripts;$env:Path"

hf download unsloth/Kimi-K2.6-GGUF --include "UD-Q2_K_XL/*" --local-dir Kimi-K2.6-GGUF
```
<!-- @os:end -->

> **Remarque** : le téléchargement du modèle doit être effectué sur la machine 1 (le contrôleur). Les nœuds de travail RPC (machines 2, 3 et 4) n'ont pas besoin d'une copie locale des fichiers du modèle.

## Lancement du modèle sur la grappe

Le moteur RPC (Remote Procedure Call) de llama.cpp permet à une seule instance de llama.cpp de déléguer des couches du modèle à des nœuds de travail distants via le réseau. Une machine agit comme **contrôleur** (machine 1), gérant la tokenisation, l'ordonnancement et l'orchestration. Chacune des trois autres machines exécute un **serveur RPC** léger (machines 2, 3 et 4) qui expose sa mémoire GPU et sa capacité de calcul au contrôleur.

Au moment du chargement, llama.cpp répartit le modèle entre les quatre nœuds. Une fois le chargement terminé, l'inférence se déroule comme si elle s'exécutait sur un seul accélérateur. Le RPC gère les transferts de tenseurs et la synchronisation en arrière-plan.

### Étape 1 : Démarrage des serveurs RPC (machines 2, 3 et 4)

Sur chacune des machines 2, 3 et 4, démarrez le serveur RPC afin d'exposer ses ressources GPU au contrôleur :
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

| Indicateur | But |
|------|---------|
| `-p` | Port sur lequel diffuser le serveur RPC |
| `-c` | Active une antémémoire locale pour les tenseurs volumineux, évitant les transferts réseau répétés pendant le chargement du modèle |
| `--host` | Adresse IP à laquelle lier le serveur RPC (`0.0.0.0` pour toutes les interfaces) |

Pour en savoir plus sur les options, consultez la [documentation RPC de llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Étape 2 : Lancement du modèle (machine 1)

Une fois les serveurs RPC en cours d'exécution sur les machines 2, 3 et 4, lancez l'inférence depuis la machine 1 à l'aide de `llama-cli` ou de `llama-server`.
#### llama-cli

`llama-cli` fournit une interface en ligne de commande pour interagir directement avec le modèle. Elle est idéale pour l'analyse comparative, le débogage et l'expérimentation bas niveau.

<!-- @os:linux -->
```bash
./llama-cli \
  -m /path/to/Kimi-K2.6-GGUF/UD-Q2_K_XL/Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  -b 4096 \
  -ub 4096 \
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **Recherche de `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`** : Sur chacune des machines 2, 3 et 4, exécutez `hostname -I | awk '{print $1}'` pour trouver son adresse IP locale.
<!-- @os:end -->

<!-- @os:windows -->
> **Remarque** : Exécutez cette commande dans Terminal (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\Kimi-K2.6-GGUF\UD-Q2_K_XL\Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  -b 4096 `
  -ub 4096 `
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **Recherche de `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`** : Sur chacune des machines 2, 3 et 4, exécutez `ipconfig | findstr /C:"IPv4"` dans Terminal (Powershell) pour trouver son adresse IP locale.

<!-- @os:end -->

Une fois lancé, `llama-cli` affiche la progression du chargement du modèle et présente une invite interactive vous permettant de discuter directement avec le modèle :

![llama-cli exécutant Kimi K2.6 sur quatre nœuds](assets/llama-cli-example.png)

#### llama-server

`llama-server` expose le même moteur d'inférence par l'intermédiaire d'un processus serveur persistant, doté d'une interface Web intégrée et d'une API HTTP compatible avec OpenAI. Il s'agit de l'interface à privilégier pour les déploiements de longue durée, l'accès multiutilisateur et l'intégration avec des outils externes.

<!-- @os:linux -->
```bash
./llama-server \
  -m /path/to/Kimi-K2.6-GGUF/UD-Q2_K_XL/Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  -b 4096 \
  -ub 4096 \
  --host 0.0.0.0 \
  --port 8081 \
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **Recherche de `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`** : Sur chacune des machines 2, 3 et 4, exécutez `hostname -I | awk '{print $1}'` pour trouver son adresse IP locale.
<!-- @os:end -->

<!-- @os:windows -->
> **Remarque** : Exécutez cette commande dans Terminal (Powershell).

```powershell
.\llama-server.exe `
  -m C:\path\to\Kimi-K2.6-GGUF\UD-Q2_K_XL\Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  -b 4096 `
  -ub 4096 `
  --host 0.0.0.0 `
  --port 8081 `
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **Recherche de `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`** : Sur chacune des machines 2, 3 et 4, exécutez `ipconfig | findstr /C:"IPv4"` dans Terminal (Powershell) pour trouver son adresse IP locale.
<!-- @os:end -->

Une fois démarré, ouvrez `http://<HOST_IP>:8081` dans votre navigateur pour accéder à l'interface Web intégrée. Celle-ci propose une interface de clavardage dans le navigateur pour interagir avec le modèle :

![Interface Web de llama-server exécutant Kimi K2.6 sur quatre nœuds](assets/llama-server-example.png)

<!-- @os:linux -->
> **Recherche de `<HOST_IP>`** : Sur la machine 1, exécutez `hostname -I | awk '{print $1}'` pour trouver son adresse IP locale.
<!-- @os:end -->

<!-- @os:windows -->
> **Recherche de `<HOST_IP>`** : Sur la machine 1, exécutez `ipconfig | findstr /C:"IPv4"` dans Terminal (Powershell) pour trouver son adresse IP locale.
<!-- @os:end -->

#### Référence des paramètres

| Indicateur | Fonction |
|------|---------|
| `-m` | Chemin d'accès au fichier de modèle GGUF (utilisez le premier fragment, `00001-of-00008`) |
| `-c` | Taille du contexte en jetons. Des valeurs plus élevées utilisent davantage de mémoire |
| `-fa on` | Active rocWMMA Flash Attention pour de meilleures performances sur les GPU AMD |
| `-ngl 999` | Décharge toutes les couches du modèle vers le GPU |
| `-lm none` | Définit le mode de chargement du modèle sur `none`, désactivant la mise en correspondance mémoire (memory-mapping) afin de réduire les temps de chargement lorsque la taille du modèle dépasse la RAM système mais tient dans la VRAM |
| `-b` | Taille logique des lots en jetons. La valeur 4096 équilibre le débit et l'utilisation de la mémoire entre les nœuds |
| `-ub` | Taille physique (micro) des lots pour le traitement des invites. Faire correspondre à `-b` évite une surcharge inutile liée au découpage |
| `--host` | Adresse IP sur laquelle lier `llama-server` (`llama-server` uniquement) |
| `--port` | Port sur lequel exposer l'API HTTP (`llama-server` uniquement) |
| `--rpc` | Liste des points de terminaison des travailleurs RPC séparés par des virgules (`IP:port`) |

Pour une description complète des paramètres, consultez la [documentation de llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) et la [documentation de llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Étapes suivantes

- **Connecter des applications tierces** : `llama-server` expose une API compatible avec OpenAI. Pointez toute application compatible avec OpenAI (comme Open WebUI) vers `http://<HOST_IP>:8081` avec une clé API fictive (par exemple, `none`) pour vous connecter à votre grappe
- **Explorer d'autres modèles** : Parcourez les GGUF quantifiés sur [Hugging Face](https://huggingface.co/models?search=gguf) pour trouver des modèles qui tiennent dans la mémoire GPU combinée de votre grappe
- **Étendre au-delà de quatre nœuds** : Ajoutez d'autres systèmes Ryzen AI Halo comme travailleurs RPC additionnels pour accéder à des modèles dépassant l'échelle de 1 000 milliards de paramètres. Transmettez des points de terminaison supplémentaires à `--rpc` sous forme de liste séparée par des virgules (par exemple, `--rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053,<RPC_WORKER_5_IP>:50053`)