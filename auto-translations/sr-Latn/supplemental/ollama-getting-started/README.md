<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Pregled

Ollama je popularan lagani alat za lokalno pokretanje velikih jezičkih modela. Upravlja preuzimanjem modela, kvantizacijom i posluživanjem putem jednostavnog interfejsa komandne linije i desktop aplikacije, tako da možete početi da razgovarate sa LLM-om za samo nekoliko minuta.

Ovaj playbook vas vodi kroz instalaciju Ollame, preuzimanje GPT-OSS 20B modela i razgovor s njim, kako putem terminala tako i putem desktop aplikacije.

## Šta ćete naučiti

- Kako da instalirate i pokrenete Ollamu na svom sistemu
- Kako da preuzmete i pokrenete GPT-OSS 20B model lokalno
- Kako da razgovarate sa modelima koristeći CLI
- Kako da programski upućujete upite modelima putem REST API-ja

## Podešavanje konfiguracije memorije

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Proverite softverska ažuriranja
> **Napomena**: Ako VS Code nije instaliran, možete ga instalirati putem Ryzen AI Developer Center-a.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalacija softverskih preduslova

<!-- @require:driver -->

### Instalacija Ollame

<!-- @os:windows -->

1. Preuzmite instalacioni program sa [ollama.com/download](https://ollama.com/download).
2. Pokrenite `.exe` instalacioni program i pratite uputstva.
3. Nakon instalacije, Ollama radi kao pozadinska usluga i dostupna je iz terminala, desktop aplikacije i sistemske trake.

Proverite instalaciju otvaranjem terminala i pokretanjem:

```powershell
ollama --version
```

<!-- @test:id=ollama-version-windows timeout=60 hidden=True -->
```powershell
ollama --version
```
<!-- @test:end -->

Trebalo bi da vidite broj instalirane verzije ispisane u konzoli.
<!-- @os:end -->

<!-- @os:linux -->

Pokrenite zvanični instalacioni skript:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Proverite instalaciju:

```bash
ollama --version
```

<!-- @test:id=ollama-version-linux timeout=60 hidden=True -->
```bash
ollama --version
```
<!-- @test:end -->

Trebalo bi da vidite broj instalirane verzije ispisane u konzoli.
<!-- @os:end -->

## Preuzimanje prvog modela

Ollama upravlja modelima putem registra sličnog kontejnerskim slikama. Da biste preuzeli GPT-OSS 20B:

```bash
ollama pull gpt-oss:20b
```

Ovo preuzima težine modela na vaš lokalni računar (otprilike 12 GB). Preuzimanje se dešava samo jednom, a naredna pokretanja učitavaju model sa diska.

Možete potvrditi da je model dostupan sa:

```bash
ollama list
```

Trebalo bi da vidite `gpt-oss:20b` u izlazu zajedno sa veličinom i datumom poslednje izmene.

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

### Imenovanje modela

Nazivi Ollama modela prate format `name:tag`. Oznaka obično ukazuje na broj parametara ili varijantu kvantizacije. Neki korisni komandi za upravljanje modelima:

| Komanda | Opis |
|---------|-------------|
| `ollama list` | Prikazuje sve preuzete modele |
| `ollama pull <model>` | Preuzima model bez pokretanja |
| `ollama rm <model>` | Uklanja model radi oslobađanja prostora na disku |
| `ollama show <model>` | Prikazuje metapodatke i parametre modela |

## Razgovor iz terminala

Pokrenite interaktivnu sesiju razgovora direktno iz komandne linije:

```bash
ollama run gpt-oss:20b
```

Ollama učitava model u memoriju i otvara prompt. Pokušajte da ga nešto pitate:

```
>>> What is the capital of France and why is it historically significant?
```

Model strimuje svoj odgovor token po token direktno u terminalu. Ukucajte `/bye` ili pritisnite `Ctrl+D` da biste izašli iz sesije.

> **Savet**: Prvo pokretanje traje nekoliko sekundi dok se model učitava u memoriju. Naredni promptovi unutar iste sesije odgovaraju mnogo brže jer model ostaje učitan.

<!-- @os:windows -->
## Razgovor putem desktop aplikacije

Ollama takođe dolazi sa desktop aplikacijom koja pruža čist interfejs za razgovor sa vašim modelima.

Otvorite **Ollama** iz Start menija ili kliknite na Ollama ikonu u sistemskoj traci i izaberite **Open Ollama**.

Kada se aplikacija otvori:

1. Kliknite na **New Chat** u bočnoj traci.
2. Izaberite **gpt-oss:20b** iz padajućeg menija modela u donjem desnom uglu oblasti za unos poruke.
3. Ukucajte poruku i pritisnite Enter da biste počeli razgovor.

<p align="center">
  <img src="assets/ollama_app.png" alt="Ollama desktop app chatting with gpt-oss:20b" width="600"/>
</p>

Desktop aplikacija čuva istoriju vaših razgovora u bočnoj traci, što olakšava vraćanje na prethodne razgovore.
<!-- @os:end -->

## Korišćenje REST API-ja

Nakon instalacije, Ollama radi kao pozadinska usluga i izlaže REST API na `http://localhost:11434` koji možete koristiti za integraciju modela u sopstvene aplikacije i skripte.

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

### Generisanje odgovora u terminalu

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

Odgovor je JSON objekat koji sadrži izlaz modela u polju `response`.


### Primer u Python-u
Sada kada možemo programski da pristupamo Ollama API-ju, pozovimo ga iz Python-a.

#### Kreiranje virtuelnog okruženja u terminalu

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
#### Kreiranje Python fajla
U istom direktorijumu, koristite VS Code ili drugi editor da kreirate .py fajl i kopirajte sledeći kod u njega. Zatim pokrenite fajl u aktiviranom okruženju sa `python your_file_name.py`

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

### Ključni API endpointi

| Endpoint | Metoda | Svrha |
|----------|--------|---------|
| `/api/generate` | POST | Generisanje teksta u jednom koraku |
| `/api/chat` | POST | Višekorni razgovor sa istorijom poruka |
| `/api/tags` | GET | Lista dostupnih modela |
| `/api/show` | POST | Prikaz detalja modela |
| `/api/pull` | POST | Preuzimanje modela iz registra |

Za potpunu API referencu, pogledajte [Ollama API dokumentaciju](https://github.com/ollama/ollama/blob/main/docs/api.md).

## Sledeći koraci

- **Isprobajte različite modele**: Pregledajte [Ollama biblioteku modela](https://ollama.com/library) da biste istražili stotine dostupnih modela, od malih asistenta za kodiranje do velikih modela za rezonovanje.
- **Kreirajte prilagođene modele**: Koristite [Modelfile](https://github.com/ollama/ollama/blob/main/docs/modelfile.md) da postavite prilagođene sistemske promptove, temperaturu i druge parametre za prilagođeno iskustvo.
- **Gradite sa API-jem**: Koristite [Python](https://github.com/ollama/ollama-python) ili [JavaScript](https://github.com/ollama/ollama-js) klijentske biblioteke da integrirate Ollamu u vaše aplikacije.
- **Povežite se sa frontend alatima**: Kombinujte Ollamu sa alatima poput [Open WebUI](https://github.com/open-webui/open-webui) za bogat interfejs za razgovor sa pretragom, personama i otpremanjem dokumenata.

Za više informacija, pogledajte [Ollama dokumentaciju](https://github.com/ollama/ollama/blob/main/README.md).