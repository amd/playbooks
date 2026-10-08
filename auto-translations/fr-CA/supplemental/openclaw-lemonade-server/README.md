<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traduction automatique.** Cette page a été traduite automatiquement de l'anglais et n'a pas été révisée par un humain. Elle peut contenir des erreurs, et certaines instructions, commandes, options de téléchargement, disponibilités de produits ou autres contenus peuvent varier selon la langue ou la région. En cas d'incompatibilité ou de divergence, la version originale anglaise du playbook fait foi.
<!-- auto-translated-disclaimer:end -->

# Exécuter OpenClaw avec Lemonade Server comme backend

## Présentation

[**OpenClaw**](https://openclaw.ai/) est un agent d'IA autonome capable d'écrire et d'exécuter du code, de gérer des fichiers et d'accomplir des tâches complexes à plusieurs étapes en votre nom. Contrairement à un assistant de clavardage qui se contente de répondre à des questions, OpenClaw entreprend des actions réelles sur votre système, ce qui signifie qu'il a besoin d'un backend d'IA rapide et performant, capable de suivre le rythme d'une boucle d'agent exigeante.

[**Lemonade Server**](https://lemonade-server.ai/) est ce backend. Il s'agit d'un serveur d'inférence local à source ouverte qui exécute des modèles GenAI directement sur votre matériel et les expose au moyen de l'API standard de l'industrie OpenAI.

Ensemble, ils forment une pile d'agent d'IA entièrement locale : Lemonade s'occupe de l'inférence des modèles, et OpenClaw fournit la boucle d'agent qui transforme les sorties du modèle en actions réelles.

> **Avant de continuer :** OpenClaw est un agent d'IA hautement autonome. Le fait de donner à tout agent d'IA l'accès à votre système peut entraîner des résultats imprévisibles ou non voulus. Poursuivez seulement si vous comprenez les risques et si vous êtes à l'aise avec l'idée qu'un logiciel autonome agisse en votre nom.

---

## Ce que vous apprendrez

À la fin de ce guide pratique, vous serez en mesure de :

- Découvrir **Lemonade Server**
- **Installer OpenClaw** et le **configurer pour qu'il utilise Lemonade Server** comme backend d'IA.
- **Démarrer la passerelle OpenClaw** et confirmer que votre agent est prêt à travailler.
- **Connecter un canal de communication** (Discord ou Telegram) afin de pouvoir discuter avec votre agent depuis n'importe quel appareil.

---

<!-- @device:halo_box,halo,stx,krk -->
## Définir la configuration de la mémoire

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Vérifier les mises à jour logicielles

<!-- @require:software-update -->
<!-- @device:end -->

## Installation des conditions préalables logicielles

<!-- @os:linux -->
- Un PC exécutant **Ubuntu 24.04+** ou une distribution Linux compatible basée sur Debian avec `apt-get`
- Au moins **12 Go de RAM** (64 Go ou plus recommandés pour les modèles plus volumineux)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (facultatif, pour l'exécution d'OpenClaw en bac à sable)
- **Environ 10 à 30 Go d'espace disque libre** pour les poids du modèle
<!-- @os:end -->

<!-- @os:windows -->
- Un PC exécutant **Windows 10/11**
- Au moins **12 Go de RAM** (64 Go ou plus recommandés pour les modèles plus volumineux)
- **Environ 10 à 30 Go d'espace disque libre** pour les poids du modèle
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (facultatif, pour l'exécution d'OpenClaw en bac à sable)
<!-- @os:end -->

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade -->
<!-- @prereq:nodejs,openclaw,lemonade-models-qwen3-35b-a3b,lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Télécharger et charger le modèle recommandé

Le modèle recommandé pour ce guide pratique est **Qwen3.6-35B-A3B-GGUF** d'Unsloth, un modèle MoE performant doté d'une fenêtre contextuelle de 263 k jetons, bien adapté aux charges de travail d'agent. Ce modèle utilise une quantification UD-Q4_K_XL. Téléchargez-le maintenant :

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Chargez-le ensuite avec une grande fenêtre contextuelle et enregistrez ce paramètre pour les exécutions futures :

<!-- @require:lemonade-ready -->
<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

Le modèle a une longueur de contexte par défaut de 262 144 jetons. Si vous rencontrez des erreurs de dépassement de mémoire (OOM), envisagez de réduire la fenêtre contextuelle. Cependant, étant donné que Qwen3.6 tire parti d'un contexte étendu pour les tâches complexes, nous recommandons de maintenir une longueur de contexte d'au moins 128 K jetons afin de préserver les capacités de réflexion.

> **Astuce : Désactiver le mode réflexion pour des réponses d'agent plus rapides :** Qwen3.6-35B-A3B s'exécute en mode réflexion par défaut, ce qui ajoute de la latence avant chaque réponse. Pour les boucles d'agent, cette surcharge s'accumule rapidement. Le dépôt [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) fournit une configuration prête à l'emploi qui désactive le mode réflexion. Pour l'utiliser, téléchargez le fichier et importez-le :
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

Nous exécutons OpenClaw dans WSL (recommandé) et le connectons à Lemonade, qui s'exécute nativement sur Windows. Cela vous donne un environnement de shell Linux pour OpenClaw tout en conservant l'accélération GPU de Lemonade du côté Windows.

### Installer WSL et Ubuntu

Ouvrez PowerShell en tant qu'administrateur et installez le noyau WSL :

```powershell
wsl --install --no-distribution
```

Installez ensuite Ubuntu :

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

Quittez WSL et redémarrez-le :

```powershell
exit
wsl --shutdown
wsl
```

### Relier Lemonade de Windows vers WSL

WSL2 s'exécute dans un réseau virtuel. Lemonade sur Windows se lie à `127.0.0.1`, que WSL ne peut pas atteindre directement. Un proxy de port Windows redirige le trafic de l'adresse IP de la passerelle WSL vers l'hôte local Windows.

**Trouvez l'adresse IP de la passerelle WSL** (exécutez ceci dans WSL) :

```bash
ip route show default | awk '{print $3}' | head -1
```

**Ajoutez le proxy de port** (exécutez ceci dans PowerShell en tant qu'administrateur, en remplaçant `<WSL-Gateway-IP>` par l'adresse IP de votre passerelle WSL) :

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```
> Remarque : Si vous rencontrez une erreur `netsh: command not found`, essayez d'utiliser plutôt le nom explicite de l'exécutable `netsh.exe`

**Ajoutez une règle de pare-feu** (même fenêtre PowerShell élevée) :

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Vérifiez à partir de WSL** :

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Si vous avez déjà chargé le modèle Qwen3.6-35B-A3B-GGUF à l'étape précédente, vous devriez voir une sortie JSON semblable à celle-ci :

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

#### Maintenir le pont fonctionnel après un redémarrage

La règle `netsh portproxy` survit aux redémarrages, mais l'adresse IP de la passerelle WSL peut changer après un `wsl --shutdown` ou un redémarrage. Dans ce cas, le proxy continue de pointer vers l'ancienne adresse IP et Lemonade devient inaccessible depuis WSL. Si cela se produit, utilisez l'une des options ci-dessous.

**Option 1 (recommandée) — Réparer le pont automatiquement.** Pour éviter d'avoir à le faire manuellement à chaque fois, utilisez une tâche planifiée qui vérifie le pont à chaque démarrage et à chaque connexion, et ne le reconstruit que lorsque l'adresse IP de la passerelle a changé. Consultez le [guide de réparation automatique du pont WSL de Lemonade](assets/RepairLemonadeWslBridge.md).


**Option 2 — Réparer le pont manuellement.** D'abord, obtenez l'adresse IP actuelle de la passerelle WSL en exécutant ceci dans WSL :

```bash
ip route show default | awk '{print $3}' | head -1
```

Copiez cette valeur; vous l'utiliserez à la place de `<new-WSL-Gateway-IP>` ci-dessous.

Ensuite, dans une invite **PowerShell élevée** (exécutée en tant qu'administrateur), listez les règles existantes, supprimez uniquement la règle Lemonade obsolète, puis ajoutez-en une nouvelle avec l'adresse IP actuelle :

```powershell
netsh interface portproxy show all
netsh interface portproxy delete v4tov4 listenaddress=<old-WSL-Gateway-IP> listenport=13305
netsh interface portproxy add v4tov4 listenaddress=<new-WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

Dans la sortie de `show all`, la règle Lemonade obsolète est l'entrée dont l'adresse de connexion est `127.0.0.1` sur le port `13305`; son adresse d'écoute est votre `<old-WSL-Gateway-IP>`. La suppression par cette adresse ne retire que cette règle et laisse intactes les autres règles de port-proxy sur votre machine.

La règle de pare-feu que vous avez ajoutée pendant la configuration est liée au port `13305` (et non à l'adresse IP), elle continue donc de fonctionner et n'a pas besoin d'être recréée.

> **Recommandation :** Pour éviter les problèmes de passerelle, nous recommandons fortement la configuration de terminal suivante :
> - Les **commandes Windows** doivent être exécutées dans **PowerShell**
> - Les **commandes de la distribution WSL** doivent être exécutées dans une **invite de commandes** (exécutée en tant qu'**administrateur**)

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

Le drapeau `--no-onboard` saute l'assistant de configuration interactif; vous configurerez le serveur modèle manuellement à l'étape suivante, ce qui vous donne un contrôle précis sur le modèle et le serveur utilisés.

Ouvrez un nouveau terminal et confirmez l'installation :

```bash
openclaw --version
```

> **Astuce :** Si vous voyez `command not found` après l'installation, ajoutez le répertoire bin global de npm à votre PATH :
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Pour rendre ce changement permanent, ajoutez la ligne ci-dessus à votre fichier `~/.bashrc` ou `~/.zshrc`.

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

Exécutez le processus d'intégration non interactif d'OpenClaw.
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

> **Dimensionnement de la fenêtre de contexte d'OpenClaw :** La compaction d'OpenClaw se déclenche lorsque `contextTokens > contextWindow − reserveTokens`. La valeur par défaut de `reserveTokensFloor` est de 20 000 jetons, un plancher qui remplace `reserveTokens` lorsque celui-ci est plus bas, ce qui fait que tout contexte de modèle inférieur à environ 37 000 déclenchera une boucle de compaction infinie. Définissez une réserve basse et désactivez le plancher une seule fois dans votre configuration, et cela s'appliquera à chaque modèle, sans réglage individuel nécessaire :
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` est un *plancher* (garde-fou minimal), et non la réserve elle-même; définir seulement le plancher n'a aucun effet. `reserveTokensFloor: 0` désactive le garde-fou afin que la valeur plus basse de `reserveTokens` soit acceptée.
>
> **Quand appliquer ceci :** Utilisez cette configuration si la fenêtre de contexte effective de votre modèle est inférieure à environ 37 000, soit parce que le modèle est petit (par exemple, 8k, 16k, 32k), soit parce que vous l'avez intentionnellement plafonnée à une valeur plus basse (par exemple, en chargeant un modèle de 128k mais en définissant le contexte à 16k dans Lemonade). Sans cela, OpenClaw entre dans une boucle de compaction infinie au démarrage.
>
> **Modèles à grande fenêtre de contexte à pleine capacité :** Vous pouvez entièrement ignorer cette étape. Les valeurs par défaut fonctionnent bien, la compaction se déclenchera bien avant que la fenêtre ne soit pleine et le modèle disposera d'amplement d'espace pour générer de longues réponses. Si vous l'appliquez quand même, notez que `reserveTokens: 4096` limite la longueur de la réponse à environ 4 000 jetons, ce qui peut tronquer la génération de longs fichiers ou de plans détaillés.
>
> **Où ajouter ceci :** Placez le bloc `compaction` à l'intérieur de `agents.defaults` dans votre fichier `openclaw.json` (généralement situé à `~/.openclaw/openclaw.json`) :
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
> Le reste de votre configuration (gateway, channels, models, etc.) demeure inchangé; seule la clé `compaction` doit être ajoutée.
### (Recommandé) Activer le sandboxing Docker

OpenClaw peut acheminer toutes les opérations de fichiers et de code de l'agent à travers un conteneur Docker isolé plutôt que de les exécuter directement sur votre hôte. Cela limite le rayon d'impact de toute action involontaire au bac à sable, laissant intacts le système de fichiers et le réseau de votre hôte.

Créez l'image du bac à sable une seule fois (Docker doit être installé) :

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

# Docker Desktop injects its WSL cli-tools a few seconds after the distro boots.
for i in $(seq 1 30); do
  docker version >/dev/null 2>&1 && break
  sleep 2
done
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

Exécutez ceci pour ajouter la clé `sandbox` à l'intérieur du bloc `agents.defaults` existant dans `~/.openclaw/openclaw.json` :

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

Par défaut, les conteneurs du bac à sable n'ont **aucun accès réseau**. Consultez la [référence sur le sandboxing](https://docs.openclaw.ai/gateway/sandboxing) pour connaître les montages liés et les options de réseau.

> #### Dépannage : autorisation refusée par Docker
> 
> Si vous obtenez « permission denied » lors de l'exécution de commandes Docker :
> 
> **Étape 1 : Ajoutez votre utilisateur au groupe docker**
> 
> ```bash
> sudo groupadd docker                    # Create group if needed
> sudo usermod -aG docker $USER           # Add yourself to the group
> newgrp docker                           # Activate the change
> docker run hello-world                  # Test it
> ```
> 
> **Étape 2 : Si l'erreur persiste, appliquez la correction permanente**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> Puis **redémarrez** votre système.
> 
> **Correction temporaire rapide** (réinitialisée après redémarrage) :
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

<!-- @os:linux -->
## (Recommandé) Intégration d'OpenClaw avec les services Firecrawl

[Firecrawl](https://docs.firecrawl.dev/introduction) offre un service d'exploration Web et d'extraction de contenu auto-hébergé qui permet de contourner ces difficultés et de libérer tout le potentiel de l'automatisation OpenClaw.

Dans cette configuration, OpenClaw s'exécute sous forme d'un ensemble de conteneurs Docker gérés avec Podman. Pour simplifier la gestion du cycle de vie et le démarrage automatique, nous enregistrons Firecrawl comme service `systemd` au niveau utilisateur, qui orchestre la pile Podman Compose sous-jacente. Cela permet à OpenClaw de démarrer la passerelle, de l'arrêter et de vérifier le service Firecrawl à l'aide des commandes `systemctl --user` standards, plutôt que d'interagir directement avec les conteneurs.

Pour simplifier les choses, nous avons découpé l'ensemble du processus en quatre étapes :

---

### 1. Enregistrer le service système
Accédez au répertoire de configuration systemd de l'utilisateur :
```bash
cd ~/.config/systemd/user
```
Créez et ouvrez un nouveau fichier nommé `firecrawl.service`.
```bash
nano firecrawl.service
```
Copiez-collez la configuration suivante :
```bash
[Unit]
Description=OpenClaw Firecrawl Service
After=podman.service
Requires=podman.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=%h/firecrawl

# Optional: Validate config before starting
ExecStartPre=/usr/bin/podman compose -f openclaw-compose.yaml config --quiet

# Generate token and write to .env file
ExecStartPre=/bin/bash -c 'chmod 644 %h/firecrawl/.env && echo "OPENCLAW_GATEWAY_TOKEN=$(openssl rand -hex 32)" > %h/firecrawl/.env'

# Step 1: Start containers in detached mode
ExecStart=/usr/bin/podman compose -f openclaw-compose.yaml up -d --remove-orphans

# Step 2: Wait for container to be healthy/ready
ExecStartPost=/bin/sleep 5

# Step 3: Run onboarding inside container in detached mode
ExecStartPost=/usr/bin/podman exec -d openclaw_gateway /bin/bash -c "openclaw onboard \
    --non-interactive \
    --accept-risk \
    --mode local \
    --auth-choice skip \
    --gateway-auth token \
    --gateway-token "$OPENCLAW_GATEWAY_TOKEN" "

# Stop containers when the service stops
ExecStop=/usr/bin/podman compose -f openclaw-compose.yaml down

[Install]
WantedBy=default.target
```
À ce stade, le service a été défini, mais pas encore enregistré auprès de `systemd`.
Assurez-vous que le nom du fichier correspond exactement à celui que vous avez créé ci-dessus, puis exécutez :
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
Si l'opération réussit, vous devriez voir le résultat suivant :

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 `default.target.wants/` contient des liens symboliques vers les services configurés pour démarrer automatiquement.

### 2. Configurer Firecrawl

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) convient parfaitement à ceux qui ont besoin d'un contrôle total sur leur environnement de scraping et de traitement des données, mais cela implique un effort supplémentaire de maintenance et de configuration.

Commencez par cloner le dépôt :
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
Créez un fichier `.env` dans le répertoire `/firecrawl` : 
```bash
# ===== Required ENVS ======
PORT=3002
HOST=0.0.0.0

# ===== Firecrawl =====
# FIRECRAWL_API_KEY="" # optional
```
### 3. Déployer OpenClaw avec Podman Compose

Avant de continuer, assurez-vous d'avoir récupéré la dernière image Docker d'OpenClaw :
```bash
podman pull ghcr.io/openclaw/openclaw:latest
```
Une fois cela fait, téléchargez le fichier Compose d'OpenClaw [openclaw-compose.yaml](assets/openclaw-compose.yaml) et placez-le dans le répertoire racine `/firecrawl` :

> Cette convention est nécessaire pour que `systemd` puisse localiser et démarrer correctement le service, comme indiqué dans `WorkingDirectory=${HOME}/firecrawl`.

> Vous pouvez toujours étendre la pile en ajoutant d'autres services Firecrawl au besoin. La liste complète des services disponibles se trouve dans le [docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml) officiel de Firecrawl.

### 4. Lancer le service OpenClaw via Firecrawl 

Avant de confier le contrôle à `systemd`, vérifiez que tout fonctionne correctement en exécutant la pile manuellement :
```bash
podman compose -f openclaw-compose.yaml up -d
```
Si tout est configuré correctement, vous devriez voir le conteneur OpenClaw démarrer et la sortie de votre ligne de commande devrait ressembler à ceci :
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

Une fois la vérification effectuée, arrêtez la pile avant de poursuivre :
```bash
podman compose -f openclaw-compose.yaml down
```
Avant de démarrer le service, vous devez vous assurer que le propriétaire et les permissions appropriés sont définis sur le répertoire `firecrawl` et son fichier `.env`.
Ceci est essentiel pour que le service puisse écrire vos identifiants au démarrage.
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
Maintenant que tout est validé, démarrez le service via `systemd` :
```bash
systemctl --user start firecrawl.service
```
[Les actions OpenClaw](https://docs.openclaw.ai/) sont accessibles depuis le conteneur interactif, et le tableau de bord Web est disponible sur le même hôte et le même port à l'adresse http://127.0.0.1:18789.
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### Obtenir votre `OPENCLAW_GATEWAY_TOKEN`

Une fois le service en cours d'exécution, vous remarquerez qu'un nouveau répertoire `.openclaw` a été créé dans votre dossier personnel (~/.openclaw). Ce répertoire est verrouillé par défaut, vous devrez donc le déverrouiller pour récupérer votre jeton de passerelle.

1. Accordez l'accès au répertoire :
```bash
sudo chmod 777 ~/.openclaw/
```
2. Lisez votre jeton de passerelle :
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
Repérez la valeur `OPENCLAW_GATEWAY_TOKEN` dans le résultat.

3. Ouvrez le tableau de bord de la passerelle dans votre navigateur à l'adresse http://127.0.0.1:18789. Collez votre jeton lorsque vous y êtes invité pour vous authentifier.

Pour arrêter le service, exécutez :
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---
## Démarrer la passerelle OpenClaw

La passerelle est le processus OpenClaw qui gère la boucle de l'agent et sert le tableau de bord :

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

Puisque la passerelle se lie à la boucle locale (loopback), le tableau de bord s'authentifie automatiquement lorsqu'il est ouvert depuis la même machine; aucune saisie de jeton ni approbation d'appareil n'est nécessaire pour l'accès local. Vous devriez voir le tableau de bord OpenClaw avec votre modèle Lemonade affiché comme serveur dorsal actif.

> Si vous avez activé le bac à sable (sandboxing), vous pouvez le vérifier en demandant à l'agent d'exécuter `run hostname` depuis le tableau de bord. Si vous voyez un court identifiant de conteneur au lieu du nom d'hôte de votre machine, le bac à sable fonctionne correctement.

**Félicitations, vous avez construit une pile d'agent IA entièrement locale, à partir de zéro.**

> **Besoin du jeton de la passerelle?** Exécutez `openclaw dashboard --no-open` pour afficher l'URL du tableau de bord avec le jeton intégré (il tente également de le copier dans votre presse-papiers). Autrement, le jeton se trouve à `gateway.auth.token` dans `~/.openclaw/openclaw.json`.

**Accéder au tableau de bord depuis un autre appareil (via un tunnel SSH)**

Si OpenClaw s'exécute sur une machine distante, vous pouvez accéder à son tableau de bord depuis votre machine locale par l'intermédiaire d'un tunnel SSH. Le tunnel redirige le port de la passerelle (`18789`) afin que votre navigateur local puisse communiquer avec la passerelle distante via `127.0.0.1`.

1. Depuis votre **machine locale**, connectez-vous une fois à la machine distante et acceptez l'invite d'empreinte numérique afin que l'hôte soit ajouté à vos hôtes connus :

   ```bash
   ssh user@<host-ip>
   ```

2. Toujours sur votre **machine locale**, ouvrez le tunnel SSH :

   ```bash
   ssh -N -L 18789:127.0.0.1:18789 user@<host-ip>
   ```

   > **Remarque :** Après avoir saisi votre mot de passe, le terminal n'affiche aucune sortie et semble figé. C'est normal : l'option `-N` indique à SSH de ne pas exécuter de commande distante, il maintient donc simplement le tunnel ouvert. Laissez ce terminal en cours d'exécution.

3. Sur votre **machine locale**, ouvrez un navigateur et accédez à `http://127.0.0.1:18789`.

4. Sur la **machine distante**, affichez le jeton de la passerelle et collez-le dans le navigateur pour vous connecter :

   ```bash
   openclaw dashboard --no-open
   ```

   Cette commande affiche l'URL du tableau de bord avec le jeton intégré; copiez le jeton pour vous connecter. (Le jeton est également stocké à `gateway.auth.token` dans `~/.openclaw/openclaw.json`.)

> **Approuver un appareil distant :** Lorsque vous ouvrez le tableau de bord depuis une autre machine ou un téléphone, le navigateur peut afficher un identifiant de demande. Sur la **machine distante**, répertoriez les demandes en attente :
> ```bash
> openclaw devices list
> ```
> Puis approuvez la demande correspondante :
> ```bash
> openclaw devices approve <requestId>
> ```
> Cette étape n'est nécessaire que pour les appareils distants ou secondaires; l'accès en boucle locale depuis la même machine s'authentifie automatiquement. Consultez la documentation sur l'[Accès distant](https://docs.openclaw.ai/gateway/remote) pour plus de détails.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Facultatif : Connecter un canal de communication

Une fois la passerelle en cours d'exécution, vous pouvez accéder à votre agent local depuis n'importe quel appareil. Choisissez l'option qui convient à votre configuration. OpenClaw prend en charge [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram), et d'autres canaux; consultez la liste complète sur [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Option A : Discord

Discord nécessite un serveur où **vous disposez d'un accès administrateur** pour ajouter un robot (bot). Si vous partagez des serveurs sans en posséder un, utilisez plutôt l'option B (Telegram).

#### Créer un compte et un serveur Discord

Si vous n'avez pas de compte Discord, inscrivez-vous sur [discord.com](https://discord.com). Vous avez également besoin d'un serveur sur lequel vous êtes administrateur; créez-en un en cliquant sur l'icône **+** dans la barre latérale de Discord, puis en sélectionnant **Créer mon propre serveur**. Un serveur privé convient parfaitement.

#### Créer une application et un robot Discord

1. Accédez au [portail des développeurs Discord](https://discord.com/developers/applications) et cliquez sur **New Application**. Donnez-lui un nom (p. ex. « openclaw-bot »).
2. Dans la barre latérale, cliquez sur **Bot**. Définissez un nom d'utilisateur pour le robot.
3. Toujours sur la page Bot, faites défiler jusqu'à **Privileged Gateway Intents** et activez :
   - **Message Content Intent** (obligatoire)
   - **Server Members Intent** (recommandé)
4. Remontez et cliquez sur **Reset Token** pour générer votre jeton de robot. Copiez-le.

#### Ajouter le robot à votre serveur

1. Dans la barre latérale, cliquez sur **OAuth2/ URL Generator**.
2. Sous **Scopes**, activez `bot` et `applications.commands`.
3. Sous **Bot Permissions**, activez : View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Copiez l'URL générée, collez-la dans votre navigateur, sélectionnez votre serveur et confirmez. Le robot devrait maintenant apparaître dans la liste des membres de votre serveur.

#### Récupérer vos identifiants

Activez le mode développeur dans Discord (**Paramètres utilisateur/ Avancés/ Mode développeur**), puis :
- Faites un clic droit sur l'icône de votre serveur : **Copier l'ID du serveur**
- Faites un clic droit sur votre propre avatar : **Copier l'ID utilisateur**

#### Autoriser les messages privés des membres du serveur

Clic droit sur l'icône de votre serveur/ **Paramètres de confidentialité**/ activez **Messages privés**. Cela permet au robot de vous envoyer des messages privés, ce qui est nécessaire pour l'étape de jumelage.

#### Configurer OpenClaw pour Discord

Enregistrez votre jeton de robot comme variable d'environnement, puis créez un seul fichier de correctif (patch) qui active Discord, référence le jeton et met votre serveur sur liste d'autorisation. Remplacez `<server_id>` et `<user_id>` par les identifiants recueillis ci-dessus.

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

> **Ne comptez pas sur l'agent pour configurer cela.** Lorsque le bac à sable est activé, l'agent ne peut pas écrire dans `~/.openclaw/openclaw.json` depuis l'intérieur du bac à sable; utilisez plutôt les commandes CLI ci-dessus sur l'hôte.

Redémarrez la passerelle afin qu'elle prenne en compte la nouvelle configuration de canal :

```bash
openclaw gateway run --bind loopback --port 18789
```

Vous devriez voir `logged in to discord as <bot-name>` dans la sortie de la passerelle en quelques secondes.
#### Jumelez votre compte Discord

Envoyez un message privé au bot sur Discord. Il répondra avec un court code de jumelage.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Approuvez-le sur la machine qui exécute OpenClaw :
```bash
openclaw pairing approve discord <CODE>
```

> Les codes de jumelage expirent après une heure.

Vous pouvez maintenant clavarder avec votre agent directement depuis Discord et déléguer des tâches à votre matériel local.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Option B : Telegram

Telegram est plus simple que Discord pour la plupart des utilisateurs; il ne nécessite ni serveur ni accès administrateur.

#### Créer un bot Telegram

1. Ouvrez Telegram et envoyez un message à **@BotFather**.
2. Envoyez `/newbot` et suivez les instructions. Enregistrez le jeton de bot qu'il vous fournit.

#### Configurer OpenClaw pour Telegram

Enregistrez le jeton comme variable d'environnement :

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Ajoutez la configuration du canal à `~/.openclaw/openclaw.json` (ou corrigez-le via le tableau de bord) :

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

Redémarrez la passerelle, puis envoyez un message à votre bot dans Telegram. Approuvez le jumelage :

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Les codes de jumelage expirent après une heure. Vous pouvez maintenant clavarder avec votre agent via message privé Telegram.

---

## Prochaines étapes

Maintenant que votre agent peut recevoir des commandes de votre téléphone et agir sur votre machine locale, voici trois pistes à explorer :

1. **Résumé du marché boursier** : Planifiez OpenClaw pour qu'il récupère des données d'API financières à intervalle fixe, résume les mouvements du jour à l'aide de votre modèle local, et envoie un résumé à votre téléphone chaque matin via le canal de votre choix.

2. **Surveillance de l'ajustement fin** : Lancez une tâche d'entraînement à distance via Telegram ou Discord, puis demandez à l'agent de surveiller le journal d'entraînement et de vous transmettre périodiquement les valeurs de perte, l'utilisation du GPU et l'utilisation du disque sur votre téléphone. Si l'exécution se bloque ou si la VRAM connaît un pic, vous le saurez immédiatement sans avoir à être devant la machine.

3. **IOT avec un VLM local** : Pointez une caméra vers votre porte d'entrée, exécutez un modèle de vision sur Lemonade, et demandez à OpenClaw d'analyser les images à la demande ou sur déclenchement. Demandez « des colis sont-ils arrivés aujourd'hui? » depuis votre téléphone et obtenez une réponse directe de votre propre matériel.

<!-- @os:linux -->
<!-- @test:id=lemonade-unload-linux timeout=60 hidden=True -->
```bash
# CI cleanup: unload the model so the GPU pool is free
lemonade unload || true
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-unload-windows timeout=60 hidden=True -->
```powershell
# CI cleanup: unload the model so the GPU pool is free
lemonade unload
exit 0
```
<!-- @test:end -->
<!-- @os:end -->