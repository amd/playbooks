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

# Regroupement en grappe de deux Ryzen™ AI Halo avec RCCL

## Aperçu

Votre Ryzen™ AI Halo est déjà capable d'exécuter des grands modèles de langage localement. Le regroupement en grappe va plus loin en combinant la mémoire GPU de plusieurs systèmes sur un réseau local, vous donnant accès à des modèles encore plus grands avec un raisonnement plus solide, une meilleure génération de code et une compréhension multilingue plus approfondie, le tout entièrement sur votre propre matériel.

Ce guide pratique vous enseigne comment regrouper en grappe deux systèmes Ryzen AI Halo à l'aide de RCCL (ROCm Communication Collectives Library) avec vLLM et exécuter Qwen3.5-397B, un modèle de 397 milliards de paramètres, sur les deux machines avec accélération ROCm.

## Ce que vous apprendrez

- Comment étendre l'allocation de VRAM sur les systèmes Ryzen AI Halo
- Le lancement de vLLM avec la prise en charge de ROCm
- La configuration de RCCL pour l'inférence à parallélisme tensoriel multi-nœuds sur deux systèmes Ryzen AI Halo
- L'exécution d'un modèle de 397 milliards de paramètres sur deux systèmes Ryzen AI Halo en réseau

## Prérequis

### Matériel

Ce guide pratique nécessite deux unités Ryzen AI Halo et un commutateur Ethernet, connectés en topologie étoile, chaque unité étant reliée directement au commutateur.

| Composant | Quantité | Description |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Nœuds de calcul qui forment la grappe |
| Commutateur Ethernet 10 Gbit/s | 1 | Commutateur central permettant la communication multi-nœuds entre les unités Ryzen AI Halo (au moins 2 ports) |
| Câble Ethernet | 2 | Relie chaque unité Halo au commutateur (Cat 7 ou supérieur recommandé) |

> **Remarque** : Deux ports de commutateur Ethernet sont requis pour connecter les deux unités Ryzen AI Halo. Un troisième port est requis si vous accédez au modèle à partir d'une machine cliente distincte plutôt qu'à partir de l'une des unités Halo.

### Logiciels
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Configuration matérielle physique

> **Remarque** : Effectuez cette étape à la fois sur la machine 1 et la machine 2.

Connectez chaque unité Ryzen AI Halo au commutateur Ethernet à l'aide d'un câble Cat 7 (ou supérieur). Cela établit la liaison à 10 Gbit/s utilisée pour la communication haute vitesse entre les nœuds.

### 1. Déterminer les interfaces réseau

Sur chaque machine, trouvez le nom de son interface réseau et notez-le (il sera désigné dans le reste des instructions par `IFNAME`). Exécutez :

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Ceci affiche directement le nom de l'interface, par exemple :

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

> **Remarque** : Si la vitesse est inférieure à `10000Mb/s` ou si la liaison ne s'établit pas, vérifiez la connexion du câble et confirmez que le port du commutateur est configuré à 10 Gbit/s. Certains commutateurs nécessitent la désactivation de la négociation automatique et le réglage manuel de la vitesse de liaison; consultez la documentation de votre commutateur.

## Extension de l'allocation de VRAM

> **Remarque** : Effectuez cette étape à la fois sur la machine 1 et la machine 2.

### Configuration de la mémoire pour l'exécution de grands modèles

Sous Linux, ROCm utilise un pool de mémoire système partagé, et ce pool est configuré par défaut à la moitié de la mémoire système.

Cette quantité peut être augmentée en modifiant le paramètre de page du gestionnaire de table de traduction (TTM) du noyau, à l'aide des instructions suivantes. AMD recommande de définir la VRAM dédiée minimale dans le BIOS (0,5 Go).

* Installez l'utilitaire pipx et ajoutez le chemin des wheels installées par pipx au chemin de recherche du système.

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

* Redémarrez le système pour que les changements prennent effet.

## Initialisation du conteneur vLLM

> **Remarque** : Effectuez cette étape à la fois sur la machine 1 et la machine 2.

Votre Ryzen AI Halo est livré avec vLLM emballé dans une image de conteneur préconstruite, que vous exécutez à l'aide de Podman, un outil de conteneurisation gratuit et à code source ouvert.

### 1. Créer le répertoire de téléchargement des modèles

Lorsque vous servez le modèle Qwen3.5-397B dans ce guide pratique, vLLM téléchargera automatiquement les poids du modèle sur votre système. Pour vous assurer que ces poids sont accessibles depuis l'intérieur du conteneur, créez d'abord un répertoire de modèles que le conteneur peut monter :

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Lancer le conteneur vLLM

La commande ci-dessous lance le conteneur et vous place dans un shell interactif. Elle monte le répertoire de modèles que vous venez de créer et transmet votre `IFNAME` à `NCCL_SOCKET_IFNAME` et `GLOO_SOCKET_IFNAME`, indiquant à RCCL (la bibliothèque que vLLM utilise pour coordonner les GPU dans la grappe) quelle interface utiliser.

