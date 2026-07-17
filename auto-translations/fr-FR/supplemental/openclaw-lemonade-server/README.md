<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->
# Exécuter OpenClaw avec Lemonade Server comme backend

## Vue d'ensemble

[**OpenClaw**](https://openclaw.ai/) est un agent IA autonome capable d'écrire et d'exécuter du code, de gérer des fichiers et de traiter des tâches complexes en plusieurs étapes en votre nom. Contrairement à un assistant de chat qui se contente de répondre aux questions, OpenClaw effectue de véritables actions sur votre système, ce qui signifie qu'il a besoin d'un backend IA rapide et performant capable de suivre le rythme d'une boucle d'agent exigeante.

[**Lemonade Server**](https://lemonade-server.ai/) est ce backend. Il s'agit d'un serveur d'inférence local open source qui exécute des modèles GenAI directement sur votre matériel et les expose via l'API OpenAI standard du secteur.

Ensemble, ils forment une pile d'agent IA entièrement locale : Lemonade gère l'inférence du modèle, et OpenClaw fournit la boucle d'agent qui transforme les sorties du modèle en actions réelles.

> **Avant de continuer :** OpenClaw est un agent IA hautement autonome. Donner à un agent IA l'accès à votre système peut entraîner des résultats imprévisibles ou non souhaités. Ne continuez que si vous comprenez les risques et êtes à l'aise avec un logiciel autonome agissant en votre nom.

---

## Ce que vous apprendrez

À la fin de ce guide, vous serez en mesure de :

- En apprendre davantage sur **Lemonade Server**
- **Installer OpenClaw** et **le pointer vers Lemonade Server** comme backend IA.
- **Démarrer la passerelle OpenClaw** et confirmer que votre agent est prêt à fonctionner.
- **Connecter un canal de communication** (Discord ou Telegram) pour pouvoir discuter avec votre agent depuis n'importe quel appareil.

---

## Configurer la configuration mémoire

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Vérifier les mises à jour logicielles

<!-- @require:software-update -->
<!-- @device:end -->

## Installation des prérequis logiciels

<!-- @os:linux -->
- Un PC exécutant **Ubuntu 24.04+** ou une distribution Linux compatible basée sur Debian avec `apt-get`
- Au moins **12 Go de RAM** (64 Go+ recommandés pour les modèles plus grands)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (Optionnel, pour isoler OpenClaw dans un bac à sable)

- **~10–30 Go d'espace disque libre** pour les poids du modèle
<!-- @os:end -->
<!-- @os:windows -->
- Un PC exécutant **Windows 10/11**
- Au moins **12 Go de RAM** (64 Go+ recommandés pour les modèles plus grands)
- **~10–30 Go d'espace disque libre** pour les poids du modèle
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (Optionnel, pour isoler OpenClaw dans un bac à sable)
<!-- @os:end -->

<!-- @require:lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Télécharger et charger le modèle recommandé

Le modèle recommandé pour ce guide est **Qwen3.6-35B-A3B-GGUF** de Unsloth, un modèle MoE performant avec une fenêtre de contexte de 263k tokens, bien adapté aux charges de travail d'agent. Ce modèle utilise la quantification UD-Q4_K_XL. Téléchargez-le maintenant :

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Chargez-le ensuite avec une grande fenêtre de contexte et enregistrez ce paramètre pour les exécutions futures :

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

Le modèle a une longueur de contexte par défaut de 262 144 tokens. Si vous rencontrez des erreurs de mémoire insuffisante (OOM), envisagez de réduire la fenêtre de contexte. Cependant, étant donné que Qwen3.6 exploite le contexte étendu pour les tâches complexes, nous conseillons de maintenir une longueur de contexte d'au moins 128K tokens pour préserver les capacités de réflexion.

> **Conseil : Désactiver la réflexion pour des réponses d'agent plus rapides :** Qwen3.6-35B-A3B s'exécute en mode réflexion par défaut, ce qui ajoute une latence avant chaque réponse. Pour les boucles d'agent, cette surcharge s'accumule rapidement. Le dépôt [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) fournit une configuration prête à l'emploi qui désactive la réflexion. Pour l'utiliser, téléchargez le fichier et importez-le :
>
> ```bash
> curl -LO https://raw.githubusercontent.com/lemonade-sdk/recipes/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json
> lemonade import Qwen3.6-35B-A3B-NoThinking.json
> ```

---

<!-- @os:windows -->
<!-- @test:id=lemonade-chat-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$modelsJson = $null
for ($i = 0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}

if (-not $modelsJson) {throw "Lemonade server not ready on http://127.0.0.1:13305"}
Write-Host "OK: Lemonade server is responding"

$parsed = $modelsJson | ConvertFrom-Json
$entry = $parsed.data | Where-Object { $_.id -eq "${openclaw_model}" } | Select-Object -First 1

if (-not $entry) {throw "Model ${openclaw_model} is not present in Lemonade /api/v1/models."}
if (-not $entry.downloaded) {throw "Model ${openclaw_model} is present but not downloaded in Lemonade. Please download it before running CI."}
Write-Host "OK: ${openclaw_model} model is downloaded in Lemonade"

if ($entry.recipe_options.ctx_size -ne 262144) {
  throw "Model ${openclaw_model} is not saved with ctx_size=262144. Run: lemonade load ${openclaw_model} --ctx-size 262144 --save-options"
}
Write-Host "OK: ${openclaw_model} is saved with ctx_size=262144"

$body = @{
  model = "${openclaw_model}"
  messages = @(
    @{
      role = "user"
      content = "Reply with exactly: OK"
    }
  )
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "openclaw-lemonade-chat-body.json"
[System.IO.File]::WriteAllText($tmpBody, $body, [System.Text.UTF8Encoding]::new($false))

try {
  $out = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpBody"
  if (-not $out) {throw "Empty response from Lemonade chat/completions"}
  Write-Host "OK: Lemonade chat/completions returned a response"
}
finally {
  Remove-Item $tmpBody -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-chat-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail

models_json=""
for i in $(seq 1 120); do
  models_json="$(curl -s --max-time 2 http://127.0.0.1:13305/api/v1/models || true)"
  if [ -n "$models_json" ]; then
    break
  fi
  sleep 1
done

if [ -z "$models_json" ]; then
  echo "Lemonade server not ready on http://127.0.0.1:13305"
  exit 1
fi
echo "OK: Lemonade server is responding"

export MODELS_JSON="$models_json"

python3 - <<'PY'
import json
import os
import sys

data = json.loads(os.environ["MODELS_JSON"])
model_id = "${openclaw_model}"

entry = None
for item in data.get("data", []):
    if item.get("id") == model_id:
        entry = item
        break

if entry is None:
    print(f"Model {model_id} is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print(f"Model {model_id} is present but not downloaded in Lemonade. Please download it before running CI.")
    sys.exit(1)

print(f"OK: {model_id} model is downloaded in Lemonade")

ctx_size = entry.get("recipe_options", {}).get("ctx_size")
if ctx_size != 262144:
    print(f"Model {model_id} is not saved with ctx_size=262144. Run: lemonade load {model_id} --ctx-size 262144 --save-options")
    sys.exit(1)
print(f"OK: {model_id} is saved with ctx_size=262144")
PY

body='{
  "model": "${openclaw_model}",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 32
}'

out="$(curl -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body")"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi

echo "OK: Lemonade chat/completions returned a response"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->

## Configurer WSL

Nous exécutons OpenClaw dans WSL (recommandé) et le connectons à Lemonade s'exécutant nativement sur Windows. Cela vous offre un environnement shell Linux pour OpenClaw tout en conservant l'accélération GPU de Lemonade côté Windows.

### Installer WSL et Ubuntu

Ouvrez PowerShell en tant qu'administrateur et installez le noyau WSL :

```powershell
wsl --install --no-distribution
```

Puis installez Ubuntu :

```powershell
wsl --install -d Ubuntu-24.04
```

### Activer systemd dans WSL

Exécutez ceci dans le terminal Ubuntu :

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

Redémarrez WSL :

```powershell
wsl --shutdown
wsl
```

### Relier Lemonade de Windows vers WSL

WSL2 s'exécute dans un réseau virtuel. Lemonade sur Windows se lie à `127.0.0.1`, que WSL ne peut pas atteindre directement. Un proxy de port Windows transfère le trafic de l'adresse IP de la passerelle WSL vers localhost Windows.

**Trouvez l'adresse IP de votre passerelle WSL** (exécutez dans WSL) :

```bash
ip route show default | awk '{print $3}' | head -1
```

**Ajoutez le proxy de port** (exécutez dans PowerShell en tant qu'administrateur, en remplaçant `<WSL-Gateway-IP>` par l'adresse IP de votre passerelle WSL) :

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**Ajoutez une règle de pare-feu** (même PowerShell élevé) :

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Vérifiez depuis WSL** :

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Si vous avez déjà chargé le modèle Qwen3.6-35B-A3B-GGUF à l'étape précédente, vous devriez voir une sortie JSON comme celle-ci :

```json
{
  "data": [
    {
      "checkpoint": "unsloth/Qwen3.6-35B-A3B-GGUF:UD-Q4_K_XL",
      "checkpoints": {
        "main": "unsloth/Qwen3.6-35B-A3B-GGUF:UD-Q4_K_XL"
      },
      "mmproj": "unsloth/Qwen3.6-35B-A3B-GGUF:mmproj-F16.gguf",
      ....
    }
  ],
  "object": "list"
}
```

> La règle `netsh portproxy` survit aux redémarrages, mais l'adresse IP de la passerelle WSL peut changer après `wsl --shutdown`. Si Lemonade devient inaccessible depuis WSL après un redémarrage, obtenez l'adresse IP de la passerelle mise à jour et mettez à jour le proxy avec cette nouvelle adresse IP.

<!-- @test:id=wsl-lemonade-bridge-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
WINDOWS_HOST="$(ip route show default | awk '{print $3}' | head -1)"

if [ -z "$WINDOWS_HOST" ]; then
  echo "Could not determine WSL gateway IP"
  exit 1
fi

echo "WSL gateway IP: $WINDOWS_HOST"

models_json="$(curl -fsS --max-time 5 "http://$WINDOWS_HOST:13305/api/v1/models")"

if [ -z "$models_json" ]; then
  echo "Could not reach Lemonade from WSL at http://$WINDOWS_HOST:13305/api/v1/models"
  echo "Check the Windows netsh portproxy and firewall rule from the README."
  exit 1
fi

echo "$models_json" | python3 -m json.tool >/dev/null
echo "OK: WSL can reach native Windows Lemonade through the bridge"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "wsl-lemonade-bridge-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "WSL Lemonade bridge test failed"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 

---
<!-- @os:end -->

## Installer et configurer OpenClaw

### Installer OpenClaw
<!-- @os:windows -->
> Exécutez les commandes de cette section dans votre **terminal WSL**.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

L'indicateur `--no-onboard` ignore l'assistant de configuration interactif ; vous configurerez le backend du modèle manuellement à l'étape suivante, ce qui vous donne un contrôle précis sur le modèle et le serveur utilisés.

Ouvrez un nouveau terminal et confirmez l'installation :

```bash
openclaw --version
```

> **Conseil :** Si vous voyez `command not found` après l'installation, ajoutez le répertoire bin global de npm à votre PATH :
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Pour rendre cela permanent, ajoutez la ligne ci-dessus à votre fichier `~/.bashrc` ou `~/.zshrc`.

<!-- @os:linux -->
<!-- @test:id=openclaw-version-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
echo "HOME=$HOME"
echo "PATH=$PATH"
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
node -v
npm -v
openclaw --version
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openclaw-version-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
echo "HOME=$HOME"
echo "PATH=$PATH"
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
node -v
npm -v
openclaw --version
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-version-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "OpenClaw version check failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->


### Configurer OpenClaw pour utiliser Lemonade

Exécutez l'intégration non interactive d'OpenClaw.
<!-- @os:linux -->
```bash
openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://127.0.0.1:13305/api/v1" \
  --custom-model-id "Qwen3.6-35B-A3B-GGUF" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk
```
<!-- @os:end -->
<!-- @os:windows -->
```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://$WINDOWS_HOST:13305/api/v1" \
  --custom-model-id "Qwen3.6-35B-A3B-GGUF" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk
```
<!-- @os:end -->

Cette commande écrit la configuration d'OpenClaw dans `~/.openclaw/openclaw.json`.

> **Dimensionnement de la fenêtre de contexte OpenClaw :** La compaction d'OpenClaw se déclenche lorsque `contextTokens > contextWindow − reserveTokens`. La valeur par défaut de `reserveTokensFloor` est de 20 000 tokens, un plancher qui remplace `reserveTokens` lorsqu'il est inférieur, de sorte que tout contexte de modèle inférieur à ~37k déclenchera une boucle de compaction infinie. Définissez une réserve faible et désactivez le plancher une fois dans votre configuration, et cela s'applique à chaque modèle, sans réglage par modèle :
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` est un *plancher* (garde minimum), pas la réserve elle-même ; définir uniquement le plancher n'a aucun effet. `reserveTokensFloor: 0` désactive la garde afin que la valeur inférieure de `reserveTokens` soit acceptée.
>
> **Quand appliquer ceci :** Utilisez cette configuration si la fenêtre de contexte effective de votre modèle est inférieure à ~37k, soit parce que le modèle est petit (par exemple 8k, 16k, 32k), soit parce que vous l'avez intentionnellement limitée à une valeur inférieure (par exemple en chargeant un modèle 128k mais en définissant le contexte à 16k dans Lemonade). Sans cela, OpenClaw entre dans une boucle de compaction infinie au démarrage.
>
> **Modèles à grand contexte à plein contexte :** Vous pouvez ignorer cela entièrement. Les valeurs par défaut fonctionnent bien, la compaction se déclenchera bien avant que la fenêtre ne soit pleine et le modèle dispose d'amplement d'espace pour générer de longues réponses. Si vous l'appliquez quand même, sachez que `reserveTokens: 4096` limite la longueur des réponses à ~4k tokens, ce qui peut interrompre la génération de longs fichiers ou de plans détaillés.
>
> **Où ajouter ceci :** Placez le bloc `compaction` dans `agents.defaults` dans votre `openclaw.json` (généralement à `~/.openclaw/openclaw.json`) :
>
> ```json
> {
>   "agents": {
>     "defaults": {
>       "workspace": "/home/<you>/.openclaw/workspace",
>       "model": {
>         "primary": "lemonade/<your-model-id>"
>       },
>       "compaction": {
>         "reserveTokens": 4096,
>         "reserveTokensFloor": 0
>       }
>     }
>   }
> }
> ```
>
> Le reste de votre configuration (passerelle, canaux, modèles, etc.) reste inchangé ; seule la clé `compaction` doit être ajoutée.

### (Recommandé) Activer l'isolation Docker

OpenClaw peut acheminer toutes les opérations de fichiers et de code de l'agent via un conteneur Docker isolé plutôt que de les exécuter directement sur votre hôte. Cela limite l'impact de toute action non intentionnelle au bac à sable, laissant intacts le système de fichiers et le réseau de votre hôte.

Construisez l'image du bac à sable une fois (Docker doit être installé) :

```bash
docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE
```

<!-- @os:linux -->
<!-- @test:id=openclaw-sandbox-image-linux timeout=1800 hidden=True -->
```bash
set -euo pipefail

docker version

docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

echo "OK: OpenClaw sandbox Docker image is available"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openclaw-sandbox-image-windows timeout=1800 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="/mnt/wsl/docker-desktop/cli-tools/usr/bin:$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

docker_config="$(mktemp -d)"
cleanup() {
  rm -rf "$docker_config"
}
trap cleanup EXIT
export DOCKER_CONFIG="$docker_config"
printf '{ "auths": {} }\n' > "$DOCKER_CONFIG/config.json"

docker version

docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

echo "OK: OpenClaw sandbox Docker image is available inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-sandbox-image-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "OpenClaw sandbox image build failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

Exécutez ceci pour ajouter la clé `sandbox` dans le bloc `agents.defaults` existant dans `~/.openclaw/openclaw.json` :

```bash
cat > sandbox.patch.json5 <<JSON5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none"
      }
    }
  }
}
JSON5
openclaw config patch --file ./sandbox.patch.json5
```

Les conteneurs du bac à sable n'ont **pas d'accès réseau** par défaut. Consultez la [référence d'isolation](https://docs.openclaw.ai/gateway/sandboxing) pour les montages de liaison et les remplacements réseau.

> #### Dépannage : Permission Docker refusée
> 
> Si vous obtenez « permission denied » lors de l'exécution de commandes Docker :
> 
> **Étape 1 : Ajoutez votre utilisateur au groupe docker**
> 
> ```bash
> sudo groupadd docker                    # Créer le groupe si nécessaire
> sudo usermod -aG docker $USER           # Vous ajouter au groupe
> newgrp docker                           # Activer le changement
> docker run hello-world                  # Tester
> ```
> 
> **Étape 2 : Si l'erreur persiste, appliquez le correctif permanent**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> Puis **redémarrez** votre système.
> 
> **Correctif temporaire rapide** (se réinitialise après le redémarrage) :
> ```bash
> sudo chmod 666 /var/run/docker.sock
> ```

<!-- @os:linux -->
<!-- @test:id=openclaw-onboard-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

mkdir -p "$HOME/.openclaw"
rm -f "$HOME/.openclaw/openclaw.json"

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://127.0.0.1:13305/api/v1" \
  --custom-model-id "${openclaw_model}" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk

config="$HOME/.openclaw/openclaw.json"
test -f "$config"

grep -q "lemonade" "$config"
grep -q "${openclaw_model}" "$config"
grep -q "127.0.0.1:13305" "$config"

echo "OK: OpenClaw onboarding wrote Lemonade configuration"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=openclaw-sandbox-config-linux timeout=120 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
config="$HOME/.openclaw/openclaw.json"

if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

cat > sandbox.patch.json5 <<JSON5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none"
      }
    }
  }
}
JSON5

