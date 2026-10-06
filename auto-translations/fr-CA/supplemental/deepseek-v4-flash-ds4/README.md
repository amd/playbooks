<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traduction automatique.** Cette page a été traduite automatiquement de l'anglais et n'a pas été révisée par un humain. Elle peut contenir des erreurs, et certaines instructions, commandes, options de téléchargement, disponibilités de produits ou autres contenus peuvent varier selon la langue ou la région. En cas d'incompatibilité ou de divergence, la version originale anglaise du playbook fait foi.
<!-- auto-translated-disclaimer:end -->

# <!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Aperçu

[DeepSeek V4 Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) est la variante axée sur l'efficacité de la famille DeepSeek V4 — un modèle de type mélange d'experts (Mixture of Experts) comptant 284 milliards de paramètres, dont 13 milliards de paramètres actifs. Selon le [rapport technique de DeepSeek](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash), il obtient un score de 79 % sur SWE-bench Verified et de 91,6 % sur LiveCodeBench.

[ds4 (Dwarf Star 4)](https://github.com/antirez/ds4) est un moteur d'inférence dédié conçu spécifiquement pour cette architecture de modèle. Plutôt qu'un environnement d'exécution universel, ds4 cible directement la famille DeepSeek V4 grâce à des optimisations de noyaux spécifiques à l'architecture pour le logiciel AMD ROCm™. Il s'agit actuellement de l'une des implémentations les plus performantes de DeepSeek V4 Flash sur Strix Halo.

Ce tutoriel montre comment utiliser `ai-toolbox-cockpit`, une interface utilisateur en mode terminal, pour configurer ds4, télécharger les poids du modèle et commencer à exécuter DeepSeek V4 Flash localement sur la plateforme de développement AMD Ryzen™ AI Halo.

## Ce que vous apprendrez

- Comment installer et lancer l'interface utilisateur en mode terminal `ai-toolbox-cockpit`
- Comment créer le conteneur de boîte à outils ROCm pour ds4
- Comment télécharger la quantification recommandée pour un seul nœud Halo
- Comment démarrer le serveur d'inférence ds4 et exposer un point de terminaison compatible OpenAI
- Comment connecter une interface Web ou un agent de codage au serveur local

## Configuration de la mémoire

<!-- @require:memory-config -->

## Installation des prérequis logiciels

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @prereq:distrobox,ds4-cockpit,ds4-toolbox-image -->

> **Exigences système pour cette configuration (nœud unique, IQ2_XXS avec un contexte de 126 000) :**
> - Un système Strix Halo avec **au moins 128 Go de mémoire unifiée**.
> - La **mémoire vive vidéo (VRAM) dédiée du BIOS (tampon de trame UMA) réglée au minimum**, afin que le bassin de mémoire partagée puisse être aussi grand que possible.
> - Le **bassin de mémoire partagée du GPU réglé à au moins 110 Go** : exécutez `amd-ttm --set 110` (voir l'étape de configuration de la mémoire ci-dessus), puis redémarrez. Des valeurs plus basses peuvent entraîner des erreurs de mémoire insuffisante lors du chargement du modèle avec un contexte de 126 000. Si votre système dispose de moins de mémoire disponible, réduisez plutôt la valeur de **Context** dans le mode serveur.
>
> **Remarque :** Essayez de régler le **bassin de mémoire partagée du GPU** à **110 Go** comme valeur de départ. Si vous obtenez des erreurs de mémoire insuffisante, augmentez le bassin de mémoire partagée ou réduisez la taille du contexte.

ai-toolbox-cockpit utilise des boîtes à outils conteneurisées pour exécuter le moteur ds4. Installez `podman`, `distrobox` et `pipx` :

```bash
sudo apt update
sudo apt install -y podman distrobox pipx
```

<!-- @test:id=ds4-prereqs-linux timeout=60 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
podman --version
distrobox version 2>/dev/null || distrobox --version
pipx --version
echo "OK: podman, distrobox, and pipx are installed"
```
<!-- @test:end -->

## Quantifications disponibles

L'auteur de ds4 fournit plusieurs versions quantifiées de DeepSeek V4 Flash au format GGUF. Tous les modèles ci-dessous utilisent un étalonnage par matrice d'importance (imatrix), qui préserve une précision plus élevée pour les parties du modèle les plus importantes pour les tâches de codage et de raisonnement.

| Quantification | Taille | Description |
|-------------|------|-------------|
| [IQ2_XXS imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~80,8 Go | Recommandé pour un seul nœud de 128 Go |
| [Hybrid Q2/Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~97 Go | Conserve les couches 37 à 42 en précision Q4 pour une meilleure exactitude. Tient dans 128 Go, mais laisse moins d'espace pour le contexte |
| [Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~153 Go | Qualité supérieure. Nécessite deux nœuds Halo via la mise en grappe multi-nœuds |
| [MTP Speculative Decoding](https://huggingface.co/antirez/deepseek-v4-gguf) | ~3,6 Go | Module complémentaire facultatif pour le décodage spéculatif permettant d'améliorer la vitesse de génération |

Le modèle **IQ2_XXS imatrix** constitue un bon point de départ. Il tient facilement sur un seul nœud et laisse suffisamment de mémoire pour une fenêtre de contexte raisonnable.

## Installation d'ai-toolbox-cockpit

[ai-toolbox-cockpit](https://github.com/kyuz0/ai-toolbox-cockpit) est une interface utilisateur légère en mode terminal qui facilite l'installation de divers moteurs d'IA. Nous l'utiliserons pour créer notre conteneur ds4, télécharger les poids du modèle et démarrer les serveurs. Installez-le avec `pipx` :

<!-- @test:id=ds4-cockpit-install-linux timeout=300 -->
```bash
pipx install git+https://github.com/kyuz0/ai-toolbox-cockpit.git
```
<!-- @test:end -->

Lancez le cockpit :
```bash
ai-toolbox-cockpit
```

<!-- @test:id=ds4-cockpit-linux timeout=60 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
# Verify the pipx-installed cockpit entry point is on PATH (do NOT launch the TUI).
command -v ai-toolbox-cockpit
echo "OK: ai-toolbox-cockpit is installed and on PATH"
```
<!-- @test:end -->

## Étape 1 : Création de la boîte à outils

Dans l'onglet **Interactive Toolboxes**, sélectionnez la dernière boîte à outils disponible/stable pour ds4 (p. ex. `ds4-rocm-10.0`) et cliquez sur **Create/Update**. Cette action récupère l'image du conteneur et crée l'environnement de la boîte à outils.


<p align="center">
  <img src="assets/ai-toolbox-cockpit-toolboxes.png" alt="Selecting the ds4 toolbox in ai-toolbox-cockpit" width="800"/>
</p>

<!-- @test:id=ds4-toolbox-image-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

# The toolbox version changes over time, so match the image family, not a fixed tag.
if ! podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'; then
  echo "No strix-halo-ds4-toolbox image found. Create the toolbox in ai-toolbox-cockpit (Interactive Toolboxes tab) first."
  exit 1
fi
echo "OK: ds4 toolbox container image is present"
```
<!-- @test:end -->

## Étape 2 : Téléchargement du modèle

Accédez à l'onglet **Models**. Sélectionnez d'abord le moteur (ds4). Ensuite, sélectionnez **IQ2_XXS imatrix (~80,8 Go)** dans le menu déroulant et cliquez sur **Download**. Les fichiers du modèle seront enregistrés dans `~/ds4` par défaut (vous pouvez modifier le chemin de stockage).

> **Remarque :** Le modèle IQ2_XXS fait environ 80 Go, le téléchargement peut donc prendre un certain temps selon votre connexion. Vous pourrez poursuivre une fois celui-ci terminé.

<p align="center">
  <img src="assets/ai-toolbox-cockpit-models.png" alt="Selecting and downloading the IQ2_XXS model" width="800"/>
</p>

<!-- @test:id=ds4-model-downloaded-linux timeout=60 hidden=True -->
```bash
set -euo pipefail

# ai-toolbox-cockpit saves model weights to ~/ds4 by default
model_dir="$HOME/ds4"

if [ ! -d "$model_dir" ]; then
  echo "Model directory $model_dir does not exist. Download the model in ai-toolbox-cockpit (Model Manager tab) first."
  exit 1
fi

if ! find "$model_dir" -maxdepth 2 -iname '*.gguf' | grep -q .; then
  echo "No .gguf model files found under $model_dir. Download the IQ2_XXS imatrix model in ai-toolbox-cockpit first."
  exit 1
fi

# Prefer to confirm the recommended IQ2_XXS imatrix quantization is present.
if find "$model_dir" -maxdepth 2 -iname '*IQ2*imatrix*.gguf' | grep -q .; then
  echo "OK: IQ2_XXS imatrix model is downloaded"
else
  echo "OK: a GGUF model is present (recommended IQ2_XXS imatrix file not detected by name)"
fi
```
<!-- @test:end -->

## Étape 3 : Démarrage du serveur

Accédez à l'onglet **Server Mode**. Sélectionnez le modèle téléchargé et la boîte à outils, puis configurez la taille du contexte, l'hôte et le port. Lorsque vous êtes prêt, cliquez sur **Start ds4-server**.

> **Astuce :** Une taille de contexte de `126000` est une valeur de départ raisonnable qui devrait tenir sur un seul nœud — vous pouvez l'augmenter si vous disposez de mémoire supplémentaire, ou la réduire si vous rencontrez des erreurs de mémoire insuffisante. Le port (`8000` dans ce guide) est arbitraire; choisissez n'importe quel port libre.

> **Cache KV sur disque (facultatif).** Activer le **KV Disk Cache** transfère le cache KV sur disque (dans le **Host Cache Dir**, par défaut `~/.cache/ds4-kv`) afin que les invites système répétées soient restaurées à partir du SSD plutôt que recalculées. Il s'agit d'une optimisation de performance pour les flux de travail des agents de codage comportant des invites longues et répétées; elle n'est **pas requise** pour exécuter le serveur.

<p align="center">
  <img src="assets/ai-toolbox-cockpit-server.png" alt="Configuring and starting the ds4 server" width="800"/>
</p>

Le serveur démarrera et écoutera sur le port 8000, exposant un point de terminaison d'API compatible OpenAI à l'adresse `http://localhost:8000/v1`.

**Test rapide :**
```bash
curl http://127.0.0.1:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "deepseek-v4-flash",
    "messages": [{"role": "user", "content": "Hello!"}],
    "stream": false
  }'
```

<!-- @test:id=ds4-server-chat-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail

# This runner is shared with other playbooks, and ds4 at a 126k context consumes almost the entire GPU memory pool.
# So rather than keeping ds4 resident, CI starts the server, verifies a chat completion, then stops it again.
# This frees the memory for the next job.
# ds4 has no separate "unload"; stopping the server process is what releases the ~80 GB model.

CONTAINER="ds4-ci-server"
MODEL_DIR="$HOME/ds4"

# Locate the downloaded model (prefer the recommended IQ2_XXS imatrix file).
model_file="$(find "$MODEL_DIR" -maxdepth 2 -iname '*IQ2*imatrix*.gguf' 2>/dev/null | head -1)"
if [ -z "$model_file" ]; then
  model_file="$(find "$MODEL_DIR" -maxdepth 2 -iname '*.gguf' 2>/dev/null | head -1)"
fi
if [ -z "$model_file" ]; then
  echo "No .gguf model found under $MODEL_DIR. Download it in ai-toolbox-cockpit first."
  exit 1
fi
model_name="$(basename "$model_file")"

# Pick the toolbox image (version-agnostic).
image="$(podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox' | head -1)"
if [ -z "$image" ]; then
  echo "No strix-halo-ds4-toolbox image found. Create the toolbox in ai-toolbox-cockpit first."
  exit 1
fi

# Always stop/remove the server on exit so it never holds GPU memory afterwards.
cleanup() {
  podman stop -t 10 "$CONTAINER" >/dev/null 2>&1 || true
  podman rm -f "$CONTAINER" >/dev/null 2>&1 || true
}
trap cleanup EXIT

# keep-id maps the calling user into the container. Root does not need it, and as root it cannot
# be combined with --ipc=host (crun fails to mount /dev/mqueue), so root keeps the host user namespace.
userns=keep-id
if [ "$(id -u)" -eq 0 ]; then
  userns=host
fi

# Remove any stale instance, then start ds4-server detached (same flags ai-toolbox-cockpit uses, with -d instead of -it).
podman rm -f "$CONTAINER" >/dev/null 2>&1 || true
podman run -d --name "$CONTAINER" \
  --device /dev/dri --device /dev/kfd \
  --group-add keep-groups \
  --security-opt seccomp=unconfined \
  --ipc=host \
  --cap-add=SYS_PTRACE \
  --security-opt label=disable \
  --userns="$userns" \
  -p 127.0.0.1:8000:8000 \
  -v "$MODEL_DIR":/models:ro \
  "$image" \
  ds4-server -m "/models/$model_name" --ctx 126000 --host 0.0.0.0 --port 8000

# Wait for readiness; the ~80 GB model can take a few minutes to load.
up=false
for i in $(seq 1 240); do
  code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 3 http://127.0.0.1:8000/v1/models || true)"
  if [ -n "$code" ] && [ "$code" != "000" ]; then
    up=true
    break
  fi
  if ! podman inspect -f '{{.State.Running}}' "$CONTAINER" 2>/dev/null | grep -q true; then
    echo "ds4-server container exited during startup:"
    podman logs "$CONTAINER" 2>&1 | tail -40 || true
    exit 1
  fi
  sleep 2
done

if [ "$up" != "true" ]; then
  echo "ds4 server did not become ready on http://127.0.0.1:8000"
  podman logs "$CONTAINER" 2>&1 | tail -40 || true
  exit 1
fi
echo "OK: ds4 server is responding on :8000"

body='{
  "model": "deepseek-v4-flash",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 32,
  "stream": false
}'

out="$(curl -sS --fail-with-body --max-time 300 http://127.0.0.1:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d "$body")"

if [ -z "$out" ]; then
  echo "Empty response from ds4 /v1/chat/completions"
  exit 1
fi

export DS4_OUT="$out"
python3 - <<'PY'
import json, os, sys

data = json.loads(os.environ["DS4_OUT"])
choices = data.get("choices")
if not choices:
    print("Response has no 'choices':")
    print(json.dumps(data, indent=2)[:2000])
    sys.exit(1)

message = choices[0].get("message", {}) or {}
content = message.get("content") or message.get("reasoning_content")
if not content:
    print("Response choice has empty content:")
    print(json.dumps(data, indent=2)[:2000])
    sys.exit(1)

print("OK: ds4 chat/completions returned content")
PY

echo "OK: ds4 server test complete; server stopped and GPU memory released"
```
<!-- @test:end -->
## Connexion d'une interface Web

Vous pouvez connecter n'importe quelle interface de clavardage prenant en charge le format d'API OpenAI. Par exemple, pour utiliser HuggingFace ChatUI :

```bash
docker run --network=host \
  -e PORT=3000 \
  -e OPENAI_BASE_URL=http://localhost:8000/v1 \
  -e OPENAI_API_KEY=dummy \
  -v chat-ui-data:/data \
  ghcr.io/huggingface/chat-ui-db
```

Ouvrez `http://localhost:3000` dans votre navigateur pour commencer à clavarder.

> **Remarque :** `--network=host` place l'interface Web sur le réseau de l'hôte afin qu'elle puisse joindre directement le serveur ds4 sur `localhost`. Cela permet de garder le serveur ds4 lié à la boucle locale (il n'a pas besoin d'être exposé sur d'autres interfaces).

