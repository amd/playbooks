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

## Présentation

Ollama est un outil léger et populaire pour exécuter des grands modèles de langage en local. Il gère le téléchargement des modèles, la quantification et le service via une interface en ligne de commande simple et une application de bureau, ce qui vous permet de passer de rien à une conversation avec un LLM en quelques minutes.

Ce playbook vous guide à travers l'installation d'Ollama, le téléchargement du modèle GPT-OSS 20B et une conversation avec celui-ci, à la fois via le terminal et l'application de bureau.

## Ce que vous allez apprendre

- Comment installer et lancer Ollama sur votre système
- Télécharger et exécuter le modèle GPT-OSS 20B en local
- Discuter avec les modèles via la CLI
- Interroger les modèles par programmation via l'API REST

## Configuration de la mémoire

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Vérifier les mises à jour logicielles
> **Remarque** : Si VS Code n'est pas installé, vous pouvez l'installer avec Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Installation des prérequis logiciels

<!-- @require:driver -->

### Installation d'Ollama

<!-- @os:windows -->

1. Téléchargez l'installeur depuis [ollama.com/download](https://ollama.com/download).
2. Exécutez l'installeur `.exe` et suivez les instructions.
3. Une fois installé, Ollama s'exécute comme un service en arrière-plan et est accessible depuis le terminal, l'application de bureau et la barre d'état système.

Vérifiez l'installation en ouvrant un terminal et en exécutant :

```powershell
ollama --version
```

<!-- @test:id=ollama-version-windows timeout=60 hidden=True -->
```powershell
ollama --version
```
<!-- @test:end --> 

Vous devriez voir le numéro de version installé s'afficher dans la console.
<!-- @os:end -->

<!-- @os:linux -->

Exécutez le script d'installation officiel :

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Vérifiez l'installation :

```bash
ollama --version
```

<!-- @test:id=ollama-version-linux timeout=60 hidden=True -->
```bash
ollama --version
```
<!-- @test:end --> 

Vous devriez voir le numéro de version installé s'afficher dans la console.
<!-- @os:end -->

## Télécharger votre premier modèle

Ollama gère les modèles via un registre similaire aux images de conteneurs. Pour télécharger GPT-OSS 20B :

```bash
ollama pull gpt-oss:20b
```

Cette opération télécharge les poids du modèle sur votre machine locale (environ 12 Go). Le téléchargement n'a lieu qu'une seule fois, les exécutions suivantes chargent le modèle depuis le disque.

Vous pouvez confirmer que le modèle est disponible avec :

```bash
ollama list
```

Vous devriez voir `gpt-oss:20b` dans la sortie, accompagné de sa taille et de sa date de dernière modification.

<!-- @os:windows -->
<!-- @test:id=ollama-list-gpt-oss-20b-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"
$list = (ollama list | Out-String)
if (-not $list) { throw "ollama list returned no output" }
if ($list -notmatch 'gpt-oss:20b') { throw "Model gpt-oss:20b is not present in ollama list. Please download it before running this test." }
Write-Host "OK: gpt-oss:20b is present in ollama list"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=ollama-list-gpt-oss-20b-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
p=""
started_here="0"

cleanup() {
  if [ "$started_here" = "1" ] && [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null || true
    sleep 2
    kill -9 "$p" 2>/dev/null || true
  fi
}
trap cleanup EXIT

wait_for_ollama_api() {
  local attempts="${1:-120}"
  local out=""
  for i in $(seq 1 "$attempts"); do
    out="$(curl -s --max-time 2 http://127.0.0.1:11434/api/tags || true)"
    if [ -n "$out" ]; then
      echo "$out"
      return 0
    fi
    sleep 1
  done
  return 1
}

tags_json="$(wait_for_ollama_api 5 || true)"
if [ -z "$tags_json" ]; then
  ollama serve >/tmp/ollama-list-test.log 2>&1 &
  p=$!
  started_here="1"
  tags_json="$(wait_for_ollama_api 120 || true)"
fi
if [ -z "$tags_json" ]; then
  echo "Ollama API not ready on http://127.0.0.1:11434"
  exit 1
fi
echo "OK: Ollama API is responding on http://127.0.0.1:11434"

list="$(ollama list)"
if [ -z "$list" ]; then
  echo "ollama list returned no output"
  exit 1
fi
echo "$list" | grep -q 'gpt-oss:20b' || {
  echo "Model gpt-oss:20b is not present in ollama list. Please download it before running this test."
  exit 1
}
echo "OK: gpt-oss:20b is present in ollama list"
```
<!-- @test:end --> 
<!-- @os:end -->

### Nommage des modèles

Les noms de modèles Ollama suivent le format `nom:tag`. Le tag indique généralement le nombre de paramètres ou la variante de quantification. Voici quelques commandes utiles pour gérer les modèles :

| Commande | Description |
|---------|-------------|
| `ollama list` | Afficher tous les modèles téléchargés |
| `ollama pull <model>` | Télécharger un modèle sans l'exécuter |
| `ollama rm <model>` | Supprimer un modèle pour libérer de l'espace disque |
| `ollama show <model>` | Afficher les métadonnées et les paramètres du modèle |

## Discuter depuis le terminal

Lancez une session de discussion interactive directement depuis la ligne de commande :

```bash
ollama run gpt-oss:20b
```

Ollama charge le modèle en mémoire et vous place dans une invite. Essayez de lui poser une question :

```
>>> What is the capital of France and why is it historically significant?
```

Le modèle diffuse sa réponse jeton par jeton directement dans le terminal. Tapez `/bye` ou appuyez sur `Ctrl+D` pour quitter la session.

> **Astuce** : La première exécution prend quelques secondes pour charger le modèle en mémoire. Les invites suivantes au sein de la même session répondent beaucoup plus rapidement, car le modèle reste chargé.

<!-- @os:windows -->
## Discuter depuis l'application de bureau

Ollama est également fourni avec une application de bureau qui offre une interface de discussion épurée pour interagir avec vos modèles.

Ouvrez **Ollama** depuis le menu Démarrer ou cliquez sur l'icône Ollama dans la barre d'état système et sélectionnez **Open Ollama**.

Une fois l'application ouverte :

1. Cliquez sur **New Chat** dans la barre latérale.
2. Sélectionnez **gpt-oss:20b** dans le menu déroulant des modèles, en bas à droite de la zone de saisie de la discussion.
3. Tapez un message et appuyez sur Entrée pour commencer à discuter.

<p align="center">
  <img src="assets/ollama_app.png" alt="Ollama desktop app chatting with gpt-oss:20b" width="600"/>
</p>

L'application de bureau conserve un historique de vos conversations dans la barre latérale, ce qui facilite la consultation des discussions précédentes.
<!-- @os:end -->

## Utilisation de l'API REST

Après l'installation, Ollama s'exécute comme un service en arrière-plan et expose une API REST sur `http://localhost:11434` que vous pouvez utiliser pour intégrer des modèles dans vos propres applications et scripts.

<!-- @os:windows -->
<!-- @test:id=ollama-smoke-windows timeout=1800 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$p = $null
$startedHere = $false
$tmpShow = $null
$tmpGenerate = $null
$tmpChat = $null
$venv = "$PWD\ollama-env-ci"
$pythonSmoke = "$PWD\ollama_python_smoke.py" 

function Wait-OllamaApi {
  param( [int]$MaxAttempts = 120 )
  $resp = $null
  for ($i = 0; $i -lt $MaxAttempts; $i++) {
    $resp = curl.exe -s --max-time 2 http://127.0.0.1:11434/api/tags
    if ($LASTEXITCODE -eq 0 -and $resp) { return $resp }
    Start-Sleep -Seconds 1
  }
  return $null
}

try {
  # If Ollama API is not already up, start it.
  $tagsJson = Wait-OllamaApi -MaxAttempts 5
  if (-not $tagsJson) {
    $p = Start-Process -FilePath "ollama" -ArgumentList "serve" -NoNewWindow -PassThru
    $startedHere = $true
    $tagsJson = Wait-OllamaApi -MaxAttempts 120
  }
  if (-not $tagsJson) { throw "Ollama API not ready on http://127.0.0.1:11434" }
  Write-Host "OK: Ollama API is responding on http://127.0.0.1:11434"

  # /api/tags must include gpt-oss:20b
  $tags = $tagsJson | ConvertFrom-Json
  $model = $tags.models | Where-Object { $_.name -eq "gpt-oss:20b" } | Select-Object -First 1
  if (-not $model) { throw "Model gpt-oss:20b is not present in /api/tags. Please download it before running this test." }
  Write-Host "OK: gpt-oss:20b is present in /api/tags"

  # /api/show should return model metadata
  $showBody = @{ name = "gpt-oss:20b" } | ConvertTo-Json
  $tmpShow = Join-Path $env:TEMP "ollama-show-body.json"
  [System.IO.File]::WriteAllText($tmpShow, $showBody, [System.Text.UTF8Encoding]::new($false))
  $showOut = curl.exe -sS --fail-with-body --max-time 60 http://127.0.0.1:11434/api/show `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpShow"
  if (-not $showOut) { throw "Empty response from /api/show" }
  $showJson = $showOut | ConvertFrom-Json
  if (-not $showJson.details) { throw "/api/show did not return model details for gpt-oss:20b" }
  Write-Host "OK: /api/show returned model details"

  # CLI inference smoke
  $cliOut = & ollama run gpt-oss:20b "Reply with exactly OK"
  if (-not $cliOut) { throw "ollama run returned empty output" }
  $cliText = ($cliOut | Out-String).Trim()
  if ($cliText -notmatch '(^|\s)OK(\s|$)') { throw "ollama run did not return OK. Output was: $cliText" }
  Write-Host "OK: ollama run inference works"

  # /api/generate smoke
  $generateBody = @{
    model  = "gpt-oss:20b"
    prompt = "Reply with exactly OK"
    stream = $false
  } | ConvertTo-Json
  $tmpGenerate = Join-Path $env:TEMP "ollama-generate-body.json"
  [System.IO.File]::WriteAllText($tmpGenerate, $generateBody, [System.Text.UTF8Encoding]::new($false))
  $generateOut = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:11434/api/generate `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpGenerate"
  if (-not $generateOut) { throw "Empty response from /api/generate" }
  $generateJson = $generateOut | ConvertFrom-Json
  if (-not $generateJson.response) { throw "/api/generate did not return a response field" }
  if ($generateJson.response.Trim() -ne "OK") { throw "/api/generate expected exactly OK but got: $($generateJson.response)" }
  Write-Host "OK: /api/generate works"

  # /api/chat smoke
  $chatBody = @{
    model = "gpt-oss:20b"
    messages = @(
      @{
        role = "user"
        content = "Reply with exactly OK"
      }
    )
    stream = $false
  } | ConvertTo-Json -Depth 5
  $tmpChat = Join-Path $env:TEMP "ollama-chat-body.json"
  [System.IO.File]::WriteAllText($tmpChat, $chatBody, [System.Text.UTF8Encoding]::new($false))
  $chatOut = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:11434/api/chat `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpChat"
  if (-not $chatOut) { throw "Empty response from /api/chat" }
  $chatJson = $chatOut | ConvertFrom-Json
  $chatText = $chatJson.message.content
  if (-not $chatText) { throw "/api/chat did not return message.content" }
  if ($chatText.Trim() -ne "OK") { throw "/api/chat expected exactly OK but got: $chatText" }
  Write-Host "OK: /api/chat works"

  # Python requests smoke
  if (Test-Path $venv) { Remove-Item -Recurse -Force $venv }
  python -m venv $venv
  $py = Join-Path $venv "Scripts\python.exe"
  & $py -m pip install --upgrade pip
  & $py -m pip install requests
@'
import requests
response = requests.post(
    "http://127.0.0.1:11434/api/generate",
    json={
        "model": "gpt-oss:20b",
        "prompt": "Reply with exactly: OK",
        "stream": False,
    },
    timeout=300,
)
response.raise_for_status()
text = response.json()["response"].strip()
if text != "OK":
    raise SystemExit(f"Expected exactly OK, got: {text}")
print("OK: Python requests example works")
'@ | Set-Content -Path $pythonSmoke -Encoding UTF8
  & $py $pythonSmoke
}

finally {
  Remove-Item $tmpShow, $tmpGenerate, $tmpChat, $pythonSmoke -Force -ErrorAction SilentlyContinue
  Remove-Item $venv -Recurse -Force -ErrorAction SilentlyContinue
  if ($startedHere) {
    if ($p -and -not $p.HasExited) {
      Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
    }
  }
}
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=ollama-smoke-linux timeout=1800 hidden=True -->
```bash
set -euo pipefail
p=""
started_here="0"
venv="./ollama-env-ci"
python_smoke="./ollama_python_smoke.py" 

cleanup() {
  rm -f "$python_smoke"
  rm -rf "$venv"
  if [ "$started_here" = "1" ] && [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null || true
    sleep 2
    kill -9 "$p" 2>/dev/null || true
  fi
}
trap cleanup EXIT

wait_for_ollama_api() {
  local attempts="${1:-120}"
  local out=""
  for i in $(seq 1 "$attempts"); do
    out="$(curl -s --max-time 2 http://127.0.0.1:11434/api/tags || true)"
    if [ -n "$out" ]; then
      echo "$out"
      return 0
    fi
    sleep 1
  done
  return 1
}

tags_json="$(wait_for_ollama_api 5 || true)"
if [ -z "$tags_json" ]; then
  ollama serve >/tmp/ollama-test.log 2>&1 &
  p=$!
  started_here="1"
  tags_json="$(wait_for_ollama_api 120 || true)"
fi
if [ -z "$tags_json" ]; then
  echo "Ollama API not ready on http://127.0.0.1:11434"
  exit 1
fi
echo "OK: Ollama API is responding on http://127.0.0.1:11434"

export TAGS_JSON="$tags_json"
python3 - <<'PY'
import json
import os
import sys
data = json.loads(os.environ["TAGS_JSON"])
models = data.get("models", [])
for item in models:
    if item.get("name") == "gpt-oss:20b":
        print("OK: gpt-oss:20b is present in /api/tags")
        sys.exit(0)
print("Model gpt-oss:20b is not present in /api/tags. Please download it before running this test.")
sys.exit(1)
PY

show_out="$(curl -s --max-time 60 http://127.0.0.1:11434/api/show \
  -H "Content-Type: application/json" \
  -d '{"name":"gpt-oss:20b"}' || true)"
if [ -z "$show_out" ]; then
  echo "Empty response from /api/show"
  exit 1
fi
export SHOW_OUT="$show_out"
python3 - <<'PY'
import json
import os
import sys
data = json.loads(os.environ["SHOW_OUT"])
if not data.get("details"):
    print("/api/show did not return model details for gpt-oss:20b")
    sys.exit(1)
print("OK: /api/show returned model details")
PY

cli_out="$(ollama run gpt-oss:20b "Reply with exactly OK" || true)"
if [ -z "$cli_out" ]; then
  echo "ollama run returned empty output"
  exit 1
fi
export CLI_OUT="$cli_out"
python3 - <<'PY'
import os
import sys
text = os.environ["CLI_OUT"].strip()
if "OK" not in text.split():
    print(f"ollama run did not return OK. Output was: {text}")
    sys.exit(1)
print("OK: ollama run inference works")
PY

generate_out="$(curl -s --max-time 300 http://127.0.0.1:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-oss:20b","prompt":"Reply with exactly OK","stream":false}' || true)"
if [ -z "$generate_out" ]; then
  echo "Empty response from /api/generate"
  exit 1
fi
export GENERATE_OUT="$generate_out"
python3 - <<'PY'
import json
import os
import sys
data = json.loads(os.environ["GENERATE_OUT"])
text = data.get("response", "")
if not text:
    print("/api/generate did not return a response field")
    sys.exit(1)
if text.strip() != "OK":
    print(f"/api/generate expected exactly OK but got: {text}")
    sys.exit(1)
print("OK: /api/generate works")
PY

chat_out="$(curl -s --max-time 300 http://127.0.0.1:11434/api/chat \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-oss:20b","messages":[{"role":"user","content":"Reply with exactly OK"}],"stream":false}' || true)"
if [ -z "$chat_out" ]; then
  echo "Empty response from /api/chat"
  exit 1
fi
export CHAT_OUT="$chat_out"
python3 - <<'PY'
import json
import os
import sys
data = json.loads(os.environ["CHAT_OUT"])
msg = data.get("message", {})
text = msg.get("content", "")
if not text:
    print("/api/chat did not return message.content")
    sys.exit(1)
if text.strip() != "OK":
    print(f"/api/chat expected exactly OK but got: {text}")
    sys.exit(1)
print("OK: /api/chat works")
PY

rm -rf "$venv"
python3 -m venv "$venv"
py="$venv/bin/python"
"$py" -m pip install --upgrade pip
"$py" -m pip install requests
cat > "$python_smoke" <<'PY'
import requests
response = requests.post(
    "http://127.0.0.1:11434/api/generate",
    json={
        "model": "gpt-oss:20b",
        "prompt": "Reply with exactly: OK",
        "stream": False,
    },
    timeout=300,
)
response.raise_for_status()
text = response.json()["response"].strip()
if text != "OK":
    raise SystemExit(f"Expected exactly OK, got: {text}")
print("OK: Python requests example works")
PY
"$py" "$python_smoke"
```
<!-- @test:end --> 
<!-- @os:end -->

### Générer une réponse dans le terminal

<!-- @os:linux -->
```bash
curl http://localhost:11434/api/generate -d '{"model": "gpt-oss:20b", "prompt": "Explain GPU acceleration in two sentences.", "stream": false}'
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
curl.exe http://localhost:11434/api/generate -d '{"model": "gpt-oss:20b", "prompt": "Explain GPU acceleration in two sentences.", "stream": false}'
```
<!-- @os:end -->

La réponse est un objet JSON contenant la sortie du modèle dans le champ `response`.


### Exemple Python
Maintenant que nous pouvons appeler l'API Ollama par programmation, appelons-la depuis Python.

#### Créer un environnement virtuel dans le terminal

<!-- @os:linux -->
```bash
sudo apt install -y python3-venv
python3 -m venv ollama-env
source ollama-env/bin/activate
pip install requests
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
python -m venv ollama-env
ollama-env\Scripts\activate
pip install requests
```
<!-- @os:end -->
#### Créer un fichier Python
Dans le même répertoire, utilisez VS Code ou un autre éditeur pour créer un fichier .py et copiez-y le code suivant. Ensuite, exécutez le fichier dans votre environnement activé avec `python your_file_name.py`

```python
import requests

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "gpt-oss:20b",
        "prompt": "Write a haiku about local AI inference.",
        "stream": False,
    },
)

print(response.json()["response"])
```

### Principaux points de terminaison de l'API

| Point de terminaison | Méthode | Objectif |
|----------|--------|---------|
| `/api/generate` | POST | Génération de texte en un seul tour |
| `/api/chat` | POST | Conversation multi-tours avec historique des messages |
| `/api/tags` | GET | Lister les modèles disponibles |
| `/api/show` | POST | Afficher les détails du modèle |
| `/api/pull` | POST | Télécharger un modèle depuis le registre |

Pour la référence complète de l'API, consultez la [documentation de l'API Ollama](https://github.com/ollama/ollama/blob/main/docs/api.md).
## Prochaines étapes

- **Essayez différents modèles** : parcourez la [bibliothèque de modèles Ollama](https://ollama.com/library) pour explorer des centaines de modèles disponibles, des petits assistants de codage aux grands modèles de raisonnement.
- **Créez des modèles personnalisés** : utilisez un [Modelfile](https://github.com/ollama/ollama/blob/main/docs/modelfile.md) pour définir des invites système personnalisées, la température et d'autres paramètres afin d'obtenir une expérience sur mesure.
- **Développez avec l'API** : utilisez les bibliothèques clientes [Python](https://github.com/ollama/ollama-python) ou [JavaScript](https://github.com/ollama/ollama-js) pour intégrer Ollama à vos applications.
- **Connectez-vous à des interfaces frontales** : associez Ollama à des outils comme [Open WebUI](https://github.com/open-webui/open-webui) pour bénéficier d'une interface de chat riche en fonctionnalités, avec recherche, personas et téléversement de documents.

Pour plus d'informations, consultez la [documentation Ollama](https://github.com/ollama/ollama/blob/main/README.md).