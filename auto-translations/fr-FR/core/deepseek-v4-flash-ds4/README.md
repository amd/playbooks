<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **Traduction automatique.** Cette page a été traduite automatiquement à partir de l'anglais et n'a pas été relue par un humain. Elle peut contenir des erreurs, et certaines étapes, commandes, téléchargements ou disponibilités de produits peuvent différer selon votre langue ou région. Si quelque chose semble incorrect, veuillez considérer le playbook original en anglais comme la source de référence.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> Ce playbook utilise des balises spéciales que GitHub ne peut pas afficher. Veuillez consulter [amd.com/playbooks](https://amd.com/playbooks) pour prévisualiser correctement ce contenu.
<!-- @github-only:end -->

## Vue d'ensemble

[DeepSeek V4 Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) est la variante axée sur l'efficacité de la famille DeepSeek V4 — un modèle Mixture of Experts de 284 milliards de paramètres avec 13 milliards de paramètres actifs. Selon le [rapport technique de DeepSeek](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash), il obtient un score de 79 % sur SWE-bench Verified et de 91,6 % sur LiveCodeBench.

[ds4 (Dwarf Star 4)](https://github.com/antirez/ds4) est un moteur d'inférence dédié conçu spécifiquement pour cette architecture de modèle. Plutôt qu'un runtime généraliste, ds4 cible directement la famille DeepSeek V4 avec des optimisations de kernel spécifiques à l'architecture pour le logiciel AMD ROCm™. C'est actuellement l'une des implémentations les plus performantes de DeepSeek V4 Flash sur Strix Halo.

Ce tutoriel montre comment utiliser `ds4-cockpit`, une interface terminal, pour configurer ds4, télécharger les poids du modèle et démarrer le service de DeepSeek V4 Flash localement sur l'AMD Ryzen™ AI Halo Developer Platform.

## Ce que vous allez apprendre

- Comment installer et lancer l'interface terminal `ds4-cockpit`
- Comment créer le conteneur toolbox ROCm pour ds4
- Télécharger la quantification recommandée pour un seul nœud Halo
- Démarrer le serveur d'inférence ds4 et exposer un endpoint compatible OpenAI
- Connecter une interface Web ou un agent de codage au serveur local

<!-- @setup:memory_config -->

## Installation des prérequis logiciels

> **Configuration système requise pour cette configuration (IQ2_XXS mono-nœud avec un contexte de 126k) :**
> - Un système Strix Halo avec **au moins 128 Go de mémoire unifiée**.
> - **La VRAM dédiée du BIOS (frame buffer UMA) réglée au minimum**, afin que le pool de mémoire partagée puisse être aussi grand que possible.
> - Le pool de mémoire partagée du GPU **réglé sur au moins 110 Go** : exécutez `amd-ttm --set 110` (voir l'étape de configuration de la mémoire ci-dessus) puis redémarrez. Des valeurs inférieures entraînent des erreurs de manque de mémoire lors du chargement du modèle avec un contexte de 126k. Si votre système dispose de moins de mémoire disponible, réduisez plutôt la valeur **Context** dans le mode serveur.

ds4-cockpit utilise des conteneurs toolbox pour exécuter le moteur ds4. Installez `podman`, `distrobox` et `pipx` :

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

L'auteur de ds4 fournit plusieurs versions quantifiées de DeepSeek V4 Flash au format GGUF. Tous les modèles ci-dessous utilisent un calibrage par matrice d'importance (imatrix), qui préserve une précision plus élevée pour les parties du modèle les plus importantes pour les tâches de codage et de raisonnement.

| Quantification | Taille | Description |
|-------------|------|-------------|
| [IQ2_XXS imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~80,8 Go | Recommandé pour un seul nœud de 128 Go |
| [Hybride Q2/Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~97 Go | Conserve les couches 37 à 42 en précision Q4 pour une meilleure exactitude. Tient dans 128 Go mais laisse moins de place pour le contexte |
| [Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~153 Go | Qualité supérieure. Nécessite deux nœuds Halo via un clustering multi-nœuds |
| [Décodage spéculatif MTP](https://huggingface.co/antirez/deepseek-v4-gguf) | ~3,6 Go | Complément optionnel pour le décodage spéculatif afin d'améliorer la vitesse de génération |

Le modèle **IQ2_XXS imatrix** est un bon point de départ. Il tient confortablement sur un seul nœud et laisse suffisamment de mémoire pour une fenêtre de contexte raisonnable.

## Installation de ds4-cockpit

[ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox) est une interface terminal légère facilitant la mise en route de ds4 sur Strix Halo. Elle gère la création des conteneurs toolbox, le téléchargement des poids du modèle et le démarrage des serveurs. Installez-la avec `pipx` :

```bash
pipx install "git+https://github.com/kyuz0/strix-halo-ds4-toolbox.git#subdirectory=ds4-strix-halo-cockpit"
```

Lancez le cockpit :
```bash
ds4-cockpit
```

<!-- @test:id=ds4-cockpit-linux timeout=60 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
# Verify the pipx-installed cockpit entry point is on PATH (do NOT launch the TUI).
command -v ds4-cockpit
echo "OK: ds4-cockpit is installed and on PATH"
```
<!-- @test:end -->

## Création de la toolbox

Dans l'onglet **Interactive Toolboxes**, sélectionnez la dernière toolbox disponible (par ex. `ds4-rocm-7.2.4`) et cliquez sur **Create/Update**. Cette action télécharge l'image du conteneur et crée l'environnement toolbox.

> **Astuce** : La version de la toolbox évoluera avec le temps à mesure que de nouvelles versions de ROCm seront publiées. Choisissez la plus récente disponible dans la liste.

<p align="center">
  <img src="assets/ds4-cockpit-toolboxes.png" alt="Selecting the ds4 toolbox in ds4-cockpit" width="800"/>
</p>

<!-- @test:id=ds4-toolbox-image-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

# The toolbox version changes over time, so match the image family, not a fixed tag.
if ! podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'; then
  echo "No strix-halo-ds4-toolbox image found. Create the toolbox in ds4-cockpit (Interactive Toolboxes tab) first."
  exit 1
fi
echo "OK: ds4 toolbox container image is present"
```
<!-- @test:end -->

## Téléchargement du modèle

Accédez à l'onglet **Model Manager**. Sélectionnez **IQ2_XXS imatrix (~80,8 Go)** dans le menu déroulant et cliquez sur **Download**. Les fichiers du modèle seront enregistrés dans `~/ds4` par défaut (vous pouvez modifier le chemin de stockage).

<p align="center">
  <img src="assets/ds4-cockpit-model-manager.png" alt="Selecting and downloading the IQ2_XXS model" width="800"/>
</p>

<!-- @test:id=ds4-model-downloaded-linux timeout=60 hidden=True -->
```bash
set -euo pipefail

# ds4-cockpit saves model weights to ~/ds4 by default
model_dir="$HOME/ds4"

if [ ! -d "$model_dir" ]; then
  echo "Model directory $model_dir does not exist. Download the model in ds4-cockpit (Model Manager tab) first."
  exit 1
fi

if ! find "$model_dir" -maxdepth 2 -iname '*.gguf' | grep -q .; then
  echo "No .gguf model files found under $model_dir. Download the IQ2_XXS imatrix model in ds4-cockpit first."
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

## Démarrage du serveur

Accédez à l'onglet **Server Mode**. Sélectionnez le modèle téléchargé et la toolbox, puis configurez la taille du contexte (par ex. 126000), l'hôte et le port (8000). Une fois prêt, cliquez sur **Start ds4-server**.

> **Cache disque KV (optionnel).** Activer **KV Disk Cache** décharge le cache KV sur disque (dans **Host Cache Dir**, par défaut `~/.cache/ds4-kv`) afin que les prompts système répétés soient restaurés depuis le SSD au lieu d'être recalculés. Il s'agit d'une optimisation de performance pour les workflows d'agents de codage avec des prompts longs et répétés, et cela n'est **pas requis** pour exécuter le serveur.

<p align="center">
  <img src="assets/ds4-cockpit-server-mode.png" alt="Configuring and starting the ds4 server" width="800"/>
</p>

Le serveur démarrera et écoutera sur le port 8000, exposant un endpoint d'API compatible OpenAI à l'adresse `http://localhost:8000/v1`.

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
  echo "No .gguf model found under $MODEL_DIR. Download it in ds4-cockpit first."
  exit 1
fi
model_name="$(basename "$model_file")"

# Pick the toolbox image (version-agnostic).
image="$(podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox' | head -1)"
if [ -z "$image" ]; then
  echo "No strix-halo-ds4-toolbox image found. Create the toolbox in ds4-cockpit first."
  exit 1
fi

# Always stop/remove the server on exit so it never holds GPU memory afterwards.
cleanup() {
  podman stop -t 10 "$CONTAINER" >/dev/null 2>&1 || true
  podman rm -f "$CONTAINER" >/dev/null 2>&1 || true
}
trap cleanup EXIT

# Remove any stale instance, then start ds4-server detached (same flags ds4-cockpit uses, with -d instead of -it).
podman rm -f "$CONTAINER" >/dev/null 2>&1 || true
podman run -d --name "$CONTAINER" \
  --device /dev/dri --device /dev/kfd \
  --group-add keep-groups \
  --security-opt seccomp=unconfined \
  --ipc=host \
  --cap-add=SYS_PTRACE \
  --security-opt label=disable \
  --userns=keep-id \
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

Vous pouvez connecter n'importe quelle interface de chat prenant en charge le format d'API OpenAI. Par exemple, pour utiliser HuggingFace ChatUI :

```bash
docker run -p 3000:3000 \
  --add-host=host.docker.internal:host-gateway \
  -e OPENAI_BASE_URL=http://host.docker.internal:8000/v1 \
  -e OPENAI_API_KEY=dummy \
  -v chat-ui-data:/data \
  ghcr.io/huggingface/chat-ui-db
```

Ouvrez `http://localhost:3000` dans votre navigateur pour commencer à discuter.

## Connexion d'un agent de codage

Le serveur ds4 expose des endpoints compatibles à la fois avec OpenAI et Anthropic, de sorte que la plupart des agents de codage peuvent s'y connecter directement. Par exemple, pour l'ajouter à l'agent de codage `pi`, ajoutez le bloc suivant à `~/.pi/agent/models.json` :

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

> **Astuce** : Si votre agent de codage ou votre interface Web s'exécute sur une machine différente de la plateforme Halo, vous devrez rediriger le port 8000 via SSH :
> ```bash
> ssh -L 0.0.0.0:8000:localhost:8000 <halo-host-ip>
> ```
## Prochaines étapes

- **Clustering multi-nœuds** : Si vous disposez de deux appareils Halo, ds4 permet de distribuer le modèle Q4 (~153 Go) sur les deux machines via le parallélisme de pipeline. Consultez la [documentation ds4-toolbox](https://github.com/kyuz0/strix-halo-ds4-toolbox#distributed-inference-pipeline-parallelism) pour les instructions de configuration.
- **Décodage spéculatif (MTP)** : Téléchargez les poids MTP (~3,6 Go) et passez `--mtp` au serveur pour une vitesse de génération plus rapide.
- **Déchargement du cache KV sur disque** : Pour les workflows d'agents de codage, activez `--kv-disk-dir` afin que les invites système répétées soient restaurées depuis le SSD plutôt que d'être recalculées à chaque fois.

Pour plus d'informations, consultez le [dépôt ds4](https://github.com/antirez/ds4) et la [boîte à outils ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox).