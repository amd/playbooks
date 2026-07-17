<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Áttekintés

Az Ollama egy népszerű, könnyűsúlyú eszköz nagy nyelvi modellek helyi futtatásához. Kezeli a modellek letöltését, kvantálását és kiszolgálását egy egyszerű parancssori felületen és asztali alkalmazáson keresztül, így percek alatt elkezdhetsz csevegni egy LLM-mel.

Ez a playbook végigvezet az Ollama telepítésén, a GPT-OSS 20B modell letöltésén és egy beszélgetés folytatásán – mind a terminálon, mind az asztali alkalmazáson keresztül.

## Mit fogsz megtanulni

- Hogyan telepítsd és indítsd el az Ollama-t a rendszereden
- A GPT-OSS 20B modell helyi letöltése és futtatása
- Csevegés modellekkel a CLI segítségével
- Modellek programozott lekérdezése a REST API-n keresztül

## A memóriakonfiguráció beállítása

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Szoftverfrissítések ellenőrzése
> **Megjegyzés**: Ha a VS Code nincs telepítve, a Ryzen AI Developer Center segítségével telepítheted.

<!-- @require:software-update -->
<!-- @device:end -->

## Szoftver-előfeltételek telepítése

<!-- @require:driver -->

### Az Ollama telepítése

<!-- @os:windows -->