> **Astuce :** Le port de l'interface Web (`3000` ici, défini via `PORT`) est arbitraire — choisissez n'importe quel port libre si le `3000` est déjà utilisé, et ouvrez ce port dans votre navigateur à la place. Assurez-vous que le port dans `OPENAI_BASE_URL` correspond au port sur lequel votre serveur ds4 s'exécute.

## Connexion d'un agent de programmation

Le serveur ds4 expose des points de terminaison compatibles OpenAI et Anthropic, de sorte que la plupart des agents de programmation peuvent s'y connecter directement. Par exemple, pour l'ajouter à l'agent de programmation `pi`, ajoutez le bloc suivant à `~/.pi/agent/models.json` :

```json
"ds4": {
  "name": "ds4.c local",
  "baseUrl": "http://localhost:8000/v1",
  "api": "openai-completions",
  "apiKey": "dsv4-local",
  "compat": {
    "supportsStore": false,
    "supportsDeveloperRole": false,
    "supportsReasoningEffort": true,
    "supportsUsageInStreaming": true,
    "maxTokensField": "max_tokens",
    "supportsStrictMode": false,
    "thinkingFormat": "deepseek",
    "requiresReasoningContentOnAssistantMessages": true
  },
  "models": [
    {
      "id": "deepseek-v4-flash",
      "name": "DeepSeek V4 Flash (ds4.c local)",
      "reasoning": true,
      "thinkingLevelMap": {
        "off": null,
        "minimal": "low",
        "low": "low",
        "medium": "medium",
        "high": "high",
        "xhigh": "xhigh"
      },
      "input": ["text"],
      "contextWindow": 131072,
      "maxTokens": 65536,
      "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 }
    }
  ]
}
```

> **Astuce** : Si votre agent de programmation ou votre interface Web s'exécute sur une machine différente de la plateforme Halo, vous devrez rediriger le port du serveur (`8000` ici) via SSH :
> ```bash
> ssh -L 8000:localhost:8000 <halo-host-ip>
> ```

## Étapes suivantes

- **Mise en grappe multinœud** : Si vous disposez de deux appareils Halo, ds4 prend en charge la distribution du modèle Q4 (~153 Go) sur les deux machines via le parallélisme de pipeline. Consultez la [documentation de ds4-toolbox](https://github.com/kyuz0/strix-halo-ds4-toolbox#distributed-inference-pipeline-parallelism) pour les instructions de configuration.
- **Décodage spéculatif (MTP)** : Téléchargez les poids MTP (~3,6 Go) et transmettez `--mtp` au serveur pour une vitesse de génération plus rapide.
- **Déchargement du cache KV sur disque** : Pour les flux de travail des agents de programmation, activez `--kv-disk-dir` afin que les invites système répétées soient restaurées à partir du SSD plutôt que recalculées à chaque fois.

Pour plus d'information, consultez le [dépôt ds4](https://github.com/antirez/ds4) et la [boîte à outils ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox).