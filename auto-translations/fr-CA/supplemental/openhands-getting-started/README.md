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
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Vue d'ensemble

[OpenHands](https://github.com/All-Hands-AI/OpenHands) est un agent logiciel
d'IA capable d'écrire du code, d'exécuter des commandes, de naviguer sur le Web
et de modifier des fichiers dans un espace de travail réel. Plutôt que de
copier des suggestions depuis une fenêtre de clavardage, vous pointez l'agent
vers un dossier de projet et le laissez faire le travail : implémenter une
fonctionnalité, corriger un bogue, écrire des tests ou expliquer une base de
code.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) est l'interface Web
recommandée pour exécuter OpenHands. Une seule commande `agent-canvas` démarre
ensemble le serveur de l'agent, le backend d'automatisation et le frontend
Web, afin que vous puissiez mener une conversation avec l'agent depuis votre
navigateur.

Pour que tout reste sur votre système AMD, l'agent communique avec un modèle
local servi par Lemonade Server. Lemonade expose ce modèle par l'intermédiaire
d'une API compatible OpenAI, de sorte qu'Agent Canvas peut le configurer comme
n'importe quel autre point de terminaison de style OpenAI, pendant que le
modèle, votre code et le contexte de la conversation demeurent tous sur votre
machine.

Dans ce guide pratique, vous allez démarrer un modèle local, lancer Agent
Canvas, le pointer vers ce modèle et exécuter votre première tâche de
codage sur un véritable dossier de projet.

## Ce que vous allez apprendre

- Comment démarrer Lemonade Server et confirmer qu'un modèle local répond aux
  requêtes de clavardage
- Comment installer et lancer Agent Canvas à partir du paquet npm
- Comment configurer Agent Canvas pour qu'il utilise un modèle Lemonade local
  comme LLM
- Comment démarrer une conversation OpenHands et observer l'agent modifier des
  fichiers et exécuter des commandes dans un espace de travail
- Comment examiner ce que l'agent a modifié et le guider à l'aide de messages
  de suivi

## Concepts clés

| Concept | Ce que c'est | Où il s'inscrit dans ce guide pratique |
| --- | --- | --- |
| Lemonade Server | Une plateforme de diffusion de LLM locale conçue pour le matériel AMD, qui expose une API compatible OpenAI. Vos données ne quittent jamais votre machine. | Exécute le modèle qui alimente l'agent. |
| OpenHands | Un agent logiciel d'IA qui lit et modifie des fichiers, exécute des commandes shell et navigue sur le Web dans un espace de travail. | L'agent que vous dirigez depuis le clavardage. |
| Agent Canvas | L'interface Web et le backend qui exécutent les conversations OpenHands et affichent les appels d'outils et les modifications de fichiers. | Lance la pile et héberge votre conversation. |
| Espace de travail | Le dossier de projet que l'agent est autorisé à lire et à modifier. | La cible des modifications et des commandes de l'agent. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Les flux de travail d'agent de codage bénéficient d'un modèle et d'une
> fenêtre de contexte plus grands. Utilisez au moins 32 Go de mémoire système,
> et privilégiez 64 Go ou plus pour les modèles GGUF de grande taille.
<!-- @device:end -->

## Définition de la configuration de la mémoire

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Vérifier les mises à jour logicielles

<!-- @require:software-update -->
<!-- @device:end -->

## Prérequis


<!-- @os:linux -->
<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade,nodejs -->
<!-- @prereq:uv,agent-canvas,lemonade-models-qwen3-35b-a3b,lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- On Windows the Agent Canvas stack runs from the Docker image (which bundles
     Node.js, uv and agent-canvas), so only the Lemonade model is needed here.
     lemonade-chat-windows asserts the model is already downloaded. -->
<!-- @prereq:lemonade-models-qwen3-35b-a3b -->
<!-- @os:end -->

Vous avez besoin de :

- Lemonade Server installé et capable de servir le modèle ci-dessous.

<!-- @os:linux -->
- Node.js 22.12 ou une version ultérieure et `npm` (utilisés par l'interface
  en ligne de commande `agent-canvas`).
- `uv`, le gestionnaire de paquets Python qu'Agent Canvas utilise pour gérer
  l'environnement du serveur de l'agent. Si votre système ne l'a pas déjà,
  installez-le à partir du [guide d'installation d'uv](https://docs.astral.sh/uv/getting-started/installation/)
  avant de lancer Agent Canvas.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop pour Windows](https://docs.docker.com/desktop/setup/install/windows-install/),
  installé et en cours d'exécution. Sous Windows, la pile Agent Canvas
  s'exécute à partir de l'image Docker publiée, qui regroupe Node.js, `uv` et
  le paquet `@openhands/agent-canvas`, de sorte que vous n'avez pas besoin de
  les installer sur l'hôte.
<!-- @os:end -->

- Un dossier de projet dans lequel travailler. Il peut s'agir de n'importe
  quel dépôt git local ou répertoire de code sur lequel vous souhaitez que
  l'agent travaille.

<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @os:linux -->
<!-- @test:id=prereq-clis-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

lemonade --version
node -v
npm -v

# uv is a required prerequisite (agent-canvas uses it to build its Python env).
# Install it only if the runner doesn't already have it.
# TODO: remove this self-provisioning once the runners ship uv by default.
if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi
export PATH="$HOME/.local/bin:$PATH"
uv --version

echo "OK: lemonade, node, npm, and uv are all available"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=prereq-clis-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

# On Windows the Agent Canvas stack runs from the published Docker image, so the
# only host prerequisites are Lemonade and a running Docker engine. Node.js, uv,
# and agent-canvas are bundled inside the container.
lemonade --version
docker version --format "{{.Server.Version}}"

Write-Host "OK: lemonade and docker are available"
```
<!-- @test:end -->
<!-- @os:end -->

## 1. Démarrer Lemonade Server

Démarrez le modèle à partir de l'interface en ligne de commande Lemonade :

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

> **Choisissez un modèle adapté à votre matériel.** `Qwen3.6-35B-A3B-GGUF`
> (~20 Go) est un modèle de codage performant, mais nécessite un grand bassin
> de mémoire. Si votre appareil dispose d'une mémoire ou d'une VRAM GPU
> limitée, choisissez plutôt un modèle GGUF plus petit dans la bibliothèque de
> modèles Lemonade et utilisez cet identifiant de modèle tout au long de ce
> guide pratique.

> **Remarque :** La première exécution de `lemonade run` télécharge le
> modèle s'il n'est pas déjà présent, ce qui peut prendre un certain temps
> selon la taille du modèle et votre connexion.

Lemonade expose une API compatible OpenAI à l'adresse suivante :

```text
http://127.0.0.1:13305/api/v1
```

## 2. Vérifier le modèle local

Confirmez que Lemonade peut servir le modèle sélectionné :

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

Envoyez ensuite une petite requête de clavardage :

```bash
curl -sS "http://127.0.0.1:13305/api/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen3.6-35B-A3B-GGUF",
    "messages": [
      {"role": "user", "content": "Reply with exactly: OK"}
    ],
    "temperature": 0,
    "max_tokens": 64
  }' | python3 -m json.tool
```

Si cela retourne un tableau `choices`, Lemonade est prêt pour Agent Canvas.

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
model_id = "${lemonade_model}"

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
PY

body='{
  "model": "${lemonade_model}",
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
$entry = $parsed.data | Where-Object { $_.id -eq "${lemonade_model}" } | Select-Object -First 1

if (-not $entry) {throw "Model ${lemonade_model} is not present in Lemonade /api/v1/models."}
if (-not $entry.downloaded) {throw "Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it before running CI."}
Write-Host "OK: ${lemonade_model} model is downloaded in Lemonade"

$body = @{
  model = "${lemonade_model}"
  messages = @(
    @{
      role = "user"
      content = "Reply with exactly: OK"
    }
  )
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "openhands-lemonade-chat-body.json"
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
## 3. Installer et lancer Agent Canvas

<!-- @os:linux -->
Installez globalement le paquet Agent Canvas publié :

```bash
npm install -g @openhands/agent-canvas
```

<!-- @test:id=agent-canvas-version-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

# agent-canvas is expected to be provisioned on the runner. Fail loudly if it
# isn't, rather than installing it here.
if ! command -v agent-canvas >/dev/null 2>&1; then
  echo "agent-canvas is not on PATH; the runner must provision it before CI runs"
  exit 1
fi

# Prefer --version; fall back to --help if this build has no --version flag.
agent-canvas --version || agent-canvas --help

echo "OK: agent-canvas CLI is on PATH"
```
<!-- @test:end -->

