<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Ce guide utilise des balises spéciales que GitHub ne peut pas afficher. Veuillez visiter [amd.com/playbooks](https://amd.com/playbooks) pour prévisualiser correctement ce contenu.
<!-- @github-only:end -->


## Vue d'ensemble

vLLM est un moteur d'inférence haute performance conçu pour les grands modèles de langage (LLM). Il offre un service optimisé avec un traitement par lots continu pour un débit élevé, ainsi qu'une API compatible OpenAI pour une intégration transparente des applications. vLLM est ainsi idéal pour les déploiements en production où la vitesse et l'efficacité des ressources sont essentielles.

Ce guide vous apprend à servir des LLM à l'aide de vLLM conteneurisé sur le GPU intégré, et à interagir avec les modèles via l'API Python OpenAI.

## Ce que vous apprendrez

- Comment configurer et démarrer un serveur vLLM avec la prise en charge AMD ROCm™
- Comment interagir avec les modèles via des points de terminaison d'API compatibles OpenAI
- Comment envoyer des invites au serveur local avec `vllm-prompt`

## Configuration de la mémoire

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Vérifier les mises à jour logicielles

> **Remarque** : Si VS Code n'est pas installé, vous pouvez l'installer avec AMD Ryzen™ AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Installation des prérequis logiciels

Ce guide utilise une image de conteneur préconstruite qui inclut vLLM, la prise en charge de ROCm et les scripts d'aide nécessaires au lancement du serveur. Vous n'avez pas besoin d'installer PyTorch, vLLM ou les scripts locaux du guide manuellement.

Il n'y a pas d'étape d'installation de vLLM côté hôte. Démarrez vLLM avec :

```bash
vllm-launch
```

Le lanceur démarre le conteneur, cible le GPU intégré et expose un serveur vLLM local compatible OpenAI. Vous pouvez également cliquer sur l'icône vLLM dans la barre des tâches.

## Démarrage rapide

### 1. Confirmer que le serveur vLLM est en cours d'exécution

`vllm-launch` peut prendre quelques minutes pour tout initialiser. Une fois démarré, le serveur est disponible à l'adresse `http://localhost:8001`. Gardez le terminal de lancement ouvert car le serveur s'exécute au premier plan, puis ouvrez un terminal séparé pour les étapes suivantes. Les exemples ci-dessous utilisent `Qwen/Qwen3-1.7B` ; si votre lanceur est configuré pour un modèle différent, substituez cet identifiant de modèle dans les requêtes.

### 2. Envoyer une invite

Utilisez le script `vllm-prompt` fourni pour envoyer une requête au serveur local compatible OpenAI de vLLM :

```bash
vllm-prompt "Tell me a story"
```

### 3. Discuter avec le modèle via l'API Python OpenAI

Puisque vLLM expose une API compatible OpenAI, vous pouvez utiliser le package Python `openai` pour interagir avec lui.

Commencez par créer un environnement virtuel Python :

<!-- @os:linux -->
<!-- @device:halo_box -->
```bash
sudo apt install -y python3-venv
python3 -m venv vllm-env
source vllm-env/bin/activate
```
<!-- @device:end -->

Installez le package OpenAI
```bash
pip install openai
```

Créez un client `OpenAI` pointant vers le serveur vLLM local plutôt que vers les serveurs d'OpenAI. La valeur `api_key` est requise par le client, mais vLLM ne la valide pas, donc n'importe quelle chaîne de caractères convient :

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Ensuite, envoyez une requête de complétion de chat. Celle-ci utilise le même format de messages que l'API OpenAI — une liste de messages avec des rôles tels que `"user"` et `"assistant"`. Définir `stream=True` signifie que la réponse arrivera de manière incrémentielle plutôt que d'un seul coup :

```python
response = client.chat.completions.create(
    model="Qwen/Qwen3-1.7B",
    messages=[
        {"role": "user", "content": "Tell me a short story"},
    ],
    max_tokens=2048,  # Maximum number of tokens the model will generate in its response
    stream=True,
)
```

Enfin, itérez sur les fragments diffusés en continu et affichez chaque portion de texte au fur et à mesure de son arrivée :

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

Le script [chat_with_model.py](assets/chat_with_model.py) inclus contient l'exemple complet et peut être téléchargé.


## Dépannage

### Connexion refusée

Assurez-vous que le serveur est en cours d'exécution :
```bash
curl http://localhost:8001/health
```

## Résumé

Dans ce guide, vous avez appris à :

- Démarrer vLLM conteneurisé avec la prise en charge de ROCm sur le GPU intégré
- Démarrer un serveur vLLM avec des points de terminaison d'API compatibles OpenAI sur le port 8001
- Envoyer des invites avec `vllm-prompt`
- Effectuer des appels d'API vers le serveur vLLM en utilisant des requêtes en streaming et sans streaming
- Résoudre les problèmes courants liés au démarrage du serveur, à la mémoire et aux connexions client

Vous disposez désormais d'un déploiement vLLM conteneurisé pour servir des grands modèles de langage avec des performances optimisées sur le GPU intégré.

## Prochaines étapes

- **Essayez différents modèles** — Remplacez le modèle dans la configuration `vllm-launch` pour expérimenter avec différents LLM et comparer les performances.
- **Créez une application** — Utilisez l'API compatible OpenAI pour intégrer vLLM dans une application Python, un chatbot ou un flux de travail d'automatisation.
- **Affinez et servez** — Affinez un modèle à l'aide de LoRA ou QLoRA, puis déployez-le avec vLLM pour une inférence optimisée.

## Ressources supplémentaires

- **[Documentation officielle de vLLM](https://docs.vllm.ai/)** — Guides complets et références d'API
- **[Dépôt GitHub de vLLM](https://github.com/vllm-project/vllm)** — Code source, problèmes et discussions communautaires