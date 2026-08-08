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

# Mise en cluster de deux Ryzen™ AI Halo avec RCCL

## Présentation

Votre Ryzen™ AI Halo est déjà capable d'exécuter localement de grands modèles de langage. La mise en cluster va plus loin en combinant la mémoire GPU de plusieurs systèmes sur un réseau local, vous donnant accès à des modèles encore plus grands, avec un raisonnement plus poussé, une meilleure génération de code et une compréhension multilingue plus approfondie, le tout entièrement sur votre propre matériel.

Ce playbook vous apprend à mettre en cluster deux systèmes Ryzen AI Halo à l'aide de RCCL (ROCm Communication Collectives Library) avec vLLM, et à exécuter Qwen3.5-397B, un modèle à 397 milliards de paramètres, sur les deux machines avec l'accélération ROCm.

## Ce que vous allez apprendre

- Comment étendre l'allocation de VRAM sur les systèmes Ryzen AI Halo
- Le lancement de vLLM avec la prise en charge de ROCm
- La configuration de RCCL pour l'inférence en parallélisme tensoriel multi-nœuds sur deux systèmes Ryzen AI Halo
- L'exécution d'un modèle à 397 milliards de paramètres sur deux systèmes Ryzen AI Halo en réseau

## Prérequis

### Matériel

Ce playbook nécessite deux unités Ryzen AI Halo et un commutateur Ethernet, connectés en topologie en étoile, chaque unité étant reliée directement au commutateur.

| Composant | Quantité | Description |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Nœuds de calcul formant le cluster |
| Commutateur Ethernet 10 Gbps | 1 | Commutateur central permettant la communication multi-nœuds entre les unités Ryzen AI Halo (au moins 2 ports) |
| Câble Ethernet | 2 | Relie chaque unité Halo au commutateur (Cat 7 ou supérieur recommandé) |

> **Remarque** : Deux ports du commutateur Ethernet sont nécessaires pour connecter les deux unités Ryzen AI Halo. Un troisième port est requis si vous accédez au modèle depuis une machine cliente distincte plutôt que depuis l'une des unités Halo.

### Logiciel
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Configuration matérielle physique

> **Remarque** : Effectuez cette étape sur la Machine 1 et la Machine 2.

Connectez chaque unité Ryzen AI Halo au commutateur Ethernet à l'aide d'un câble Cat 7 (ou supérieur). Cela établit la liaison 10 Gbps utilisée pour la communication à haut débit entre les nœuds.

### 1. Déterminer les interfaces réseau

Sur chaque machine, trouvez le nom de son interface réseau et notez-le (il sera désigné dans la suite des instructions par `IFNAME`). Exécutez :

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

> **Remarque** : Si la vitesse est inférieure à `10000Mb/s` ou si la liaison ne s'établit pas, vérifiez la connexion du câble et confirmez que le port du commutateur est configuré à 10 Gbps. Certains commutateurs nécessitent que la négociation automatique soit désactivée et que la vitesse de liaison soit définie manuellement ; consultez la documentation de votre commutateur.

## Extension de l'allocation de VRAM

> **Remarque** : Effectuez cette étape sur la Machine 1 et la Machine 2.

### Configuration de la mémoire pour l'exécution de grands modèles

Sous Linux, ROCm utilise un pool de mémoire système partagé, et ce pool est configuré par défaut à la moitié de la mémoire système.

Cette quantité peut être augmentée en modifiant le paramètre de pages du Translation Table Manager (TTM) du noyau, à l'aide des instructions suivantes. AMD recommande de définir la VRAM dédiée minimale dans le BIOS (0,5 Go).

* Installez l'utilitaire pipx et ajoutez le chemin des wheels installés par pipx au chemin de recherche système.

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

* Reconfigurez les paramètres de mémoire partagée à **120 Go** :
  ```bash
  amd-ttm --set 120
  ```

* Redémarrez le système pour que les modifications prennent effet.

## Initialisation du conteneur vLLM

> **Remarque** : Effectuez cette étape sur la Machine 1 et la Machine 2.

Votre Ryzen AI Halo est livré avec vLLM packagé dans une image de conteneur prête à l'emploi, que vous exécutez à l'aide de Podman, un outil de conteneurisation gratuit et open source.

### 1. Créer le répertoire de téléchargement du modèle

Lorsque vous servez le modèle Qwen3.5-397B dans ce playbook, vLLM téléchargera automatiquement les poids du modèle sur votre système. Pour vous assurer que ces poids sont accessibles depuis l'intérieur du conteneur, créez d'abord un répertoire de modèles que le conteneur pourra monter :

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Lancer le conteneur vLLM

La commande ci-dessous lance le conteneur et vous place dans un shell interactif. Elle monte le répertoire de modèles que vous venez de créer et transmet votre `IFNAME` à `NCCL_SOCKET_IFNAME` et `GLOO_SOCKET_IFNAME`, indiquant à RCCL (la bibliothèque utilisée par vLLM pour coordonner les GPU sur le cluster) quelle interface utiliser.