Démarrez ensuite la pile complète à partir d'un terminal :

```bash
agent-canvas
```

Par défaut, Agent Canvas démarre sur `http://localhost:8000`. Ouvrez cette URL
dans votre navigateur. Le port n'a rien de particulier : si le port 8000 est
déjà utilisé, indiquez un port libre quelconque avec `--port` (ou `-p`) au
moment de lancer Agent Canvas :

```bash
agent-canvas --port 3000
```

Ouvrez ensuite `http://localhost:3000` à la place. Le backend local par défaut
devrait s'afficher comme étant en bonne santé sur l'écran d'accueil.

La commande `agent-canvas` démarre ensemble le serveur de l'agent, le backend
d'automatisation et le frontend web. Cette seule commande suffit pour exécuter
OpenHands localement.

<!-- @test:id=agent-canvas-server-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

log="/tmp/agent-canvas-ci.log"
p=""
cleanup() {
  if [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null || true
    sleep 2
    kill -9 "$p" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

# First launch builds the agent server's uv-managed Python env, so allow a generous startup window.
agent-canvas >"$log" 2>&1 &
p=$!

# Probe the agent-server backend health (18000/server_info), NOT just the 8000
# ingress root: the ingress serves the static frontend and returns 200 for /
# even when the agent-server is down.
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
  echo "---- agent-canvas log ----"
  cat "$log" || true
  exit 1
fi

echo "OK: agent-canvas agent-server is responding"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
Sous Windows, exécutez l'image de conteneur Agent Canvas publiée avec Docker
Desktop. L'image regroupe le serveur de l'agent, le backend d'automatisation et
le frontend web, de sorte que vous n'avez pas à installer Node.js, `uv` ni la
CLI sur l'hôte.

Créez d'abord les dossiers de configuration et d'espace de travail que le
conteneur monte :

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Récupérez l'image publiée (elle est publique, aucune connexion n'est donc
requise) :

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

Ouvrez `http://localhost:8000/canvas` dans votre navigateur. Si le port 8000
est déjà utilisé, mappez un autre port hôte, par exemple `-p 8080:8000`, et
ouvrez plutôt `http://localhost:8080/canvas`.

> **Remarque :** Le premier lancement initialise le serveur de l'agent à
> l'intérieur du conteneur, ce qui peut donc prendre une minute ou deux avant
> que le backend ne signale un bon fonctionnement.

Le montage `.openhands` conserve votre profil LLM et vos paramètres d'une
relance de conteneur à l'autre. Le reste de ce guide configure tout par
l'intermédiaire de l'interface utilisateur d'Agent Canvas dans votre
navigateur.

<!-- @test:id=agent-canvas-docker-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$image    = "ghcr.io/openhands/agent-canvas:1.14.0"
$name     = "openhands-agent-canvas-ci"
$hostPort = 18080

# The image is expected to be provisioned on the runner. Fail loudly if it
# isn't, rather than pulling it here.
$imgId = docker images -q $image
if (-not $imgId) {
  throw "Image $image is not present; the runner must provision it before CI runs"
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

## 4. Configurer le LLM local

Au premier lancement, Agent Canvas ouvre un processus d'intégration. Dans ce
processus :

1. Laissez **OpenHands** sélectionné comme agent et cliquez sur **Next**.
2. À l'étape **Set up your LLM**, sélectionnez **Advanced**.
3. Laissez **Authentication** réglé sur **API key**.
4. Réglez **Custom Model** à `openai/Qwen3.6-35B-A3B-GGUF`.
5. Réglez **Base URL** à `http://127.0.0.1:13305/api/v1`.
   <!-- @os:windows -->
   > Sous Windows, la pile s'exécute dans un conteneur, qui ne peut pas
   > joindre l'hôte à l'adresse `127.0.0.1`. Utilisez plutôt
   > `http://host.docker.internal:13305/api/v1` afin que l'agent conteneurisé
   > puisse joindre Lemonade s'exécutant sur l'hôte Windows.
   <!-- @os:end -->
6. Pour **API Key**, saisissez une valeur non vide quelconque servant de
   substitut, par exemple `lemonade-local`. Lemonade n'exige pas de véritable
   clé, mais le client OpenHands a besoin d'une valeur à envoyer.
7. Cliquez sur **Next**.

Les paramètres avancés une fois remplis devraient ressembler à ceci. Le champ
de clé API est masqué par l'interface utilisateur.

![Paramètres avancés du LLM lors de la première utilisation d'Agent Canvas, avec le modèle Lemonade et l'URL de base locale](assets/01-llm-advanced-settings.png)

Agent Canvas enregistre ces valeurs comme profil LLM. Si votre version vous
demande de nommer ce profil, utilisez un nom sans espace, par exemple
`lemonade-local`. Si vous changez de modèle plus tard, ouvrez **Settings >
LLM** et mettez à jour les mêmes champs avancés. Vous pouvez basculer entre les
profils enregistrés à partir du champ de saisie du clavardage avec la commande
`/model`.

## 5. Ouvrir un espace de travail

L'agent ne peut lire et modifier que les fichiers se trouvant dans un espace de
travail que vous choisissez. Avant de démarrer une tâche, pointez Agent Canvas
vers votre dossier de projet :

1. À partir de l'écran d'accueil, choisissez **Open Workspace**.
2. Sélectionnez le dossier contenant votre projet (par exemple, un dépôt git
   sur lequel vous souhaitez que l'agent travaille).
3. Démarrez une nouvelle conversation dans cet espace de travail.

Tout ce que fait l'agent — lire des fichiers, exécuter des commandes, modifier
du code — est limité à cet espace de travail.

![Écran d'accueil d'Agent Canvas après l'intégration](assets/02-agent-canvas-home.png)

## 6. Exécuter votre première tâche de programmation

Une fois l'espace de travail ouvert et le LLM local sélectionné, saisissez une
tâche concrète dans le clavardage. Une bonne première tâche est simple et
vérifiable, par exemple :

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

Observez la chronologie de la conversation. OpenHands va :

- Lire l'espace de travail pour comprendre sa structure.
- Créer `hello.py` contenant la fonction demandée et le bloc de test.
- Exécuter facultativement `python3 hello.py` pour vérifier le résultat.
- Rendre compte de ce qu'il a fait et de tout résultat de commande dans le
  clavardage.

Vous devriez voir le nouveau fichier apparaître dans l'espace de travail, et le
message final de l'agent devrait décrire la modification qu'il a apportée. Il
s'agit du moment clé : l'agent a écrit et exécuté du vrai code dans votre
dossier de projet.

## 7. Examiner le travail de l'agent et l'orienter

Une fois que l'agent a terminé une étape, examinez son travail avant d'accepter
la suivante :

- **Modifications de fichiers** : utilisez l'explorateur de fichiers de
  l'espace de travail ou la vue des différences de l'agent pour voir
  exactement ce qui a été ajouté, modifié ou supprimé.
- **Résultat des commandes** : développez toute commande exécutée par l'agent
  pour voir la sortie standard, la sortie d'erreur et le code de sortie.
- **Suivi** : si le résultat n'est pas celui que vous souhaitiez, répondez dans
  la même conversation avec une correction. L'agent conserve le contexte
  antérieur et itère sur les mêmes fichiers.

Par exemple, si le test n'a pas affiché le message d'accueil attendu, répondez :

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

L'agent relira le fichier, exécutera la commande, diagnostiquera le problème et
modifiera de nouveau le fichier — le tout dans la même conversation.
## Dépannage

<!-- @os:linux -->
- **`agent-canvas` n'est pas dans le PATH :** réinstallez avec
  `npm install -g @openhands/agent-canvas` et confirmez que le répertoire
  binaire global de npm se trouve dans votre PATH avant que `agent-canvas`
  puisse être lancé à partir d'un nouveau terminal.
- **`npm install -g` échoue avec une erreur de permissions :** configurez un
  répertoire global npm appartenant à l'utilisateur, puis rouvrez le terminal
  et installez de nouveau Agent Canvas.

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
- **`uv` est absent :** installez-le à partir
  [du guide d'installation de uv](https://docs.astral.sh/uv/getting-started/installation/).
  Agent Canvas utilise `uv` pour gérer l'environnement Python du serveur d'agent.
<!-- @os:end -->

<!-- @os:windows -->
- **`docker pull` ou `docker run` échoue à se connecter :** assurez-vous que
  Docker Desktop est en cours d'exécution (son icône de baleine se trouve dans
  la barre système) et que le moteur a terminé son démarrage. `docker version`
  devrait afficher à la fois une section Client et une section Server.
- **Le conteneur démarre, mais le serveur dorsal ne devient jamais sain :** le
  premier lancement initialise le serveur d'agent à l'intérieur du conteneur;
  laissez-lui une minute ou deux, puis vérifiez `docker logs <container>` pour
  détecter des erreurs.
- **Le conteneur ne parvient pas à joindre Lemonade :** le conteneur atteint
  l'hôte par l'intermédiaire de `host.docker.internal`. Confirmez que
  Lemonade est bien servi sur l'hôte Windows avec `lemonade status`, et
  utilisez `http://host.docker.internal:13305/api/v1` comme URL de base lors
  de la configuration du LLM.
<!-- @os:end -->

- **L'interface utilisateur se charge, mais le serveur dorsal indique qu'il
  n'est pas sain :** attendez une minute ou deux que le serveur d'agent
  termine son démarrage, puis actualisez. S'il reste non sain, redémarrez la
  pile et vérifiez les journaux pour détecter des erreurs.
- **Les requêtes de clavardage Lemonade échouent avec une erreur de
  connexion :** confirmez que
  `curl -fsS "http://127.0.0.1:13305/api/v1/health"` réussit et que Lemonade
  sert toujours le modèle avec `lemonade status`.
- **L'agent échoue avec un message concernant la longueur de contexte ou la
  limite de jetons :** amorcez une nouvelle conversation pour que l'agent ne
  conserve pas un historique trop volumineux. Si le problème persiste,
  redémarrez Lemonade avec une valeur `ctx_size` plus grande que la valeur par
  défaut de 65536 (par exemple `ctx_size=131072`), si la mémoire le permet.
- **L'agent produit des modifications de mauvaise qualité ou incomplètes :**
  passez à un modèle plus grand dans Lemonade, ou confiez à l'agent une tâche
  plus petite et plus concrète, et laissez-le la terminer avant de demander le
  changement suivant.

## Prochaines étapes

- Essayez une tâche plus importante dans le même espace de travail, comme
  l'ajout d'un fichier de test unitaire ou la correction d'un bogue connu, et
  passez en revue le diff de l'agent avant de conserver la modification.
- Connectez un serveur MCP tel que GitHub ou Slack dans **Personnaliser** afin
  que l'agent puisse lire des problèmes (issues) ou publier des mises à jour
  pendant qu'il travaille.
- Enregistrez plusieurs profils LLM (un petit modèle rapide et un grand modèle
  plus puissant) et passez de l'un à l'autre avec `/model` en cours de
  conversation.
- Passez aux [automatisations OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview)
  pour transformer les boucles de développement récurrentes en exécutions
  d'agent planifiées ou déclenchées par des événements.

## Ressources

- [Documentation OpenHands](https://docs.openhands.dev/)
- [Aperçu d'Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Configuration d'Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [Profils LLM et configuration des modèles](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [Documentation de Lemonade Server](https://lemonade-server.ai/docs)

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