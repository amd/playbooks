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


## Aperçu

vLLM est un moteur d'inférence haute performance conçu pour les grands modèles de langage (LLM). Il offre un service optimisé avec regroupement continu (« continuous batching ») pour un débit élevé et une API compatible OpenAI pour une intégration transparente aux applications. Cela fait de vLLM un excellent choix pour les déploiements en production où la vitesse et l'efficacité des ressources sont essentielles.

Ce guide vous apprend à servir des LLM à l'aide de vLLM conteneurisé sur le GPU intégré et à interagir avec les modèles au moyen de l'API Python OpenAI.

## Ce que vous apprendrez

- Comment configurer et démarrer un serveur vLLM avec la prise en charge d'AMD ROCm™
- Comment interagir avec les modèles par l'intermédiaire des points de terminaison d'API compatibles OpenAI
- Comment envoyer des invites au serveur local avec `vllm-prompt`

## Configuration de la mémoire

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Vérifier les mises à jour logicielles

> **Remarque** : Si VS Code n'est pas installé, vous pouvez l'installer avec le AMD Ryzen™ AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Installation des logiciels prérequis

vLLM s'exécute dans un conteneur préconstruit avec ROCm et ses dépendances déjà harmonisées. Aucune installation supplémentaire n'est requise.

Il n'y a aucune étape d'installation de vLLM côté hôte. Démarrez vLLM avec :

```bash
vllm-launch
```

Le lanceur démarre le conteneur, cible le GPU intégré et expose un serveur vLLM local compatible OpenAI. Vous pouvez aussi cliquer sur l'icône vLLM dans la barre des tâches.

## Démarrage rapide

### 1. Confirmer que le serveur vLLM est en cours d'exécution

Le `vllm-launch` peut prendre quelques minutes pour tout initialiser. Une fois démarré, le serveur est accessible à `http://localhost:8001`. Gardez le terminal de lancement ouvert, car le serveur s'exécute au premier plan; ouvrez ensuite un terminal distinct pour les étapes suivantes. Les exemples ci-dessous utilisent `Qwen/Qwen3-1.7B`; si votre lanceur est configuré pour un autre modèle, remplacez-le par cet identifiant de modèle dans les requêtes.

### 2. Envoyer une invite

Utilisez le script `vllm-prompt` fourni pour envoyer une requête au serveur vLLM local compatible OpenAI :

```bash
vllm-prompt "Tell me a story"
```

### 3. Discuter avec le modèle à l'aide de l'API Python OpenAI

Puisque vLLM expose une API compatible OpenAI, vous pouvez utiliser le paquet Python `openai` pour interagir avec celle-ci.

D'abord, créez un environnement virtuel Python :

<!-- @os:linux -->
<!-- @device:halo_box -->
```bash
sudo apt install -y python3-venv
python3 -m venv vllm-env
source vllm-env/bin/activate
```
<!-- @device:end -->

Installez le paquet OpenAI
```bash
pip install openai
```

Créez un client `OpenAI` pointant vers le serveur vLLM local plutôt que vers les serveurs d'OpenAI. Le paramètre `api_key` est requis par le client, mais vLLM ne le valide pas; n'importe quelle chaîne de caractères convient donc :

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Ensuite, envoyez une requête de complétion de conversation. Celle-ci utilise le même format de messages que l'API OpenAI, soit une liste de messages avec des rôles comme `"user"` et `"assistant"`. En définissant `stream=True`, la réponse arrivera de façon progressive plutôt que d'un seul coup :

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

Enfin, parcourez les fragments diffusés et affichez chaque morceau de texte au fur et à mesure de son arrivée :

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

Le script [chat_with_model.py](assets/chat_with_model.py) fourni contient l'exemple complet et peut être téléchargé.


## Choix et configuration d'un modèle