Démarrez le conteneur avec :

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Remarque** : Remplacez `<IFNAME>` par le nom de l'interface de sortie obtenu à l'étape [1. Déterminer les interfaces réseau](#1-determine-network-interfaces)

## Exécution du modèle sur le cluster

vLLM utilise Ray pour orchestrer le cluster et RCCL pour gérer la communication GPU à GPU entre les nœuds. Une machine agit en tant que **nœud principal** (Machine 1), coordonnant l'inférence. L'autre rejoint le cluster en tant que **nœud de travail** (Machine 2), apportant sa mémoire GPU et sa puissance de calcul.

> **Remarque** : Ray est une dépendance optionnelle pour vLLM et n'est disponible que depuis le conteneur Podman préconfiguré.

Au démarrage, vLLM répartit le modèle sur les deux nœuds à l'aide du parallélisme tensoriel. Une fois chargée, l'inférence se déroule comme si elle s'exécutait sur un seul accélérateur.

### Étape 1 : Démarrer le nœud principal Ray (Machine 1)

Sur la Machine 1, démarrez le nœud principal Ray pour initialiser le cluster :

```bash
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **Recherche de `<MACHINE_1_IP>`** : Sur la Machine 1, exécutez `hostname -I | awk '{print $1}'` pour trouver son adresse IP locale.
### Étape 2 : Rejoindre le cluster (Machine 2)

Sur la Machine 2, connectez-vous au nœud principal pour former le cluster :

```bash
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **Trouver `<MACHINE_2_IP>`** : Sur la Machine 2, exécutez `hostname -I | awk '{print $1}'` pour trouver son adresse IP locale.

### Étape 3 : Servir le modèle (Machine 1)

Sur la Machine 1, lancez le serveur vLLM. Cela téléchargera automatiquement le modèle et commencera à le servir sur les deux nœuds :

```bash
vllm serve Qwen/Qwen3.5-397B-A17B-GPTQ-Int4 \
  --port 7000 \
  --host 0.0.0.0 \
  --max-model-len 32768 \
  --gpu-memory-utilization 0.9 \
  --dtype float16 \
  --tensor-parallel-size 2 \
  --distributed-executor-backend ray \
  --enforce-eager \
  --language-model-only \
  --reasoning-parser qwen3
```

#### Référence des paramètres

| Indicateur | Objectif |
|------|---------|
| `--port` | Port sur lequel servir l'API HTTP |
| `--host` | Adresse IP à laquelle lier le serveur (`0.0.0.0` pour toutes les interfaces) |
| `--max-model-len` | Longueur de contexte maximale en tokens |
| `--gpu-memory-utilization` | Fraction de la mémoire GPU à allouer (0.0–1.0) |
| `--dtype` | Type de données pour les poids du modèle |
| `--tensor-parallel-size` | Nombre de GPU sur lesquels répartir le modèle (à définir sur le nombre total de GPU dans le cluster) |
| `--distributed-executor-backend` | Backend pour l'exécution multi-nœud (`ray` pour les déploiements en cluster) |
| `--enforce-eager` | Désactive la compilation des graphes CUDA pour des raisons de compatibilité |
| `--language-model-only` | Ignore le chargement des composants de modèle auxiliaires (par exemple, l'encodeur visuel) |
| `--reasoning-parser` | Active l'analyse structurée de la sortie de raisonnement pour le modèle |

Pour l'usage complet des paramètres, consultez la [documentation vLLM](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Accéder au modèle

vLLM expose une API compatible OpenAI, vous pouvez donc connecter n'importe quel client ou interface compatible à votre cluster. Une option populaire est [Open WebUI](https://github.com/open-webui/open-webui), qui fournit une interface de chat basée sur navigateur.

Pour connecter Open WebUI à votre point de terminaison vLLM :

1. Ouvrez **Settings** > **Admin Panel** > **Connections**
2. Cliquez sur le **+** dans **Manage OpenAI API Connections**
3. Définissez le **Connection Type** sur **External**
4. Définissez l'**URL** sur `http://<MACHINE_1_IP>:7000/v1`
5. Sous **Auth**, sélectionnez **None** dans le menu déroulant
6. Laissez **Model IDs** vide pour découvrir automatiquement tous les modèles depuis le point de terminaison

> **Trouver `<MACHINE_1_IP>`** : Sur la Machine 1, exécutez `hostname -I | awk '{print $1}'` pour trouver son adresse IP locale. Si vous accédez à Open WebUI depuis la Machine 1 elle-même, vous pouvez utiliser `http://localhost:7000/v1`.

![Paramètres de connexion Open WebUI pour le point de terminaison vLLM](assets/openwebui-connection.png)

Une fois connecté, sélectionnez le modèle dans le menu déroulant des modèles dans Open WebUI et commencez à discuter. Le modèle s'exécute désormais sur vos deux nœuds Ryzen AI Halo :

![Discussion avec Qwen3.5-397B dans Open WebUI](assets/openwebui-chat.png)

## Étapes suivantes

- **Explorer d'autres modèles** : Découvrez de nouveaux modèles sur [Hugging Face](https://huggingface.co/models?&sort=trending) qui correspondent à la mémoire GPU combinée de votre cluster
- **Passer à quatre nœuds** : Ajoutez deux systèmes Ryzen AI Halo supplémentaires en tant que workers Ray additionnels pour répartir les modèles sur encore plus de GPU. Cela nécessite un commutateur Ethernet avec au moins quatre ports, un pour chaque nœud. Suivez [Étape 2 : Rejoindre le cluster](#step-2-join-the-cluster-machine-2) sur chaque worker supplémentaire et augmentez `--tensor-parallel-size` en conséquence
- **Essayer d'autres stratégies de parallélisme** : vLLM prend en charge le [parallélisme expert](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) pour les modèles de type mixture-of-experts et le [parallélisme des données](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) pour un débit plus élevé. Expérimentez avec `--enable-expert-parallel` et `--data-parallel-size` pour trouver la meilleure configuration pour votre charge de travail