openclaw config patch --file ./sandbox.patch.json5

grep -q '"sandbox"' "$config"
grep -Eq '"mode"[[:space:]]*:[[:space:]]*"non-main"' "$config"
grep -Eq '"scope"[[:space:]]*:[[:space:]]*"session"' "$config"
grep -Eq '"workspaceAccess"[[:space:]]*:[[:space:]]*"none"' "$config"

echo "OK: OpenClaw sandbox configuration was written"
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=openclaw-onboard-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

mkdir -p "$HOME/.openclaw"
rm -f "$HOME/.openclaw/openclaw.json"

WINDOWS_HOST="$(ip route show default | awk '{print $3}' | head -1)"

if [ -z "$WINDOWS_HOST" ]; then
  echo "Could not determine WSL gateway IP"
  exit 1
fi

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://$WINDOWS_HOST:13305/api/v1" \
  --custom-model-id "${openclaw_model}" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk

config="$HOME/.openclaw/openclaw.json"
test -f "$config"

grep -q "lemonade" "$config"
grep -q "${openclaw_model}" "$config"
grep -q "$WINDOWS_HOST:13305" "$config"

echo "OK: OpenClaw onboarding wrote Lemonade configuration inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-onboard-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "OpenClaw onboarding failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=openclaw-sandbox-config-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="/mnt/wsl/docker-desktop/cli-tools/usr/bin:$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

