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


## Aperçu

vLLM est un moteur d'inférence haute performance conçu pour les grands modèles de langage (LLM). Il offre un service optimisé avec un traitement par lots continu pour un débit élevé et une API compatible OpenAI pour une intégration applicative transparente. Cela rend vLLM particulièrement adapté aux déploiements de production où la rapidité et l'efficacité des ressources sont essentielles.

Ce guide vous apprend à servir des LLM à l'aide de vLLM conteneurisé sur le GPU intégré et à interagir avec les modèles via l'API Python OpenAI.

## Ce que vous allez apprendre

- Comment configurer et démarrer un serveur vLLM avec la prise en charge AMD ROCm™
- Comment interagir avec les modèles via des points de terminaison API compatibles OpenAI
- Comment envoyer des invites au serveur local avec `vllm-prompt`

## Configuration de la mémoire

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Vérifier les mises à jour logicielles

> **Remarque** : Si VS Code n'est pas installé, vous pouvez l'installer avec AMD Ryzen™ AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Installation des prérequis logiciels

vLLM s'exécute dans un conteneur préconstruit avec ROCm et ses dépendances déjà appariées. Aucune installation supplémentaire n'est nécessaire.

Il n'y a pas d'étape d'installation de vLLM côté hôte. Démarrez vLLM avec :

```bash
vllm-launch
```

Le lanceur démarre le conteneur, cible le GPU intégré et expose un serveur vLLM local compatible OpenAI. Vous pouvez également cliquer sur l'icône vLLM dans la barre des tâches.

## Démarrage rapide

### 1. Confirmer que le serveur vLLM est en cours d'exécution

`vllm-launch` peut prendre quelques minutes pour tout initialiser. Une fois démarré, le serveur est disponible à l'adresse `http://localhost:8001`. Laissez le terminal de lancement ouvert, car le serveur s'exécute au premier plan, puis ouvrez un terminal séparé pour les étapes suivantes. Les exemples ci-dessous utilisent `Qwen/Qwen3-1.7B` ; si votre lanceur est configuré pour un modèle différent, remplacez cet ID de modèle dans les requêtes.

### 2. Envoyer une invite

Utilisez le script `vllm-prompt` fourni pour envoyer une requête au serveur local vLLM compatible OpenAI :

```bash
vllm-prompt "Tell me a story"
```

### 3. Discuter avec le modèle à l'aide de l'API Python OpenAI

Puisque vLLM expose une API compatible OpenAI, vous pouvez utiliser le package Python `openai` pour interagir avec lui.

Tout d'abord, créez un environnement virtuel Python :

<!-- @os:linux -->
<!-- @device:halo_box -->
```bash
sudo apt install -y python3-venv
python3 -m venv vllm-env
source vllm-env/bin/activate
```
<!-- @device:end -->
<!-- @os:end -->

Installez le package OpenAI
```bash
pip install openai
```

Créez un client `OpenAI` pointant vers le serveur vLLM local au lieu des serveurs d'OpenAI. La clé `api_key` est requise par le client, mais vLLM ne la valide pas, donc n'importe quelle chaîne fonctionne :

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Ensuite, envoyez une requête de complétion de chat. Celle-ci utilise le même format de message que l'API OpenAI — une liste de messages avec des rôles tels que `"user"` et `"assistant"`. Définir `stream=True` signifie que la réponse arrivera de manière incrémentielle plutôt que d'un seul coup :

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

Enfin, parcourez les fragments diffusés et affichez chaque portion de texte au fur et à mesure de son arrivée :

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

Le script inclus [chat_with_model.py](assets/chat_with_model.py) contient l'exemple complet et peut être téléchargé.


## Choisir et configurer un modèle

Par défaut, `vllm-launch` sert `Qwen/Qwen3-1.7B` comme modèle de test sur le port `8001`. Vous pouvez changer le modèle, le port et les paramètres de service vLLM sans reconstruire ni modifier le conteneur.

### Modèles testés par AMD

Les modèles suivants sont préconfigurés et validés par AMD :

| Modèle | Remarques |
|-------|-------|
| `Qwen/Qwen3-1.7B` | Modèle par défaut. Léger et rapide à charger. |
| `openai/gpt-oss-20b` | Modèle plus grand pour des réponses de meilleure qualité. |

### Lancer un modèle différent

Transmettez l'ID du modèle avec `--model` (ou `-m`) :

```bash
vllm-launch --model openai/gpt-oss-20b
```

### Changer le port

Transmettez un port supérieur à 1024 avec `--port` (ou `-p`) ; la valeur par défaut est `8001` :

```bash
vllm-launch --port 8080 --model openai/gpt-oss-20b
```

Si vous changez le port, pointez le `base_url` de votre client vers le même port (par exemple `http://localhost:8080/v1`).

### Transmettre des paramètres vLLM supplémentaires

Tout argument supplémentaire est transmis directement à vLLM, ce qui vous permet d'ajuster le comportement du service, comme la longueur du contexte ou le type de données. Il existe deux façons de les fournir.

**En ligne**, après les options du lanceur :

```bash
vllm-launch --model openai/gpt-oss-20b --max-model-len 8192
```

**De manière persistante**, dans un fichier de configuration situé à `~/.local/share/vLLM/vllm-launch.conf`. Ce fichier n'existe pas par défaut — créez-le et ajoutez vos arguments sous forme de tableau Bash :

```bash
VLLM_EXTRA_ARGS=(--max-model-len 8192 --dtype float16)
```

Utilisez `+=` pour ajouter aux arguments par défaut au lieu de les remplacer :

```bash
VLLM_EXTRA_ARGS+=(--max-model-len 8192)
```

Pour voir toutes les options du lanceur à tout moment, exécutez :

```bash
vllm-launch --help
```

### Où sont stockés les modèles

`vllm-launch` recherche les modèles à deux emplacements :

| Emplacement | Chemin |
|----------|------|
| Modèles système | `/var/cache/models` |
| Modèles utilisateur | `~/.local/share/vLLM/models` |

Vous pouvez placer un modèle téléchargé dans l'un ou l'autre répertoire et le lancer en transmettant son chemin ou son ID à `--model` :

```bash
vllm-launch --model /var/cache/models/my-model
```

> **Remarque** : L'exécution de votre propre modèle téléchargé de cette manière devrait fonctionner une fois le modèle placé dans l'un des répertoires ci-dessus, mais ce flux de travail n'a pas encore été officiellement validé par AMD.

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
- Envoyer des invites avec `vllm-prompt`
- Effectuer des appels API vers le serveur vLLM en utilisant des requêtes en streaming et non-streaming
- Dépanner les problèmes courants liés au démarrage du serveur, à la mémoire et aux connexions client

Vous disposez maintenant d'un déploiement vLLM conteneurisé pour servir des grands modèles de langage avec des performances optimisées sur le GPU intégré.

## Prochaines étapes

- **Essayer différents modèles** — Utilisez `vllm-launch --model <model>` pour expérimenter avec différents LLM et comparer les performances (voir [Choisir et configurer un modèle](#choosing-and-configuring-a-model)).
- **Créer une application** — Utilisez l'API compatible OpenAI pour intégrer vLLM dans une application Python, un chatbot ou un flux de travail d'automatisation.
- **Affiner et servir** — Affinez un modèle à l'aide de LoRA ou QLoRA, puis déployez-le avec vLLM pour une inférence optimisée.
## Ressources supplémentaires

- **[Documentation officielle de vLLM](https://docs.vllm.ai/)** — Guides complets et références API
- **[Dépôt GitHub de vLLM](https://github.com/vllm-project/vllm)** — Code source, problèmes et discussions communautaires