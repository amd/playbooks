<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Podman

Podman est un logiciel de conteneurisation pour Linux.


**Étape 1** : Installez le moteur Podman principal et le plugin d'analyse Compose V2 autonome.

```bash
sudo apt update && sudo apt install -y podman docker-compose-plugin podman-compose
```

**Étape 2** : Vérifiez Podman et Compose

```bash
podman --version
podman-compose --version
```

**Étape 3** : Activez le socket API Podman à l'échelle du système afin que le plugin Compose puisse communiquer avec le runtime de conteneur.

```bash
sudo systemctl enable --now podman.socket
```
**Étape 4** : Exécutez un conteneur de test temporaire pour vérifier que le moteur peut extraire et exécuter des images avec succès.

```bash
sudo podman run --rm docker.io/library/hello-world
```