Par défaut, `vllm-launch` sert `Qwen/Qwen3-1.7B` comme modèle de test sur le port `8001`. Vous pouvez changer le modèle, le port et les paramètres de service de vLLM sans reconstruire ni modifier le conteneur.

### Modèles testés par AMD

Les modèles suivants sont préconfigurés et validés par AMD :

| Modèle | Remarques |
|-------|-------|
| `Qwen/Qwen3-1.7B` | Modèle par défaut. Léger et rapide à charger. |
| `openai/gpt-oss-20b` | Modèle plus volumineux pour des réponses de meilleure qualité. |

### Lancer un autre modèle

Transmettez l'identifiant du modèle avec `--model` (ou `-m`) :

```bash
vllm-launch --model openai/gpt-oss-20b
```

### Changer le port

Transmettez un port supérieur à 1024 avec `--port` (ou `-p`); la valeur par défaut est `8001` :

```bash
vllm-launch --port 8080 --model openai/gpt-oss-20b
```

Si vous changez le port, faites pointer le `base_url` de votre client vers ce même port (par exemple `http://localhost:8080/v1`).

### Transmettre des paramètres vLLM supplémentaires

Tout argument supplémentaire est transmis directement à vLLM, ce qui vous permet d'ajuster le comportement du service, comme la longueur du contexte ou le type de données. Il existe deux façons de les fournir.

**En ligne**, après les options du lanceur :

```bash
vllm-launch --model openai/gpt-oss-20b --max-model-len 8192
```

**De façon persistante**, dans un fichier de configuration situé à `~/.local/share/vLLM/vllm-launch.conf`. Ce fichier n'existe pas par défaut; créez-le et ajoutez vos arguments sous forme de tableau Bash :

```bash
VLLM_EXTRA_ARGS=(--max-model-len 8192 --dtype float16)
```

Utilisez `+=` pour ajouter aux arguments par défaut plutôt que de les remplacer :

```bash
VLLM_EXTRA_ARGS+=(--max-model-len 8192)
```

Pour voir toutes les options du lanceur à tout moment, exécutez :

```bash
vllm-launch --help
```

### Emplacement de stockage des modèles

`vllm-launch` recherche les modèles à deux emplacements :

| Emplacement | Chemin |
|----------|------|
| Modèles système | `/var/cache/models` |
| Modèles utilisateur | `~/.local/share/vLLM/models` |

Vous pouvez placer un modèle téléchargé dans l'un ou l'autre de ces répertoires et le lancer en transmettant son chemin ou son identifiant à `--model` :

```bash
vllm-launch --model /var/cache/models/my-model
```

> **Remarque** : L'exécution de votre propre modèle téléchargé de cette façon devrait fonctionner une fois le modèle placé dans l'un des répertoires ci-dessus, mais ce processus n'a pas encore été officiellement validé par AMD.

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
- Effectuer des appels API vers le serveur vLLM en utilisant des requêtes en diffusion continue et non continue
- Dépanner les problèmes courants liés au démarrage du serveur, à la mémoire et aux connexions client

Vous disposez maintenant d'un déploiement vLLM conteneurisé pour servir de grands modèles de langage avec des performances optimisées sur le GPU intégré.

## Prochaines étapes

- **Essayer différents modèles** — Utilisez `vllm-launch --model <model>` pour expérimenter avec différents LLM et comparer les performances (voir [Choix et configuration d'un modèle](#choosing-and-configuring-a-model)).
- **Créer une application** — Utilisez l'API compatible OpenAI pour intégrer vLLM à une application Python, un agent conversationnel ou un flux de travail automatisé.
- **Affiner et servir** — Affinez un modèle à l'aide de LoRA ou QLoRA, puis déployez-le avec vLLM pour une inférence optimisée.
## Ressources supplémentaires

- **[Documentation officielle de vLLM](https://docs.vllm.ai/)** — Guides complets et références de l'API
- **[Dépôt GitHub de vLLM](https://github.com/vllm-project/vllm)** — Code source, problèmes et discussions communautaires