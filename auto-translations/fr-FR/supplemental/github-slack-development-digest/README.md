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
> This playbook uses AMD Playbooks comment tags that are interpreted by the AMD Playbooks site.
> GitHub renders the Markdown content, but not the device, OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Vue d'ensemble

Les développeurs passent beaucoup de temps sur de petites boucles récurrentes : examiner des pull requests étiquetées, répondre aux commentaires GitHub, trier de nouveaux tickets, transformer des fils Slack en notes de standup ou en suivis d'incidents, et surveiller les signaux de version ou de recherche.
Chaque boucle est familière, mais elle exige tout de même du jugement : rassembler le bon contexte, décider ce qui compte, et publier une mise à jour claire là où l'équipe travaille déjà.

Les [automatisations OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview) transforment ces boucles en conversations d'agent planifiées ou déclenchées par des événements : des exécutions où un agent logiciel IA peut lire le contexte, appeler des outils, et produire une mise à jour.
Les modèles d'automatisation partagés dans le catalogue d'extensions OpenHands suivent ce schéma pour la revue de pull requests GitHub, la surveillance de dépôts, le tri de tickets Linear, les rétrospectives d'incidents, les digests de standup Slack, et les résumés de recherche : une automatisation se réveille, utilise des intégrations configurées telles que GitHub ou Slack pour récupérer le contexte, raisonne sur ce contexte avec un grand modèle de langage (LLM), et écrit un résultat en retour.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) est le plan de contrôle local pour construire et tester ces automatisations.
Dans ce guide pratique, il exécute un serveur d'agent OpenHands, le processus backend qui exécute les conversations d'agent, et connecte l'agent à des services externes tels que GitHub et Slack.

Pour conserver le flux de travail sur votre système AMD, l'agent communique avec un modèle local servi par Lemonade Server.
Lemonade expose ce modèle via une API compatible OpenAI, de sorte qu'Agent Canvas peut le configurer comme un point de terminaison distant de type OpenAI, tandis que le modèle, l'invite et le contexte du flux de travail restent locaux.

Dans ce guide pratique, vous allez construire une automatisation concrète : un digest de développement planifié allant de GitHub à Slack.
Elle utilise GitHub pour examiner l'activité récente du dépôt, Slack pour publier le digest, les appels API d'Agent Canvas pour configurer et tester l'automatisation, et Lemonade pour exécuter le LLM localement.

![Diagramme d'architecture montrant GitHub MCP, l'automatisation OpenHands, Lemonade Server, et Slack MCP](assets/00-architecture-overview.png)

## Ce que vous allez apprendre

- Comment démarrer Lemonade Server et vérifier qu'un modèle local répond aux requêtes de chat
- Comment lancer Agent Canvas et faire pointer son serveur d'agent vers un LLM local
- Comment installer des serveurs Model Context Protocol (MCP) GitHub et Slack via l'API du serveur d'agent
- Comment créer et déclencher une automatisation OpenHands planifiée qui publie un digest de développement sur Slack
- Comment dépanner les erreurs les plus courantes liées au modèle local et à l'automatisation

## Concepts clés

| Concept | Ce que c'est | Sa place dans ce guide pratique |
| --- | --- | --- |
| Lemonade Server | Une plateforme de service de LLM local conçue pour le matériel AMD qui expose une API compatible OpenAI. Vos données ne quittent jamais votre machine. | Exécute le modèle qui alimente l'agent. |
| OpenHands Agent Server | Le processus backend qui exécute les conversations d'agent OpenHands. | Héberge l'agent, son profil LLM, et ses serveurs MCP. |
| Agent Canvas | Le plan de contrôle local pour OpenHands qui exécute Agent Server et une interface utilisateur pour inspecter les exécutions d'agent. | Lance les backends et fournit l'API que vous appelez. |
| Serveur MCP | Un serveur Model Context Protocol qui donne à un agent des outils pour un service externe tel que GitHub ou Slack. | Permet à l'agent de lire GitHub et d'écrire sur Slack. |
| Automatisation OpenHands | Une conversation d'agent planifiée ou déclenchée par un événement qui récupère du contexte, raisonne dessus, et écrit un résultat quelque part. | Le digest GitHub-vers-Slack que vous construisez ici. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Les flux de travail d'agent de codage bénéficient d'un modèle et d'une fenêtre de contexte plus grands.
> Utilisez au moins 32 Go de mémoire système, et privilégiez 64 Go ou plus pour les modèles GGUF plus volumineux.
<!-- @device:end -->