Démarrez le conteneur avec :

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Remarque** : Remplacez `<IFNAME>` par le nom de l'interface de sortie obtenu à l'étape [1. Déterminer les interfaces réseau](#1-determine-network-interfaces)

## Exécution du modèle sur la grappe

vLLM utilise Ray pour orchestrer la grappe et RCCL pour gérer la communication GPU à GPU entre les nœuds. Une machine agit comme le **nœud principal** (machine 1), coordonnant l'inférence. L'autre se joint en tant que **nœud de travail** (machine 2), contribuant sa mémoire GPU et sa puissance de calcul.

> **Remarque** : Ray est une dépendance facultative pour vLLM et n'est disponible que depuis l'intérieur du conteneur Podman préconfiguré.

Au lancement, vLLM répartit le modèle sur les deux nœuds à l'aide du parallélisme tensoriel. Une fois chargé, l'inférence se déroule comme si elle s'exécutait sur un seul accélérateur.

### Étape 1 : Démarrer le nœud principal Ray (machine 1)

Sur la machine 1, démarrez le nœud principal Ray pour initialiser la grappe :

```bash
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **Trouver `<MACHINE_1_IP>`** : Sur la machine 1, exécutez `hostname -I | awk '{print $1}'` pour trouver son adresse IP locale.

### Étape 2 : Rejoindre la grappe (machine 2)

Sur la machine 2, connectez-vous au nœud principal pour former la grappe :

```bash
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **Trouver `<MACHINE_2_IP>`** : Sur la machine 2, exécutez `hostname -I | awk '{print $1}'` pour trouver son adresse IP locale.
### Étape 3 : Servir le modèle (Machine 1)

Sur la Machine 1, lancez le serveur vLLM. Cette opération téléchargera automatiquement le modèle et commencera à le servir sur les deux nœuds :

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
| `--max-model-len` | Longueur maximale du contexte en jetons |
| `--gpu-memory-utilization` | Fraction de la mémoire GPU à allouer (0,0 à 1,0) |
| `--dtype` | Type de données pour les poids du modèle |
| `--tensor-parallel-size` | Nombre de GPU sur lesquels partager le modèle (à définir selon le nombre total de GPU dans la grappe) |
| `--distributed-executor-backend` | Moteur d'exécution pour l'exécution multinœud (`ray` pour les déploiements en grappe) |
| `--enforce-eager` | Désactive la compilation des graphes CUDA pour assurer la compatibilité |
| `--language-model-only` | Ignore le chargement des composants auxiliaires du modèle (p. ex. l'encodeur de vision) |
| `--reasoning-parser` | Active l'analyse structurée de la sortie de raisonnement pour le modèle |

Pour connaître l'utilisation complète des paramètres, consultez la [documentation de vLLM](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Accès au modèle

vLLM expose une API compatible avec OpenAI, ce qui vous permet de connecter tout client ou interface compatible à votre grappe. Une option populaire est [Open WebUI](https://github.com/open-webui/open-webui), qui offre une interface de clavardage accessible depuis un navigateur.

Pour connecter Open WebUI à votre point de terminaison vLLM :

1. Ouvrez **Settings** > **Admin Panel** > **Connections**
2. Cliquez sur le **+** dans **Manage OpenAI API Connections**
3. Réglez le **Connection Type** à **External**
4. Réglez le **URL** à `http://<MACHINE_1_IP>:7000/v1`
5. Sous **Auth**, sélectionnez **None** dans le menu déroulant
6. Laissez le champ **Model IDs** vide pour découvrir automatiquement tous les modèles offerts par le point de terminaison

> **Trouver `<MACHINE_1_IP>`** : Sur la Machine 1, exécutez `hostname -I | awk '{print $1}'` pour trouver son adresse IP locale. Si vous accédez à Open WebUI depuis la Machine 1 elle-même, vous pouvez utiliser `http://localhost:7000/v1`.

![Paramètres de connexion Open WebUI pour le point de terminaison vLLM](assets/openwebui-connection.png)

Une fois la connexion établie, sélectionnez le modèle dans le menu déroulant des modèles d'Open WebUI et commencez à clavarder. Le modèle s'exécute maintenant sur vos deux nœuds Ryzen AI Halo :

![Clavardage avec Qwen3.5-397B dans Open WebUI](assets/openwebui-chat.png)

## Prochaines étapes

- **Explorer d'autres modèles** : Découvrez de nouveaux modèles sur [Hugging Face](https://huggingface.co/models?&sort=trending) qui conviennent à la mémoire GPU combinée de votre grappe
- **Passer à quatre nœuds** : Ajoutez deux autres systèmes Ryzen AI Halo comme travailleurs Ray supplémentaires afin de partager les modèles sur encore plus de GPU. Cela nécessite un commutateur Ethernet doté d'au moins quatre ports, soit un pour chaque nœud. Suivez l'[Étape 2 : Joindre la grappe](#step-2-join-the-cluster-machine-2) sur chaque travailleur supplémentaire et augmentez `--tensor-parallel-size` en conséquence
- **Essayer d'autres stratégies de parallélisme** : vLLM prend en charge le [parallélisme expert](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) pour les modèles à mélange d'experts et le [parallélisme des données](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) pour un débit plus élevé. Expérimentez avec `--enable-expert-parallel` et `--data-parallel-size` afin de trouver la meilleure configuration pour votre charge de travail