docker_config="$(mktemp -d)"
cleanup() {
  rm -rf "$docker_config"
}
trap cleanup EXIT
export DOCKER_CONFIG="$docker_config"
printf '{ "auths": {} }\n' > "$DOCKER_CONFIG/config.json"

config="$HOME/.openclaw/openclaw.json"

if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

cat > sandbox.patch.json5 <<JSON5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none"
      }
    }
  }
}
JSON5

openclaw config patch --file ./sandbox.patch.json5

grep -q '"sandbox"' "$config"
grep -Eq '"mode"[[:space:]]*:[[:space:]]*"non-main"' "$config"
grep -Eq '"scope"[[:space:]]*:[[:space:]]*"session"' "$config"
grep -Eq '"workspaceAccess"[[:space:]]*:[[:space:]]*"none"' "$config"

echo "OK: OpenClaw sandbox configuration was written inside WSL"
'@

$script = $script -replace "`r`n", "`n"
$tmp = Join-Path $env:TEMP "openclaw-sandbox-config-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "OpenClaw sandbox config patch failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->

### Démarrer la passerelle OpenClaw

La passerelle est le processus OpenClaw qui gère la boucle d'agent et sert le tableau de bord :

```bash
openclaw gateway run --bind loopback --port 18789
```

<!-- @os:linux -->
<!-- @test:id=openclaw-gateway-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.openclaw/openclaw.json"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi
log="/tmp/openclaw-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