## Définition de la configuration de la mémoire

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Vérifier les mises à jour logicielles

<!-- @require:software-update -->
<!-- @device:end -->

## Prérequis

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- @os:end -->

Vous avez besoin de :

- Lemonade Server installé en suivant le [guide d'installation standard de Lemonade](https://lemonade-server.ai/docs/guide/install/).

<!-- @os:linux -->
- Node.js 22.12 ou une version ultérieure et `npm`, utilisés pour installer le CLI publié d'Agent Canvas et exécuter les serveurs MCP avec `npx`.
- `uv`, le gestionnaire de paquets Python qu'Agent Canvas utilise pour construire l'environnement du serveur d'agent. S'il n'est pas déjà installé, installez-le à partir du [guide d'installation d'uv](https://docs.astral.sh/uv/getting-started/installation/).
- Un package `@openhands/agent-canvas` publié récent avec des paramètres d'agent pilotés par schéma, `LLMSummarizingCondenserSettings.max_tokens`, et la prise en charge de `custom_tokenizer` pour le LLM.
- Le package Python `transformers` disponible dans l'environnement du serveur d'agent. Il est requis pour le comptage de jetons de modèle de chat lorsque `custom_tokenizer` est défini.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop pour Windows](https://docs.docker.com/desktop/setup/install/windows-install/), installé et en cours d'exécution. Sur Windows, la pile Agent Canvas s'exécute à partir de l'image Docker publiée, qui regroupe Node.js, `uv`, `transformers`, et le package `@openhands/agent-canvas`, de sorte que vous n'avez pas besoin de les installer sur l'hôte.
<!-- @os:end -->

- Un jeton GitHub avec un accès en lecture au dépôt que vous souhaitez résumer.
- Un jeton de bot Slack (`xoxb-...`) avec `chat:write` et un accès en lecture aux canaux.
- Un ID d'équipe Slack (`T...`).
- Un ID de canal Slack (`C...`) où le digest doit être publié.

Invitez l'application Slack dans le canal cible avant de tester l'automatisation.
## Variables utilisées dans ce playbook

<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @os:linux -->
```bash
export LEMONADE_BASE_URL="http://127.0.0.1:13305/api/v1"
export LEMONADE_MODEL="Qwen3.6-35B-A3B-GGUF"
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
$env:LEMONADE_BASE_URL = "http://127.0.0.1:13305/api/v1"
$env:LEMONADE_MODEL = "Qwen3.6-35B-A3B-GGUF"
```
<!-- @os:end -->

Ces deux variables sont utilisées par les commandes de vérification ci-dessous.
Le modèle, le tokenizer et les autres paramètres du LLM sont saisis directement dans l'interface utilisateur d'Agent Canvas lors des étapes suivantes ; leurs valeurs littérales sont donc indiquées directement dans le texte là où vous en avez besoin.

Les valeurs suivantes sont saisies dans l'interface utilisateur d'Agent Canvas lors des étapes suivantes.
Définissez-les ici afin de pouvoir les copier :

<!-- @os:linux -->
```bash
export GITHUB_REPO_FILTER="your-org/your-repo"
export SLACK_DIGEST_CHANNEL="C0123456789"
export DIGEST_TIMEZONE="America/New_York"
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
$env:GITHUB_REPO_FILTER = "your-org/your-repo"
$env:SLACK_DIGEST_CHANNEL = "C0123456789"
$env:DIGEST_TIMEZONE = "America/New_York"
```
<!-- @os:end -->

Utilisez une valeur explicite `owner/repo` pour `GITHUB_REPO_FILTER`.
Des jokers d'organisation trop larges peuvent renvoyer un contexte MCP trop volumineux pour les modèles locaux.

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

## 1. Démarrer Lemonade Server

Démarrez le modèle depuis la CLI de Lemonade :

<!-- @os:linux -->
```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "${LEMONADE_MODEL}"
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "$env:LEMONADE_MODEL"
```
<!-- @os:end -->

> **Choisissez un modèle adapté à votre matériel.** `Qwen3.6-35B-A3B-GGUF` (~20 Go) est un modèle performant pour ce workflow, mais nécessite un vaste espace mémoire.
> Si votre appareil dispose d'une mémoire ou d'une VRAM GPU limitée, choisissez un modèle GGUF plus petit dans la bibliothèque de modèles Lemonade et utilisez cet identifiant de modèle (ainsi que son tokenizer correspondant) tout au long de ce playbook.

> **Remarque :** La première commande `lemonade run` télécharge le modèle s'il n'est pas déjà présent, ce qui peut prendre un certain temps selon la taille du modèle et votre connexion.

Lemonade expose une API compatible OpenAI à l'adresse :

```text
http://127.0.0.1:13305/api/v1
```

Facultatif : si Agent Canvas ou l'exécuteur d'automatisation ne se trouve pas sur la même machine, publiez le point de terminaison Lemonade via un tunnel sécurisé et utilisez l'URL HTTPS comme URL de base du LLM.
[ngrok](https://ngrok.com/) expose un port local sur Internet via une URL HTTPS sécurisée ; cela nécessite un compte ngrok gratuit, et vous remplacez `YOUR_NGROK_DOMAIN.ngrok-free.dev` par votre propre domaine réservé :

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. Vérifier le modèle local

Confirmez que Lemonade peut servir le modèle sélectionné :

<!-- @os:linux -->
```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Envoyez ensuite une petite requête de chat :

```bash
curl -sS "${LEMONADE_BASE_URL}/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "'"${LEMONADE_MODEL}"'",
    "messages": [
      {"role": "user", "content": "Reply with exactly: OK"}
    ],
    "temperature": 0,
    "max_tokens": 64
  }' | python3 -m json.tool
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
curl.exe -s "$env:LEMONADE_BASE_URL/models"
```

Envoyez ensuite une petite requête de chat :

```powershell
$body = @{
  model    = "$env:LEMONADE_MODEL"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens  = 64
} | ConvertTo-Json -Depth 5
curl.exe -sS "$env:LEMONADE_BASE_URL/chat/completions" -H "Content-Type: application/json" -d $body
```
<!-- @os:end -->

Si cela renvoie un tableau `choices`, Lemonade est prêt pour Agent Canvas.

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
entry = None
for item in data.get("data", []):
    if item.get("id") == "${lemonade_model}":
        entry = item
        break

if entry is None:
    print("Model ${lemonade_model} is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print("Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it.")
    sys.exit(1)

print("OK: ${lemonade_model} model is downloaded in Lemonade")
PY

body='{
  "model": "${lemonade_model}",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 64
}'

out="$(curl -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body" || true)"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi
```
<!-- @test:end -->
<!-- @os:end -->

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

if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

$parsed = $modelsJson | ConvertFrom-Json
$entry = $parsed.data | Where-Object { $_.id -eq "${lemonade_model}" } | Select-Object -First 1

if (-not $entry) { throw "Model ${lemonade_model} is not present in Lemonade /api/v1/models." }
if (-not $entry.downloaded) { throw "Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it." }
Write-Host "OK: ${lemonade_model} model is downloaded in Lemonade"

$body = @{
  model    = "${lemonade_model}"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens  = 64
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "digest-lemonade-chat-body.json"
[System.IO.File]::WriteAllText($tmpBody, $body, [System.Text.UTF8Encoding]::new($false))

try {
  $out = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpBody"
  if (-not $out) { throw "Empty response from Lemonade chat/completions" }
  Write-Host "OK: Lemonade chat/completions returned a response"
}
finally {
  Remove-Item $tmpBody -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=node-npm-version timeout=60 hidden=True -->
```bash
node -v
npm -v
```
<!-- @test:end -->
<!-- @os:end -->

## 3. Démarrer Agent Canvas

<!-- @os:linux -->
Installez le package Agent Canvas publié et démarrez l'ensemble de la stack :

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Si l'installation globale npm échoue avec une erreur de permissions, consultez l'entrée de dépannage des permissions npm ci-dessous.

Par défaut, Agent Canvas démarre sur `http://localhost:8000`.
Ouvrez cette URL dans votre navigateur.
Le port n'a rien de spécial : si le port 8000 est déjà utilisé, indiquez n'importe quel port libre avec `--port` (ou `-p`).
Le backend local par défaut devrait s'afficher comme opérationnel sur l'écran d'accueil.

> **Remarque :** Le premier lancement construit l'environnement Python géré par `uv` de l'Agent Server, ce qui peut donc prendre quelques minutes avant que le backend ne se signale comme opérationnel.

La commande `agent-canvas` démarre ensemble le serveur d'agent, le backend d'automatisation et le frontend web.
Vous n'avez besoin que de cette seule commande pour exécuter OpenHands localement.
Le reste de ce playbook configure tout via l'interface utilisateur d'Agent Canvas dans votre navigateur.
<!-- @os:end -->

<!-- @os:windows -->
Sous Windows, exécutez l'image conteneur Agent Canvas publiée avec Docker Desktop.
L'image regroupe l'Agent Server, le backend d'automatisation et le frontend web, vous n'avez donc pas besoin d'installer Node.js, `uv` ou la CLI sur l'hôte.

Commencez par créer les dossiers de configuration et d'espace de travail montés par le conteneur :

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Récupérez l'image publiée (environ 6 Go ; elle est publique, aucune connexion n'est donc requise) :

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

Démarrez ensuite la stack :

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

Ouvrez `http://localhost:8000/canvas` dans votre navigateur.
Si le port 8000 est déjà utilisé, mappez un port hôte différent, par exemple `-p 8080:8000`, et ouvrez plutôt `http://localhost:8080/canvas`.

> **Remarque :** Le premier lancement construit l'environnement de l'Agent Server à l'intérieur du conteneur, ce qui peut donc prendre quelques minutes avant que le backend ne se signale comme opérationnel.

Le montage `.openhands` conserve votre profil LLM, vos serveurs MCP et vos automatisations d'un redémarrage du conteneur à l'autre.
Le reste de ce playbook configure tout via l'interface utilisateur d'Agent Canvas dans votre navigateur à l'adresse `http://localhost:8000/canvas`.
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=uv-version timeout=60 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
uv --version
```
<!-- @test:end -->

<!-- @test:id=agent-canvas-version timeout=60 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
# Prefer --version; fall back to --help if this build has no --version flag.
agent-canvas --version || agent-canvas --help
echo "OK: agent-canvas CLI is on PATH"
```
<!-- @test:end -->

<!-- @test:id=agent-canvas-start timeout=1200 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
log="/tmp/agent-canvas-test.log"
p=""
cleanup() {
  set +e
  for port in 8000 18000 18001 3001; do
    pid="$(ss -ltnp 2>/dev/null | grep ":$port " | grep -oE 'pid=[0-9]+' | head -1 | cut -d= -f2)"
    [ -n "$pid" ] && kill "$pid" 2>/dev/null
  done
  if [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null
    sleep 2
    kill -9 "$p" 2>/dev/null
  fi
}
# Preserve the real exit code; cleanup must never flip a pass to a fail (or vice versa).
trap 'rc=$?; cleanup; exit $rc' EXIT

# First launch builds the agent server's uv-managed Python env, so allow a generous startup window.
agent-canvas >"$log" 2>&1 &
p=$!

# Probe the agent-server backend health (18000/server_info), NOT just the 8000 ingress root:
# the ingress serves the static frontend and returns 200 for / even when the agent-server is down.
ok=false
for i in $(seq 1 300); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:18000/server_info || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  if ! kill -0 "$p" 2>/dev/null; then
    echo "agent-canvas process exited before it finished starting"
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "agent-server not ready on http://127.0.0.1:18000/server_info"
  cat "$log" || true
  exit 1
fi

echo "OK: agent-canvas agent-server is responding"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=agent-canvas-docker-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$image    = "ghcr.io/openhands/agent-canvas:1.14.0"
$name     = "digest-agent-canvas-ci"
$hostPort = 18080

# Pull the image if the runner doesn't already have it. The published image is
# public, so no login is needed. A non-interactive session can trip over a
# configured Docker credential helper (ghcr is unauthenticated here), so pull
# with an isolated, empty Docker config that has no credsStore/credHelpers.
# TODO: remove this self-provisioning once the runners ship the image by default.
$imgId = docker images -q $image
if (-not $imgId) {
  Write-Host "Image $image not present; pulling..."
  $dockerCfg = Join-Path $env:TEMP "digest-docker-cfg"
  New-Item -ItemType Directory -Force -Path $dockerCfg | Out-Null
  '{}' | Set-Content -Path (Join-Path $dockerCfg "config.json") -Encoding ascii
  docker --config $dockerCfg pull $image
  if ($LASTEXITCODE -ne 0) { throw "docker pull failed for $image" }
}
Write-Host "OK: $image is present"

if (docker ps -aq -f "name=$name") { docker rm -f $name | Out-Null }

try {
  docker run -d --name $name -p "${hostPort}:8000" $image | Out-Null
  if ($LASTEXITCODE -ne 0) { throw "docker run failed for $image" }

  # Probe the agent-server backend health through the container proxy
  # (/server_info -> agent-server on 18000 inside the container), not just the
  # /canvas static UI, which can return 200 while the backend is still down.
  $ok = $false
  for ($i = 0; $i -lt 300; $i++) {
    $canvas = try { (Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 "http://localhost:${hostPort}/canvas").StatusCode } catch { 0 }
    $info   = try { (Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 "http://localhost:${hostPort}/server_info").StatusCode } catch { 0 }
    if ($canvas -eq 200 -and $info -eq 200) { $ok = $true; break }
    $state = docker inspect -f "{{.State.Status}}" $name 2>$null
    if ($state -ne "running") { throw "Container $name exited before it finished starting" }
    Start-Sleep -Seconds 2
  }

  if (-not $ok) {
    docker logs --tail 40 $name
    throw "agent-canvas backend not healthy on http://localhost:${hostPort}/server_info"
  }
  Write-Host "OK: agent-canvas Docker stack is healthy (/canvas and /server_info return 200)"
}
finally {
  if (docker ps -aq -f "name=$name") { docker rm -f $name | Out-Null }
}
```
<!-- @test:end -->
<!-- @os:end -->
## 4. Configurer le LLM local dans l'UI

Au premier lancement, Agent Canvas ouvre un flux d'onboarding.
Dans ce flux :

1. Laissez **OpenHands** sélectionné comme agent et cliquez sur **Next**.
2. Sur **Set up your LLM**, sélectionnez **Advanced**.
3. Laissez **Authentication** défini sur **API key**.
4. Définissez **Custom Model** sur `openai/Qwen3.6-35B-A3B-GGUF`.
5. Définissez **Base URL** sur `http://127.0.0.1:13305/api/v1`.
6. Pour **API Key**, saisissez un espace réservé non vide, par exemple `lemonade-local`. Lemonade n'exige pas de véritable clé, mais le client OpenHands a besoin d'une valeur à envoyer.

<!-- @os:windows -->
> **Windows (Docker) :** l'Agent Server s'exécute à l'intérieur du conteneur, définissez donc **Base URL** sur `http://host.docker.internal:13305/api/v1` au lieu de `http://127.0.0.1:13305/api/v1`.
> Depuis l'intérieur du conteneur, `127.0.0.1` désigne le conteneur lui-même ; `host.docker.internal` permet d'atteindre Lemonade qui s'exécute sur l'hôte Windows, et Docker Desktop fournit automatiquement ce nom d'hôte.
<!-- @os:end -->

Les champs de connexion devraient ressembler à ceci.
Le champ de clé API est masqué par l'UI.

![Paramètres LLM avancés d'Agent Canvas au premier lancement avec le modèle Lemonade et l'URL de base locale](assets/01-llm-advanced-settings.png)

Sélectionnez ensuite **All** et définissez les champs supplémentaires du modèle local :

1. Faites défiler jusqu'à **Custom Tokenizer** et définissez-le sur `Qwen/Qwen3.6-35B-A3B`.
2. Faites défiler jusqu'à **LiteLLM Extra Body** et définissez-le sur `{"enable_thinking": true}`.
3. Cliquez sur **Next**.

![Onglet All des paramètres LLM d'Agent Canvas au premier lancement avec le tokenizer personnalisé Qwen](assets/02-llm-all-tokenizer-settings.png)

![Onglet All des paramètres LLM d'Agent Canvas au premier lancement avec le corps supplémentaire LiteLLM configuré](assets/03-llm-all-extra-body-settings.png)

Les paramètres LLM devraient afficher :

| Champ | Valeur |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

Le préfixe `openai/` indique à LiteLLM d'utiliser un formatage de requête compatible OpenAI vis-à-vis du point de terminaison Lemonade.
Le tokenizer personnalisé est le tokenizer Hugging Face original du modèle GGUF ; il permet à OpenHands de compter les mêmes jetons de modèle de conversation que ceux vus par le serveur de modèle local.
Le formulaire LLM actuel de premier lancement n'affiche pas les paramètres de condenseur.
Si votre build d'Agent Canvas expose ultérieurement les paramètres de condenseur sous **Settings > LLM**, utilisez `llm_summarizing` et définissez un nombre maximal de jetons inférieur à la fenêtre de contexte de Lemonade, par exemple `56000`.

## 5. Installer les serveurs MCP GitHub et Slack

Dans l'UI d'Agent Canvas, ouvrez **Customize** (ou **Settings > MCP**) pour ajouter les serveurs MCP qui donnent à l'agent des outils pour GitHub et Slack.
Les valeurs de jeton sont envoyées uniquement à votre Agent Server local et sont conservées sous forme de paramètres chiffrés.

<!-- @os:windows -->
> **Windows (Docker) :** les commandes de serveur MCP `npx` ci-dessous s'exécutent à l'intérieur du conteneur, qui inclut déjà Node.js, de sorte que rien de plus n'est installé sur l'hôte.
> Comme `.openhands` est monté, les serveurs MCP et leurs jetons persistent entre les redémarrages du conteneur.
<!-- @os:end -->

### Serveur MCP GitHub

Ajoutez un nouveau serveur MCP avec ces paramètres :

| Champ | Valeur |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = votre jeton GitHub |

Utilisez un jeton GitHub avec un accès en lecture au dépôt que vous souhaitez résumer.

### Serveur MCP Slack

Ajoutez un second serveur MCP avec ces paramètres :

| Champ | Valeur |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = l'ID de votre canal de synthèse |

Définissez `SLACK_CHANNEL_IDS` sur l'ID du canal de synthèse (la même valeur que `SLACK_DIGEST_CHANNEL`) afin que l'agent n'ait pas besoin de parcourir chaque canal Slack.

Après avoir ajouté les deux serveurs, utilisez le bouton **Test** sur chacun d'eux pour confirmer qu'il se connecte et annonce ses outils.
Le serveur GitHub devrait lister des outils GitHub, et le serveur Slack devrait lister des outils Slack.

![Page MCP d'Agent Canvas avec les serveurs GitHub et Slack installés](assets/04-mcp-servers-installed.png)

<!-- @test:id=mcp-packages-resolve timeout=300 hidden=True -->
```bash
# The GitHub and Slack MCP servers run via npx and need real tokens to connect,
# so CI only confirms the referenced packages resolve from the npm registry.
npm view @modelcontextprotocol/server-github version
npm view @modelcontextprotocol/server-slack version
```
<!-- @test:end -->

## 6. Créer l'automatisation de synthèse

Dans l'UI d'Agent Canvas, ouvrez la page **Automations** et créez une nouvelle automatisation :

1. Choisissez **Create automation** et sélectionnez le type **Prompt preset**.
2. Définissez **Name** sur `GitHub Development Digest to Slack`.
3. Définissez **Prompt** sur le texte suivant, en remplaçant les espaces réservés du dépôt et du canal par vos propres valeurs :

   ```text
   Use the GitHub MCP server for exactly one repository: your-org/your-repo.
   Inspect recent development activity since the previous weekday, including
   merged pull requests, newly opened or reopened pull requests, notable
   commits pushed to main or release branches, new issues, important issue
   updates, releases, risks, blockers, and review requests. Keep GitHub
   lookups small: inspect the latest 3 to 5 commits, pull requests, issues,
   and releases. Use the Slack MCP server to post directly to channel ID
   C0123456789. Keep the Slack message concise: title with date range, 3 to 7
   bullets, links back to GitHub, and a Needs attention section only if
   needed. End with: This digest was generated by an AI agent (OpenHands) on
   behalf of the user. Do not include secrets, raw tokens, private
   environment variables, or unrelated Slack messages.
   ```

4. Définissez **Trigger** sur **Cron** avec la planification `0 9 * * 1-5` (9 h en semaine) et définissez **Timezone** sur votre fuseau horaire, par exemple `America/New_York`.
5. Définissez **Timeout** sur `900` secondes.
6. Enregistrez l'automatisation.

La page de détail de l'automatisation affiche la nouvelle automatisation avec son déclencheur cron et le point d'entrée de prompt preset généré.

![Détail de l'automatisation Agent Canvas après création](assets/05-automation-created.png)
## 7. Tester l'automatisation

Depuis la page de détail de l'automatisation dans l'interface Agent Canvas UI :

1. Cliquez sur **Run now** (ou **Dispatch**) pour exécuter l'automatisation une fois immédiatement.
2. Observez la liste des exécutions sur la même page. La dernière exécution doit passer à l'état `COMPLETED`.
3. Ouvrez votre canal Slack cible. Il doit contenir le résumé généré.

Vous n'avez pas besoin d'attendre le déclenchement de la planification cron : **Run now** déclenche une exécution à la demande afin que vous puissiez confirmer que le prompt, les connexions MCP et la publication Slack fonctionnent tous correctement avant de vous fier à la planification.

![Exécution de l'automatisation Agent Canvas terminée avec succès](assets/06-automation-run-completed.png)

![Canal Slack affichant le résumé OpenHands généré](assets/07-slackbot-message.png)

## Dépannage

<!-- @os:windows -->
- **Le port Docker 8000 est déjà utilisé :** mappez un port hôte différent, par exemple `docker run ... -p 8080:8000 ...`, puis ouvrez `http://localhost:8080/canvas`.
- **`docker pull` échoue avec une erreur d'identifiants** (par exemple, « A specified logon session does not exist ») : exécutez le pull depuis une session Windows interactive, ou pré-téléchargez l'image. L'image est publique, aucun `docker login` n'est donc nécessaire.
- **L'interface se charge mais le backend est en état non sain :** le premier lancement construit l'environnement de l'Agent Server à l'intérieur du conteneur. Attendez une minute puis actualisez, ensuite vérifiez `docker logs <container>` pour suivre la progression.
- **Agent Canvas ne parvient pas à joindre Lemonade depuis le conteneur :** définissez l'**URL de base** du LLM sur `http://host.docker.internal:13305/api/v1` (et non `127.0.0.1`), et vérifiez que Lemonade s'exécute bien sur l'hôte Windows.
<!-- @os:end -->

- **Lemonade est arrêté :** redémarrez-le avec la commande `lemonade run "${LEMONADE_MODEL}"` de l'étape 1, puis relancez la vérification de santé.
- **`npm install -g` échoue avec une erreur de permissions :** sous Linux ou WSL, configurez un répertoire global npm appartenant à l'utilisateur, ajoutez-le à votre fichier de démarrage shell, puis réinstallez Agent Canvas :

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

Si vous utilisez `zsh`, ajoutez la même ligne `export PATH=...` à `~/.zshrc` au lieu de `~/.bashrc`.
- **Agent Canvas rejette les paramètres LLM après la définition de `custom_tokenizer` :** installez `transformers` dans l'environnement Python de l'Agent Server, redémarrez Agent Canvas si nécessaire, puis réessayez d'enregistrer les paramètres LLM. OpenHands a besoin de Transformers pour charger le modèle de chat du tokenizer lorsque `custom_tokenizer` est défini.
- **Agent Canvas ne parvient pas à joindre Lemonade :** vérifiez `curl -fsS "${LEMONADE_BASE_URL}/health"` et assurez-vous que l'URL de base saisie dans le formulaire LLM de première utilisation ou dans **Settings > LLM** correspond bien à l'endpoint local en cours d'exécution ou au tunnel HTTPS.
- **Les paramètres LLM n'ont pas été enregistrés :** assurez-vous d'avoir cliqué sur **Next** après avoir saisi les valeurs. Rouvrez **Settings > LLM** pour confirmer que les valeurs ont bien été conservées.
- **Le MCP GitHub ne voit pas les dépôts privés :** vérifiez que le token GitHub dispose d'un accès en lecture au dépôt cible et que le bouton **Test** du MCP dans **Customize** annonce bien les outils GitHub.
- **Slack peut lire les canaux mais ne peut pas y publier :** invitez l'application Slack sur le canal cible et vérifiez que le bot dispose de `chat:write`.
- **L'automatisation liste trop de canaux Slack :** utilisez un identifiant de canal Slack et définissez `SLACK_CHANNEL_IDS` sur le serveur MCP Slack dans **Customize**.
- **L'exécution de l'automatisation échoue ou dépasse le contexte :** vérifiez que Lemonade a été démarré avec `ctx_size=65536`, que le LLM OpenHands a bien `custom_tokenizer` défini, et utilisez un dépôt explicite avec des jeux de résultats GitHub limités à 3-5 éléments. Si votre build Agent Canvas expose des paramètres de condenseur, définissez le nombre maximal de tokens du condenseur en dessous de la fenêtre de contexte de Lemonade.

## Étapes suivantes

- Ajouter un résumé hebdomadaire limité aux versions publiées.
- Ajouter une automatisation déclenchée par événement GitHub pour des alertes plus rapides sur les PR ou les push.
- Router le même résumé vers Notion, Linear, ou un autre outil basé sur MCP.

## Ressources

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [Documentation du serveur Lemonade](https://lemonade-server.ai/docs)
- [Dépôt d'extensions OpenHands](https://github.com/OpenHands/extensions)
- [Serveurs Model Context Protocol](https://github.com/modelcontextprotocol/servers)
- [Paquet Slack MCP](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)

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
try { lemonade unload } catch {}
```
<!-- @test:end -->
<!-- @os:end -->