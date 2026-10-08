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
> This playbook uses AMD Playbooks comment tags that are interpreted by the AMD Playbooks site.
> GitHub renders the Markdown content, but not the device, OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Aperçu

Les développeurs consacrent beaucoup de temps à de petites boucles récurrentes : examiner des demandes de tirage (pull requests) étiquetées, répondre aux commentaires GitHub, trier de nouveaux problèmes (issues), transformer des fils Slack en notes de mêlée quotidienne ou en suivis d'incidents, et surveiller les signaux de versions ou de recherche.
Chaque boucle est familière, mais elle exige tout de même du jugement : rassembler le bon contexte, décider de ce qui importe, et publier une mise à jour claire là où l'équipe travaille déjà.

Les [automatisations OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview) transforment ces boucles en conversations d'agent planifiées ou déclenchées par des événements : des exécutions où un agent logiciel d'IA peut lire le contexte, appeler des outils et produire une mise à jour.
Les modèles d'automatisation partagés dans le catalogue d'extensions OpenHands suivent ce modèle pour l'examen de demandes de tirage GitHub, la surveillance de dépôts, le triage de problèmes Linear, les rétrospectives d'incidents, les résumés de mêlée Slack et les comptes rendus de recherche : une automatisation se déclenche, utilise des intégrations configurées comme GitHub ou Slack pour récupérer le contexte, raisonne sur ce contexte avec un grand modèle de langage (LLM), puis consigne un résultat.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) est le plan de contrôle local pour créer et tester ces automatisations.
Dans ce guide pratique, il exécute un serveur d'agent OpenHands, le processus principal qui exécute les conversations d'agent, et connecte l'agent à des services externes comme GitHub et Slack.

Pour que le flux de travail demeure sur votre système AMD, l'agent communique avec un modèle local servi par Lemonade Server.
Lemonade expose ce modèle par l'intermédiaire d'une API compatible OpenAI, de sorte qu'Agent Canvas peut le configurer comme un point de terminaison distant de type OpenAI, tandis que le modèle, l'invite et le contexte du flux de travail demeurent locaux.

Dans ce guide pratique, vous allez créer une automatisation concrète : un résumé de développement planifié de GitHub vers Slack.
Elle utilise GitHub pour examiner l'activité récente du dépôt, Slack pour publier le résumé, les appels API d'Agent Canvas pour configurer et tester l'automatisation, et Lemonade pour exécuter le LLM localement.

![Diagramme d'architecture montrant GitHub MCP, l'automatisation OpenHands, Lemonade Server et Slack MCP](assets/00-architecture-overview.png)

## Ce que vous apprendrez

- Comment démarrer Lemonade Server et vérifier qu'un modèle local répond aux requêtes de clavardage
- Comment lancer Agent Canvas et pointer son serveur d'agent vers un LLM local
- Comment installer les serveurs du protocole de contexte de modèle (MCP) pour GitHub et Slack par l'intermédiaire de l'API du serveur d'agent
- Comment créer et déclencher une automatisation OpenHands planifiée qui publie un résumé de développement sur Slack
- Comment résoudre les problèmes les plus courants liés au modèle local et à l'automatisation

## Concepts de base

| Concept | Ce que c'est | Sa place dans ce guide pratique |
| --- | --- | --- |
| Lemonade Server | Une plateforme locale de diffusion de LLM conçue pour le matériel AMD qui expose une API compatible OpenAI. Vos données ne quittent jamais votre machine. | Exécute le modèle qui alimente l'agent. |
| Serveur d'agent OpenHands | Le processus principal qui exécute les conversations d'agent OpenHands. | Héberge l'agent, son profil LLM et ses serveurs MCP. |
| Agent Canvas | Le plan de contrôle local pour OpenHands qui exécute le serveur d'agent et une interface utilisateur permettant d'examiner les exécutions d'agent. | Lance les systèmes dorsaux et fournit l'API que vous appelez. |
| Serveur MCP | Un serveur du protocole de contexte de modèle qui donne à un agent des outils pour un service externe comme GitHub ou Slack. | Permet à l'agent de lire GitHub et d'écrire sur Slack. |
| Automatisation OpenHands | Une conversation d'agent planifiée ou déclenchée par un événement qui récupère le contexte, raisonne dessus et consigne un résultat quelque part. | Le résumé GitHub-vers-Slack que vous créez ici. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Les flux de travail d'agent de programmation bénéficient d'un modèle et d'une fenêtre contextuelle plus grands.
> Utilisez au moins 32 Go de mémoire système, et privilégiez 64 Go ou plus pour les modèles GGUF plus volumineux.
<!-- @device:end -->

