<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Podman

Podman est un logiciel de conteneurisation pour Linux.


**Étape 1** : Installez le moteur Podman de base ainsi que le plugiciel autonome Compose V2.

```bash
sudo apt update && sudo apt install -y podman docker-compose-plugin podman-compose
```

**Étape 2** : Vérifiez Podman et Compose

```bash
podman --version
podman-compose --version
```

**Étape 3** : Activez le socket API Podman à l'échelle du système afin que le plugiciel Compose puisse communiquer avec l'environnement d'exécution des conteneurs.

```bash
sudo systemctl enable --now podman.socket
```
**Étape 4** : Exécutez un conteneur de test temporaire pour vérifier que le moteur peut extraire et exécuter des images avec succès.

```bash
sudo podman run --rm docker.io/library/hello-world
```