1. Töltsd le a telepítőt az [ollama.com/download](https://ollama.com/download) oldalról.
2. Futtasd a `.exe` telepítőt, és kövesd az utasításokat.
3. A telepítés után az Ollama háttérszolgáltatásként fut, és elérhető a terminálból, az asztali alkalmazásból és a rendszertálcáról.

Ellenőrizd a telepítést egy terminál megnyitásával és a következő parancs futtatásával:

```powershell
ollama --version
```

<!-- @test:id=ollama-version-windows timeout=60 hidden=True -->
```powershell
ollama --version
```
<!-- @test:end --> 

A konzolon megjelenik a telepített verziószám.
<!-- @os:end -->

<!-- @os:linux -->

Futtasd a hivatalos telepítő szkriptet:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Ellenőrizd a telepítést:

```bash
ollama --version
```

<!-- @test:id=ollama-version-linux timeout=60 hidden=True -->
```bash
ollama --version
```
<!-- @test:end --> 

A konzolon megjelenik a telepített verziószám.
<!-- @os:end -->

## Az első modell letöltése

Az Ollama a modelleket egy konténerképekhez hasonló nyilvántartáson keresztül kezeli. A GPT-OSS 20B letöltéséhez:

```bash
ollama pull gpt-oss:20b
```

Ez letölti a modell súlyait a helyi gépedre (körülbelül 12 GB). A letöltés csak egyszer történik meg, a következő futtatások a modellt lemezről töltik be.

A modell elérhetőségét a következővel ellenőrizheted:

```bash
ollama list
```

A kimenetben látni fogod a `gpt-oss:20b` bejegyzést a méretével és az utolsó módosítás dátumával együtt.

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

### Modellnevezési konvenciók

Az Ollama modellnevei a `name:tag` formátumot követik. A tag általában a paraméterszámot vagy a kvantálási változatot jelzi. Néhány hasznos parancs a modellek kezeléséhez:

| Parancs | Leírás |
|---------|-------------|
| `ollama list` | Az összes letöltött modell megjelenítése |
| `ollama pull <model>` | Modell letöltése futtatás nélkül |
| `ollama rm <model>` | Modell eltávolítása a lemezterület felszabadításához |
| `ollama show <model>` | Modell metaadatainak és paramétereinek megjelenítése |

## Csevegés a terminálból

Indíts interaktív csevegési munkamenetet közvetlenül a parancssorból:

```bash
ollama run gpt-oss:20b
```

Az Ollama betölti a modellt a memóriába, és egy prompthoz juttat. Próbálj meg valamit kérdezni:

```
>>> What is the capital of France and why is it historically significant?
```

A modell token-ről tokenre streameli a választ közvetlenül a terminálban. A munkamenet befejezéséhez írd be a `/bye` parancsot, vagy nyomj `Ctrl+D` billentyűkombinációt.

> **Tipp**: Az első futtatás néhány másodpercet vesz igénybe a modell memóriába töltéséhez. Az ugyanazon munkameneten belüli következő promptok sokkal gyorsabban válaszolnak, mivel a modell betöltve marad.

<!-- @os:windows -->
## Csevegés az asztali alkalmazásból

Az Ollama egy asztali alkalmazással is rendelkezik, amely tiszta csevegési felületet biztosít a modellekkel való interakcióhoz.

Nyisd meg az **Ollama** alkalmazást a Start menüből, vagy kattints az Ollama ikonra a rendszertálcán, és válaszd az **Open Ollama** lehetőséget.

Miután az alkalmazás megnyílt:

1. Kattints az **New Chat** gombra az oldalsávban.
2. Válaszd a **gpt-oss:20b** modellt a csevegési beviteli terület jobb alsó sarkában lévő modell legördülő menüből.
3. Írj be egy üzenetet, és nyomj Entert a csevegés megkezdéséhez.

<p align="center">
  <img src="assets/ollama_app.png" alt="Ollama desktop app chatting with gpt-oss:20b" width="600"/>
</p>

Az asztali alkalmazás az oldalsávban tárolja a beszélgetések előzményeit, így könnyen visszatérhetsz a korábbi csevegésekhez.
<!-- @os:end -->

## A REST API használata

A telepítés után az Ollama háttérszolgáltatásként fut, és egy REST API-t tesz elérhetővé a `http://localhost:11434` címen, amelyet saját alkalmazásaidba és szkriptjeidbe integrálhatsz.

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

### Válasz generálása a terminálban

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

A válasz egy JSON objektum, amely a modell kimenetét tartalmazza a `response` mezőben.


### Python példa
Most, hogy programozottan is elérhetjük az Ollama API-t, hívjuk meg Pythonból.

#### Virtuális környezet létrehozása a terminálban

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
#### Python fájl létrehozása
Ugyanabban a könyvtárban használd a VS Code-ot vagy egy másik szerkesztőt egy .py fájl létrehozásához, és másold bele az alábbi kódot. Ezután futtasd a fájlt az aktivált környezetedben a `python your_file_name.py` paranccsal.

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

### Főbb API végpontok

| Végpont | Metódus | Cél |
|----------|--------|---------|
| `/api/generate` | POST | Egylépéses szöveggenerálás |
| `/api/chat` | POST | Többlépéses beszélgetés üzenettörténettel |
| `/api/tags` | GET | Elérhető modellek listázása |
| `/api/show` | POST | Modell részleteinek megjelenítése |
| `/api/pull` | POST | Modell letöltése a nyilvántartásból |

A teljes API-referenciáért lásd az [Ollama API dokumentációját](https://github.com/ollama/ollama/blob/main/docs/api.md).

## Következő lépések

- **Próbálj ki különböző modelleket**: Böngészd az [Ollama modellkönyvtárát](https://ollama.com/library), ahol több száz elérhető modellt fedezhetsz fel, a kis kódolási asszisztensektől a nagy érvelési modellekig.
- **Hozz létre egyéni modelleket**: Használj egy [Modelfile](https://github.com/ollama/ollama/blob/main/docs/modelfile.md) fájlt egyéni rendszerpromptok, hőmérséklet és egyéb paraméterek beállításához a személyre szabott élmény érdekében.
- **Fejlessz az API-val**: Használd a [Python](https://github.com/ollama/ollama-python) vagy [JavaScript](https://github.com/ollama/ollama-js) klienskönyvtárakat az Ollama alkalmazásaidba való integrálásához.
- **Csatlakozz frontend eszközökhöz**: Párosítsd az Ollama-t olyan eszközökkel, mint az [Open WebUI](https://github.com/open-webui/open-webui), egy funkciógazdag csevegési felületért kereséssel, személyiségekkel és dokumentumfeltöltéssel.

További információkért tekintsd meg az [Ollama dokumentációját](https://github.com/ollama/ollama/blob/main/README.md).