openclaw gateway run --bind loopback --port 18789 >"$log" 2>&1 &
gateway_pid=$!

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:18789/ || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "OpenClaw gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi

echo "OK: OpenClaw gateway is reachable"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openclaw-gateway-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.openclaw/openclaw.json"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi
log="/tmp/openclaw-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

openclaw gateway run --bind loopback --port 18789 >"$log" 2>&1 &
gateway_pid=$!

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:18789/ || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "OpenClaw gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi

echo "OK: OpenClaw gateway is reachable inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-gateway-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "OpenClaw gateway test failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->

Pour ouvrir le tableau de bord, exécutez ceci dans un second terminal pendant que la passerelle est toujours en cours d'exécution :

```bash
openclaw dashboard
```

Étant donné que la passerelle se lie à la boucle locale, le tableau de bord s'authentifie automatiquement lorsqu'il est ouvert depuis la même machine — aucune saisie de token ni approbation d'appareil n'est nécessaire pour l'accès local. Vous devriez voir le tableau de bord OpenClaw avec votre modèle Lemonade répertorié comme backend actif.

> Si vous avez activé l'isolation, vous pouvez la vérifier en demandant à l'agent d'exécuter `run hostname` depuis le tableau de bord. Si vous voyez un identifiant de conteneur court au lieu du nom d'hôte de votre machine, le bac à sable fonctionne.

**Félicitations, vous avez construit une pile d'agent IA entièrement locale de zéro.**

> **Besoin du token de la passerelle ?** Exécutez `openclaw dashboard --no-open` pour afficher l'URL du tableau de bord avec le token intégré (il tente également de le copier dans votre presse-papiers). Alternativement, le token se trouve à `gateway.auth.token` dans `~/.openclaw/openclaw.json`.
>
> **Approuver un appareil distant :** Lorsque vous ouvrez le tableau de bord depuis une seconde machine ou un téléphone, le navigateur affiche un identifiant de demande. Sur la machine exécutant la passerelle, exécutez :
> ```bash
> openclaw devices approve <requestId>
> ```
> Cela n'est nécessaire que pour les appareils distants ou secondaires — l'accès en boucle locale depuis la même machine s'authentifie automatiquement.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Optionnel : Connecter un canal de communication

Une fois la passerelle en cours d'exécution, vous pouvez atteindre votre agent local depuis n'importe quel appareil. Choisissez l'option qui correspond à votre configuration. OpenClaw prend en charge [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram) et d'autres canaux — consultez la liste complète sur [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Option A : Discord

Discord nécessite un serveur sur lequel **vous avez un accès administrateur** pour ajouter un bot. Si vous partagez des serveurs mais n'en possédez pas, utilisez l'Option B (Telegram) à la place.

#### Créer un compte et un serveur Discord

Si vous n'avez pas de compte Discord, inscrivez-vous sur [discord.com](https://discord.com). Vous avez également besoin d'un serveur dont vous êtes administrateur — créez-en un en cliquant sur l'icône **+** dans la barre latérale Discord et en sélectionnant **Créer le mien**. Un serveur privé convient parfaitement.

#### Créer une application et un bot Discord

1. Accédez au [Portail des développeurs Discord](https://discord.com/developers/applications) et cliquez sur **Nouvelle application**. Donnez-lui un nom (par exemple « openclaw-bot »).
2. Dans la barre latérale, cliquez sur **Bot**. Définissez un nom d'utilisateur pour le bot.
3. Toujours sur la page Bot, faites défiler jusqu'à **Privileged Gateway Intents** et activez :
   - **Message Content Intent** (requis)
   - **Server Members Intent** (recommandé)
4. Faites défiler vers le haut et cliquez sur **Reset Token** pour générer votre token de bot. Copiez-le.

#### Ajouter le bot à votre serveur

1. Dans la barre latérale, cliquez sur **OAuth2/ URL Generator**.
2. Sous **Scopes**, activez `bot` et `applications.commands`.
3. Sous **Bot Permissions**, activez : View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Copiez l'URL générée, collez-la dans votre navigateur, sélectionnez votre serveur et confirmez. Le bot devrait maintenant apparaître dans la liste des membres de votre serveur.

#### Collecter vos identifiants

Activez le mode développeur dans Discord (**Paramètres utilisateur/ Avancé/ Mode développeur**), puis :
- Faites un clic droit sur l'icône de votre serveur : **Copier l'identifiant du serveur**
- Faites un clic droit sur votre propre avatar : **Copier l'identifiant utilisateur**

#### Autoriser les messages directs des membres du serveur

Faites un clic droit sur l'icône de votre serveur/ **Paramètres de confidentialité**/ activez **Messages directs**. Cela permet au bot de vous envoyer des messages directs, ce qui est requis pour l'étape d'appairage.

#### Configurer OpenClaw pour Discord

Stockez votre token de bot comme variable d'environnement, puis créez un fichier de correctif unique qui active Discord, référence le token et autorise votre serveur. Remplacez `<server_id>` et `<user_id>` par les identifiants collectés ci-dessus.

```bash
export DISCORD_BOT_TOKEN="YOUR_BOT_TOKEN"

cat > discord.patch.json5 <<JSON5
{
  channels: {
    discord: {
      enabled: true,
      token: { source: "env", provider: "default", id: "DISCORD_BOT_TOKEN" },
      dmPolicy: "pairing",
      groupPolicy: "allowlist",
      guilds: {
        "<server_id>": {
          requireMention: false,
          users: ["<user_id>"],
        },
      },
    },
  },
}
JSON5
openclaw config patch --file ./discord.patch.json5
```

> **Ne comptez pas sur l'agent pour configurer cela.** Lorsque l'isolation est activée, l'agent ne peut pas écrire dans `~/.openclaw/openclaw.json` depuis l'intérieur du bac à sable — utilisez les commandes CLI ci-dessus sur l'hôte à la place.

Redémarrez la passerelle pour qu'elle prenne en compte la nouvelle configuration du canal :

```bash
openclaw gateway run --bind loopback --port 18789
```

Vous devriez voir `logged in to discord as <bot-name>` dans la sortie de la passerelle en quelques secondes.

#### Appairer votre compte Discord

Envoyez un message direct au bot dans Discord. Il répondra avec un court code d'appairage.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Approuvez-le sur la machine exécutant OpenClaw :
```bash
openclaw pairing approve discord <CODE>
```

> Les codes d'appairage expirent après une heure.

Vous pouvez maintenant discuter avec votre agent directement depuis Discord et déléguer des tâches à votre matériel local.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Option B : Telegram

Telegram est plus simple que Discord pour la plupart des utilisateurs — il ne nécessite ni serveur ni accès administrateur.

#### Créer un bot Telegram

1. Ouvrez Telegram et envoyez un message à **@BotFather**.
2. Envoyez `/newbot` et suivez les instructions. Sauvegardez le token de bot qu'il vous donne.

#### Configurer OpenClaw pour Telegram

Stockez le token comme variable d'environnement :

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Ajoutez la configuration du canal dans `~/.openclaw/openclaw.json` (ou appliquez-la via le tableau de bord) :

```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "botToken": "YOUR_BOT_TOKEN",
      "dmPolicy": "pairing"
    }
  }
}
```

Redémarrez la passerelle, puis envoyez n'importe quel message à votre bot dans Telegram. Approuvez l'appairage :

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Les codes d'appairage expirent après une heure. Vous pouvez maintenant discuter avec votre agent via message direct Telegram.

---

## Prochaines étapes

Maintenant que votre agent peut recevoir des commandes depuis votre téléphone et agir sur votre machine locale, voici trois directions qui méritent d'être explorées :

1. **Résumé du marché boursier** : Planifiez OpenClaw pour récupérer des données depuis des API financières à intervalle fixe, résumer les mouvements de la journée avec votre modèle local, et envoyer un résumé sur votre téléphone chaque matin via le canal de votre choix.

2. **Moniteur d'affinage** : Lancez une tâche d'entraînement à distance via Telegram ou Discord, puis demandez à l'agent de surveiller le journal d'entraînement et de rapporter périodiquement les valeurs de perte, l'utilisation du GPU et l'utilisation du disque sur votre téléphone. Si l'exécution se bloque ou que la VRAM augmente brusquement, vous en êtes informé immédiatement sans avoir besoin d'être devant la machine.

3. **IOT avec un VLM local** : Pointez une caméra vers votre porte d'entrée, exécutez un modèle de vision sur Lemonade, et demandez à OpenClaw d'analyser les images à la demande ou sur déclencheur. Posez la question « des colis sont-ils arrivés aujourd'hui ? » depuis votre téléphone et obtenez une réponse directe depuis votre propre matériel.