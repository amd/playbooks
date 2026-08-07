<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traduction automatique.** Cette page a été traduite automatiquement depuis l'anglais et n'a pas été relue par un traducteur humain. Elle peut contenir des erreurs, et certaines instructions, commandes, téléchargements, disponibilités de produits ou autres contenus peuvent varier selon la langue ou la région. En cas d'incohérence ou de divergence, la version originale en anglais du playbook fait foi et prévaut.
<!-- auto-translated-disclaimer:end -->

# Configuration de la plateforme

Ce document décrit les configurations de plateforme attendues pour exécuter ce playbook.

## Applications/Frameworks requis

### Windows/Linux

- **Lemonade Server** doit être installé en suivant le
  [guide d'installation de Lemonade](https://lemonade-server.ai/docs/guide/install/).
- **Node.js 22.12 ou version ultérieure** et `npm`, utilisés par la CLI `agent-canvas` et les
  serveurs MCP lancés avec `npx`.
- **uv**, le gestionnaire de paquets Python qu'Agent Canvas utilise pour gérer l'environnement
  du serveur agent. Installez-le à partir du
  [guide d'installation de uv](https://docs.astral.sh/uv/getting-started/installation/).

## Modèles requis

### Windows/Linux

Le modèle suivant doit être disponible pour Lemonade Server avant de démarrer le
playbook.

| Type de modèle | ID du modèle | Remarques |
| --- | --- | --- |
| Modèle de chat GGUF | `Qwen3.6-35B-A3B-GGUF` | Servi par Lemonade Server sur `http://127.0.0.1:13305/api/v1`. Utilisez un modèle GGUF plus petit sur les appareils disposant de moins de 32 Go de mémoire. |

Démarrez le modèle avec :

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

## Identifiants externes

Ce playbook nécessite :

- Un jeton GitHub avec un accès en lecture au dépôt à résumer.
- Un jeton de bot Slack avec les autorisations `chat:write` et un accès en lecture aux canaux.
- Un ID d'équipe Slack et l'ID du canal Slack cible.