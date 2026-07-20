<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Ce guide utilise des balises spéciales que GitHub ne peut pas afficher. Veuillez consulter [amd.com/playbooks](https://amd.com/playbooks) pour prévisualiser correctement ce contenu.
<!-- @github-only:end -->


## Présentation

vLLM est un moteur d'inférence hautes performances conçu pour les grands modèles de langage (LLM). Il fournit un service optimisé avec un traitement par lots continu pour un débit élevé et une API compatible OpenAI pour une intégration transparente des applications. Cela rend vLLM idéal pour les déploiements en production où la vitesse et l'efficacité des ressources sont essentielles.

Ce guide vous apprend à servir des LLM en utilisant vLLM conteneurisé sur le GPU intégré et à interagir avec les modèles via l'API Python OpenAI.

## Ce que vous allez apprendre

- Comment configurer et démarrer un serveur vLLM avec la prise en charge AMD ROCm™
- Comment interagir avec les modèles via des points de terminaison API compatibles OpenAI
- Comment envoyer des prompts au serveur local avec `vllm-prompt`

## Configuration de la mémoire

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Vérifier les mises à jour logicielles

> **Remarque** : Si VS Code n'est pas installé, vous pouvez l'installer avec AMD Ryzen™ AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Installation des prérequis logiciels

Ce guide utilise une image de conteneur préconstruite qui inclut vLLM, la prise en charge ROCm, ainsi que les scripts d'assistance nécessaires pour lancer le serveur. Vous n'avez pas besoin d'installer PyTorch, vLLM, ou les scripts du guide manuellement en local.

Il n'y a pas d'étape d'installation de vLLM côté hôte. Démarrez vLLM avec :

```bash
vllm-launch
```

Le lanceur démarre le conteneur, cible le GPU intégré et expose un serveur vLLM local compatible OpenAI. Vous pouvez également cliquer sur l'icône vLLM dans la barre des tâches.

## Démarrage rapide

### 1. Confirmer que le serveur vLLM fonctionne

`vllm-launch` peut prendre quelques minutes pour tout initialiser. Une fois démarré, le serveur est disponible à l'adresse `http://localhost:8001`. Laissez le terminal de lancement ouvert car le serveur s'exécute au premier plan, puis ouvrez un terminal séparé pour les étapes suivantes. Les exemples ci-dessous utilisent `Qwen/Qwen3-1.7B` ; si votre lanceur est configuré pour un modèle différent, remplacez cet ID de modèle dans les requêtes.

### 2. Envoyer un prompt

Utilisez le script `vllm-prompt` fourni pour envoyer une requête au serveur local vLLM compatible OpenAI :

```bash
vllm-prompt "Tell me a story"
```

### 3. Discuter avec le modèle à l'aide de l'API Python OpenAI

Comme vLLM expose une API compatible OpenAI, vous pouvez utiliser le package Python `openai` pour interagir avec lui.

Tout d'abord, créez un environnement virtuel Python :

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

Créez un client `OpenAI` pointant vers le serveur vLLM local au lieu des serveurs d'OpenAI. La `api_key` est requise par le client mais vLLM ne la valide pas, donc n'importe quelle chaîne fonctionne :

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Ensuite, envoyez une requête de complétion de chat. Cela utilise le même format de message que l'API OpenAI — une liste de messages avec des rôles comme `"user"` et `"assistant"`. Définir `stream=True` signifie que la réponse arrivera de manière incrémentielle plutôt que d'un seul coup :

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

Enfin, parcourez les morceaux transmis en continu et affichez chaque partie de texte à mesure qu'elle arrive :

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

Le script inclus [chat_with_model.py](assets/chat_with_model.py) contient l'exemple complet et peut être téléchargé.


## Dépannage

### Connexion refusée

Assurez-vous que le serveur est en cours d'exécution :
```bash
curl http://localhost:8001/health
```

## Résumé

Dans ce guide, vous avez appris à :

- Démarrer vLLM conteneurisé avec la prise en charge ROCm sur le GPU intégré
- Démarrer un serveur vLLM avec des points de terminaison API compatibles OpenAI sur le port 8001
- Envoyer des prompts avec `vllm-prompt`
- Effectuer des appels API vers le serveur vLLM en utilisant des requêtes en streaming et non-streaming
- Résoudre les problèmes courants liés au démarrage du serveur, à la mémoire et aux connexions client

Vous disposez maintenant d'un déploiement vLLM conteneurisé pour servir des grands modèles de langage avec des performances optimisées sur le GPU intégré.

## Prochaines étapes

- **Essayez différents modèles** — Remplacez le modèle dans la configuration de `vllm-launch` pour expérimenter avec différents LLM et comparer les performances.
- **Créez une application** — Utilisez l'API compatible OpenAI pour intégrer vLLM dans une application Python, un chatbot ou un flux de travail automatisé.
- **Affinez et servez** — Affinez un modèle à l'aide de LoRA ou QLoRA, puis déployez-le avec vLLM pour une inférence optimisée.

## Ressources supplémentaires

- **[Documentation officielle de vLLM](https://docs.vllm.ai/)** — Guides complets et références API
- **[Dépôt GitHub de vLLM](https://github.com/vllm-project/vllm)** — Code source, problèmes et discussions communautaires