## Configuration de la mémoire

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Vérifier les mises à jour logicielles

<!-- @require:software-update -->
<!-- @device:end -->

## Conditions préalables

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @prereq:uv,agent-canvas,lemonade-models-qwen3-35b-a3b,lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- On Windows the Agent Canvas stack runs from the Docker image (which bundles
     Node.js, uv and agent-canvas), so only the Lemonade model is needed here. -->
<!-- @prereq:lemonade-models-qwen3-35b-a3b -->
<!-- @os:end -->

Vous avez besoin de :

- Lemonade Server installé en suivant le [guide d'installation standard de Lemonade](https://lemonade-server.ai/docs/guide/install/).

<!-- @os:linux -->
- Node.js 22.12 ou une version ultérieure et `npm`, utilisés pour installer le CLI publié d'Agent Canvas et exécuter des serveurs MCP avec `npx`.
- `uv`, le gestionnaire de paquets Python qu'Agent Canvas utilise pour construire l'environnement du serveur d'agent. S'il n'est pas déjà installé, installez-le à partir du [guide d'installation d'uv](https://docs.astral.sh/uv/getting-started/installation/).
- Un paquet publié récent `@openhands/agent-canvas` avec des paramètres d'agent pilotés par schéma, `LLMSummarizingCondenserSettings.max_tokens`, et la prise en charge de `custom_tokenizer` pour le LLM.
- Le paquet Python `transformers` disponible dans l'environnement du serveur d'agent. Il est requis pour le comptage de jetons des modèles de clavardage lorsque `custom_tokenizer` est défini.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop pour Windows](https://docs.docker.com/desktop/setup/install/windows-install/), installé et en cours d'exécution. Sous Windows, la pile Agent Canvas s'exécute à partir de l'image Docker publiée, qui regroupe Node.js, `uv`, `transformers` et le paquet `@openhands/agent-canvas`, de sorte que vous n'avez pas à les installer sur l'hôte.
<!-- @os:end -->

- Un jeton GitHub avec un accès en lecture au dépôt que vous souhaitez résumer.
- Un jeton de robot Slack (`xoxb-...`) avec les droits `chat:write` et un accès en lecture aux canaux.
- Un identifiant d'équipe Slack (`T...`).
- Un identifiant de canal Slack (`C...`) où le résumé doit être publié.

Invitez l'application Slack dans le canal cible avant de tester l'automatisation.
## Variables utilisées dans ce guide pratique

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
Le modèle, le tokenizer et les autres paramètres du LLM sont saisis directement dans l'interface utilisateur d'Agent Canvas lors des étapes suivantes, c'est pourquoi leurs valeurs littérales sont indiquées en ligne là où vous en avez besoin.

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
Des caractères génériques d'organisation trop larges peuvent renvoyer un contexte MCP trop volumineux pour les modèles locaux.

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

## 1. Démarrer Lemonade Server

Démarrez le modèle à partir de l'interface en ligne de commande Lemonade :

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

> **Choisissez un modèle adapté à votre matériel.** `Qwen3.6-35B-A3B-GGUF` (~20 Go) est un modèle performant pour ce flux de travail, mais il nécessite un important bassin de mémoire.
> Si votre appareil dispose d'une mémoire ou d'une mémoire vidéo (VRAM) GPU limitée, choisissez un modèle GGUF plus petit dans la bibliothèque de modèles Lemonade et utilisez cet identifiant de modèle (ainsi que le tokenizer correspondant) tout au long de ce guide pratique.

> **Remarque :** La première exécution de `lemonade run` télécharge le modèle s'il n'est pas déjà présent, ce qui peut prendre un certain temps selon la taille du modèle et votre connexion.

Lemonade expose une API compatible OpenAI à l'adresse suivante :

```text
http://127.0.0.1:13305/api/v1
```

Facultatif : si Agent Canvas ou l'exécuteur d'automatisation ne se trouve pas sur la même machine, publiez le point de terminaison Lemonade par l'intermédiaire d'un tunnel sécurisé et utilisez l'URL HTTPS comme URL de base du LLM.
[ngrok](https://ngrok.com/) expose un port local à Internet par l'entremise d'une URL HTTPS sécurisée; il nécessite un compte ngrok gratuit, et vous devez remplacer `YOUR_NGROK_DOMAIN.ngrok-free.dev` par votre propre domaine réservé :

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. Vérifier le modèle local

Confirmez que Lemonade peut servir le modèle sélectionné :

<!-- @os:linux -->
```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Envoyez ensuite une petite requête de clavardage :

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

Envoyez ensuite une petite requête de clavardage :

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

Si cette requête renvoie un tableau `choices`, Lemonade est prêt pour Agent Canvas.

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
Installez le paquet Agent Canvas publié et démarrez la pile complète :

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Si l'installation globale de npm échoue avec une erreur de permissions, consultez la rubrique de dépannage des permissions npm ci-dessous.

Par défaut, Agent Canvas démarre à l'adresse `http://localhost:8000`.
Ouvrez cette URL dans votre navigateur.
Le port n'a rien de particulier : si le port 8000 est déjà utilisé, passez n'importe quel port libre avec `--port` (ou `-p`).
Le backend local par défaut devrait apparaître comme étant en bon état de fonctionnement sur l'écran d'accueil.

> **Remarque :** Le premier lancement crée l'environnement Python géré par `uv` du serveur d'agent, ce qui peut donc prendre quelques minutes avant que le backend ne signale un bon état de fonctionnement.

La commande `agent-canvas` démarre ensemble le serveur d'agent, le backend d'automatisation et l'interface Web.
Il vous suffit de cette seule commande pour exécuter OpenHands localement.
Le reste de ce guide pratique configure tout par l'intermédiaire de l'interface utilisateur d'Agent Canvas dans votre navigateur.
<!-- @os:end -->

<!-- @os:windows -->
Sous Windows, exécutez l'image de conteneur Agent Canvas publiée avec Docker Desktop.
L'image regroupe le serveur d'agent, le backend d'automatisation et l'interface Web, de sorte que vous n'avez pas besoin d'installer Node.js, `uv` ou l'interface en ligne de commande sur l'hôte.

Créez d'abord les dossiers de configuration et d'espace de travail que le conteneur monte :

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Récupérez l'image publiée (environ 6 Go; elle est publique, aucune connexion n'est donc requise) :

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

Démarrez ensuite la pile :

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

Ouvrez `http://localhost:8000/canvas` dans votre navigateur.
Si le port 8000 est déjà utilisé, mappez un autre port d'hôte, par exemple `-p 8080:8000`, et ouvrez plutôt `http://localhost:8080/canvas`.

> **Remarque :** Le premier lancement crée l'environnement du serveur d'agent à l'intérieur du conteneur, ce qui peut donc prendre quelques minutes avant que le backend ne signale un bon état de fonctionnement.

Le montage `.openhands` conserve votre profil LLM, vos serveurs MCP et vos automatisations d'un redémarrage de conteneur à l'autre.
Le reste de ce guide pratique configure tout par l'intermédiaire de l'interface utilisateur d'Agent Canvas dans votre navigateur à l'adresse `http://localhost:8000/canvas`.
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
## 4. Configurer le LLM local dans l'interface utilisateur

Au premier lancement, Agent Canvas ouvre un processus d'accueil.
Dans ce processus :

1. Conservez **OpenHands** comme agent sélectionné et cliquez sur **Next**.
2. Dans **Set up your LLM**, sélectionnez **Advanced**.
3. Laissez **Authentication** sur **API key**.
4. Définissez **Custom Model** sur `openai/Qwen3.6-35B-A3B-GGUF`.
5. Définissez **Base URL** sur `http://127.0.0.1:13305/api/v1`.
6. Pour **API Key**, saisissez une valeur d'espace réservé non vide, par exemple `lemonade-local`. Lemonade n'exige pas une véritable clé, mais le client OpenHands a besoin d'une valeur à envoyer.

<!-- @os:windows -->
> **Windows (Docker) :** le serveur Agent Server s'exécute à l'intérieur du conteneur, alors définissez **Base URL** sur `http://host.docker.internal:13305/api/v1` plutôt que sur `http://127.0.0.1:13305/api/v1`.
> Depuis l'intérieur du conteneur, `127.0.0.1` désigne le conteneur lui-même; `host.docker.internal` permet d'atteindre Lemonade qui s'exécute sur l'hôte Windows, et Docker Desktop fournit automatiquement ce nom d'hôte.
<!-- @os:end -->

Les champs de connexion devraient ressembler à ceci.
Le champ de clé API est masqué par l'interface utilisateur.

![Paramètres LLM avancés d'Agent Canvas lors de la première utilisation, avec le modèle Lemonade et l'URL de base locale](assets/01-llm-advanced-settings.png)

Sélectionnez ensuite **All** et définissez les champs supplémentaires propres au modèle local :

1. Faites défiler jusqu'à **Custom Tokenizer** et définissez-le sur `Qwen/Qwen3.6-35B-A3B`.
2. Faites défiler jusqu'à **LiteLLM Extra Body** et définissez-le sur `{"enable_thinking": true}`.
3. Cliquez sur **Next**.

![Onglet All des paramètres LLM d'Agent Canvas lors de la première utilisation, avec le tokenizer personnalisé Qwen](assets/02-llm-all-tokenizer-settings.png)

![Onglet All des paramètres LLM d'Agent Canvas lors de la première utilisation, avec le corps supplémentaire LiteLLM configuré](assets/03-llm-all-extra-body-settings.png)

Les paramètres du LLM devraient afficher :

| Champ | Valeur |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

Le préfixe `openai/` indique à LiteLLM d'utiliser un formatage de requête compatible OpenAI envers le point de terminaison Lemonade.
Le tokenizer personnalisé est le tokenizer Hugging Face d'origine du modèle GGUF; il permet à OpenHands de compter les mêmes jetons de gabarit de conversation (chat-template) que ceux que voit le serveur de modèle local.
Le formulaire LLM de première utilisation actuel n'affiche pas les paramètres du condenseur (condenser).
Si votre version d'Agent Canvas expose plus tard les paramètres du condenseur sous **Settings > LLM**, utilisez `llm_summarizing` et définissez le nombre maximal de jetons en dessous de la fenêtre contextuelle de Lemonade, par exemple `56000`.

## 5. Installer les serveurs MCP GitHub et Slack

Dans l'interface utilisateur d'Agent Canvas, ouvrez **Customize** (ou **Settings > MCP**) pour ajouter les serveurs MCP qui fournissent à l'agent des outils pour GitHub et Slack.
Les valeurs de jetons sont envoyées uniquement à votre Agent Server local et sont conservées sous forme de paramètres chiffrés.

<!-- @os:windows -->
> **Windows (Docker) :** les commandes de serveur MCP `npx` ci-dessous s'exécutent à l'intérieur du conteneur, qui inclut déjà Node.js, de sorte que rien de plus n'est installé sur l'hôte.
> Comme `.openhands` est monté, les serveurs MCP et leurs jetons persistent d'un redémarrage du conteneur à l'autre.
<!-- @os:end -->

### Serveur MCP GitHub

Ajoutez un nouveau serveur MCP avec les paramètres suivants :

| Champ | Valeur |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = votre jeton GitHub |

Utilisez un jeton GitHub avec un accès en lecture au dépôt que vous souhaitez résumer.

### Serveur MCP Slack

Ajoutez un deuxième serveur MCP avec les paramètres suivants :

| Champ | Valeur |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = l'identifiant de votre canal de synthèse |

Définissez `SLACK_CHANNEL_IDS` sur l'identifiant du canal de synthèse (la même valeur que `SLACK_DIGEST_CHANNEL`) afin que l'agent n'ait pas besoin de parcourir chaque canal Slack.

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

## 6. Créer l'automatisation de la synthèse

Dans l'interface utilisateur d'Agent Canvas, ouvrez la page **Automations** et créez une nouvelle automatisation :

1. Choisissez **Create automation** et sélectionnez le type **Prompt preset**.
2. Définissez **Name** sur `GitHub Development Digest to Slack`.
3. Définissez **Prompt** avec le texte suivant, en remplaçant les valeurs d'espace réservé du dépôt et du canal par vos propres valeurs :

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

4. Définissez **Trigger** sur **Cron** avec l'horaire `0 9 * * 1-5` (9 h les jours de semaine) et définissez **Timezone** sur votre fuseau horaire, par exemple `America/New_York`.
5. Définissez **Timeout** sur `900` secondes.
6. Enregistrez l'automatisation.

La page de détail de l'automatisation affiche la nouvelle automatisation avec son déclencheur cron et le point d'entrée de type prompt preset généré.

![Détail de l'automatisation Agent Canvas après sa création](assets/05-automation-created.png)
## 7. Tester l'automatisation

Depuis la page de détail de l'automatisation dans l'interface Agent Canvas UI :

1. Cliquez sur **Run now** (ou **Dispatch**) pour exécuter l'automatisation une fois immédiatement.
2. Surveillez la liste des exécutions sur la même page. La dernière exécution devrait passer à l'état `COMPLETED`.
3. Ouvrez votre canal Slack cible. Il devrait contenir le résumé généré.

Vous n'avez pas besoin d'attendre le déclenchement de la planification cron — **Run now** déclenche une exécution à la demande afin que vous puissiez confirmer que le prompt, les connexions MCP et la publication Slack fonctionnent tous avant de vous fier à la planification.

![Exécution d'automatisation Agent Canvas terminée avec succès](assets/06-automation-run-completed.png)

![Canal Slack affichant le résumé OpenHands généré](assets/07-slackbot-message.png)

## Dépannage

<!-- @os:windows -->
- **Le port Docker 8000 est déjà utilisé :** mappez un port hôte différent, par exemple `docker run ... -p 8080:8000 ...`, et ouvrez `http://localhost:8080/canvas`.
- **`docker pull` échoue avec une erreur d'identifiants** (par exemple, « A specified logon session does not exist ») : exécutez l'extraction depuis une session Windows interactive, ou pré-extrayez l'image. L'image est publique, donc aucune connexion `docker login` n'est requise.
- **L'interface se charge mais le serveur dorsal est défaillant :** le premier lancement construit l'environnement Agent Server dans le conteneur. Attendez une minute et actualisez, puis vérifiez `docker logs <container>` pour suivre la progression.
- **Agent Canvas ne peut pas joindre Lemonade depuis le conteneur :** réglez l'**URL de base** du LLM à `http://host.docker.internal:13305/api/v1` (et non `127.0.0.1`), et confirmez que Lemonade s'exécute sur l'hôte Windows.
<!-- @os:end -->

- **Lemonade est arrêté :** redémarrez-le avec la commande `lemonade run "${LEMONADE_MODEL}"` de l'étape 1, puis relancez la vérification de l'état de santé.
- **`npm install -g` échoue avec une erreur d'autorisation :** sous Linux ou WSL, configurez un répertoire global npm appartenant à l'utilisateur, ajoutez-le à votre fichier de démarrage du shell, puis réinstallez Agent Canvas :

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

Si vous utilisez `zsh`, ajoutez la même ligne `export PATH=...` à `~/.zshrc` plutôt qu'à `~/.bashrc`.
- **Agent Canvas rejette les paramètres LLM après la configuration de `custom_tokenizer` :** installez `transformers` dans l'environnement Python d'Agent Server, redémarrez Agent Canvas si nécessaire, puis réessayez d'enregistrer les paramètres LLM. OpenHands exige Transformers pour charger le modèle de conversation du tokenizer lorsque `custom_tokenizer` est défini.
- **Agent Canvas ne peut pas joindre Lemonade :** vérifiez `curl -fsS "${LEMONADE_BASE_URL}/health"` et confirmez que l'URL de base saisie dans le formulaire LLM de première utilisation ou dans **Settings > LLM** correspond au point de terminaison local en cours d'exécution ou au tunnel HTTPS.
- **Les paramètres LLM n'ont pas été enregistrés :** assurez-vous d'avoir cliqué sur **Next** après avoir saisi les valeurs. Rouvrez **Settings > LLM** pour confirmer que les valeurs ont bien été conservées.
- **Le GitHub MCP ne peut pas voir les dépôts privés :** confirmez que le jeton GitHub dispose d'un accès en lecture au dépôt cible et que le bouton **Test** du MCP dans **Customize** annonce les outils GitHub.
- **Slack peut lire les canaux mais ne peut pas publier :** invitez l'application Slack au canal cible et confirmez que le bot dispose de `chat:write`.
- **L'automatisation liste trop de canaux Slack :** utilisez un identifiant de canal Slack et définissez `SLACK_CHANNEL_IDS` sur le serveur MCP Slack dans **Customize**.
- **L'exécution de l'automatisation échoue ou dépasse le contexte :** confirmez que Lemonade a été démarré avec `ctx_size=65536`, confirmez que le LLM OpenHands a bien `custom_tokenizer` défini, et utilisez un dépôt explicite avec des ensembles de résultats GitHub plafonnés à 3 à 5 éléments. Si votre version d'Agent Canvas expose des paramètres de condensateur, réglez le nombre maximal de jetons du condensateur en dessous de la fenêtre de contexte de Lemonade.

## Prochaines étapes

- Ajouter un résumé hebdomadaire consacré uniquement aux versions.
- Ajouter une automatisation déclenchée par un événement GitHub pour des alertes plus rapides sur les PR ou les push.
- Acheminer le même résumé vers Notion, Linear ou un autre outil pris en charge par MCP.

## Ressources

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [Documentation de Lemonade Server](https://lemonade-server.ai/docs)
- [Dépôt d'extensions OpenHands](https://github.com/OpenHands/extensions)
- [Serveurs Model Context Protocol](https://github.com/modelcontextprotocol/servers)
- [Paquet MCP Slack](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)

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