<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový překlad.** Tato stránka byla automaticky přeložena z angličtiny a nebyla zkontrolována člověkem. Může obsahovat chyby a určité pokyny, příkazy, soubory ke stažení, dostupnost produktů nebo jiný obsah se může lišit podle jazyka nebo regionu. V případě jakéhokoli nesouladu nebo rozporu je rozhodující původní anglická verze playbooku.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Přehled

Ollama je oblíbený lehký nástroj pro lokální spouštění velkých jazykových modelů. Zajišťuje stahování modelů, kvantizaci a jejich zpřístupnění prostřednictvím jednoduchého rozhraní příkazové řádky a desktopové aplikace, takže se během několika minut dostanete od nuly k chatování s LLM.

Tento playbook vás provede instalací Ollama, stažením modelu GPT-OSS 20B a konverzací s ním, a to jak z terminálu, tak z desktopové aplikace.

## Co se naučíte

- Jak nainstalovat a spustit Ollama ve vašem systému
- Jak stáhnout a spustit model GPT-OSS 20B lokálně
- Jak chatovat s modely pomocí CLI
- Jak dotazovat modely programově přes REST API

## Nastavení konfigurace paměti

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Zkontrolujte aktualizace softwaru
> **Poznámka**: Pokud nemáte nainstalovaný VS Code, můžete jej nainstalovat pomocí Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalace softwarových předpokladů

<!-- @require:driver -->

### Instalace Ollama

<!-- @os:windows -->

1. Stáhněte instalační program z [ollama.com/download](https://ollama.com/download).
2. Spusťte instalační program `.exe` a postupujte podle pokynů.
3. Po instalaci běží Ollama jako služba na pozadí a je přístupná z terminálu, desktopové aplikace i systémové lišty.

Ověřte instalaci otevřením terminálu a spuštěním:

```powershell
ollama --version
```

<!-- @test:id=ollama-version-windows timeout=60 hidden=True -->
```powershell
ollama --version
```
<!-- @test:end --> 

Na konzoli by se mělo zobrazit číslo nainstalované verze.
<!-- @os:end -->

<!-- @os:linux -->

Spusťte oficiální instalační skript:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Ověřte instalaci:

```bash
ollama --version
```

<!-- @test:id=ollama-version-linux timeout=60 hidden=True -->
```bash
ollama --version
```
<!-- @test:end --> 

Na konzoli by se mělo zobrazit číslo nainstalované verze.
<!-- @os:end -->

## Stažení prvního modelu

Ollama spravuje modely prostřednictvím registru podobného kontejnerovým obrazům. Chcete-li stáhnout GPT-OSS 20B:

```bash
ollama pull gpt-oss:20b
```

Tím se stáhnou váhy modelu na váš lokální počítač (přibližně 12 GB). Ke stažení dojde pouze jednou, další spuštění pak model načtou z disku.

Dostupnost modelu můžete ověřit pomocí:

```bash
ollama list
```

V. výstupu by se měl zobrazit `gpt-oss:20b` spolu s jeho velikostí a datem poslední úpravy.

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

### Pojmenování modelů

Názvy modelů Ollama mají formát `name:tag`. Tag obvykle udává počet parametrů nebo variantu kvantizace. Několik užitečných příkazů pro správu modelů:

| Příkaz | Popis |
|---------|-------------|
| `ollama list` | Zobrazí všechny stažené modely |
| `ollama pull <model>` | Stáhne model bez jeho spuštění |
| `ollama rm <model>` | Odstraní model a uvolní místo na disku |
| `ollama show <model>` | Zobrazí metadata a parametry modelu |

## Chatování z terminálu

Spusťte interaktivní chatovací relaci přímo z příkazové řádky:

```bash
ollama run gpt-oss:20b
```

Ollama načte model do paměti a přesune vás do promptu. Zkuste se ho na něco zeptat:

```
>>> What is the capital of France and why is it historically significant?
```

Model streamuje svou odpověď token po tokenu přímo v terminálu. Chcete-li relaci ukončit, zadejte `/bye` nebo stiskněte `Ctrl+D`.

> **Tip**: První spuštění trvá několik sekund, než se model načte do paměti. Další prompty v rámci stejné relace reagují mnohem rychleji, protože model zůstává načtený.

<!-- @os:windows -->
## Chatování z desktopové aplikace

Ollama je také dodávána s desktopovou aplikací, která poskytuje přehledné chatovací rozhraní pro interakci s vašimi modely.

Otevřete **Ollama** z nabídky Start nebo klikněte na ikonu Ollama v systémové liště a vyberte **Open Ollama**.

Po otevření aplikace:

1. Klikněte na **New Chat** v postranním panelu.
2. Vyberte **gpt-oss:20b** z rozbalovací nabídky modelu v pravém dolním rohu oblasti pro zadávání zprávy.
3. Napište zprávu a stisknutím klávesy Enter zahajte konverzaci.

<p align="center">
  <img src="assets/ollama_app.png" alt="Ollama desktop app chatting with gpt-oss:20b" width="600"/>
</p>

Desktopová aplikace uchovává historii vašich konverzací v postranním panelu, takže se k předchozím chatům snadno vrátíte.
<!-- @os:end -->

## Používání REST API

Po instalaci běží Ollama jako služba na pozadí a zpřístupňuje REST API na adrese `http://localhost:11434`, které můžete využít k integraci modelů do vlastních aplikací a skriptů.

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

### Vygenerování odpovědi v terminálu

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

Odpovědí je objekt JSON obsahující výstup modelu v poli `response`.


### Příklad v Pythonu
Nyní, když můžeme volat API Ollama programově, si ho zavoláme z Pythonu.

#### Vytvoření virtuálního prostředí v terminálu

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
#### Vytvoření souboru v Pythonu
Ve stejném adresáři použijte VS Code nebo jiný editor a vytvořte soubor .py, do kterého zkopírujete následující kód. Poté soubor spusťte ve svém aktivovaném prostředí pomocí `python your_file_name.py`

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

### Klíčové koncové body API

| Koncový bod | Metoda | Účel |
|----------|--------|---------|
| `/api/generate` | POST | Generování textu v jedné konverzační relaci |
| `/api/chat` | POST | Vícekolová konverzace s historií zpráv |
| `/api/tags` | GET | Seznam dostupných modelů |
| `/api/show` | POST | Zobrazení podrobností o modelu |
| `/api/pull` | POST | Stažení modelu z registru |

Úplnou dokumentaci API najdete v [dokumentaci API Ollama](https://github.com/ollama/ollama/blob/main/docs/api.md).
## Další kroky

- **Vyzkoušejte různé modely**: Prohlédněte si [knihovnu modelů Ollama](https://ollama.com/library) a objevte stovky dostupných modelů, od malých asistentů pro programování až po velké modely pro pokročilé uvažování.
- **Vytvořte vlastní modely**: Použijte [Modelfile](https://github.com/ollama/ollama/blob/main/docs/modelfile.md) k nastavení vlastních systémových promptů, teploty a dalších parametrů pro přizpůsobený zážitek.
- **Vytvářejte aplikace pomocí API**: Použijte klientské knihovny pro [Python](https://github.com/ollama/ollama-python) nebo [JavaScript](https://github.com/ollama/ollama-js) k integraci Ollama do vašich aplikací.
- **Propojte s frontendy**: Zkombinujte Ollama s nástroji, jako je [Open WebUI](https://github.com/open-webui/open-webui), a získejte tak bohaté chatovací rozhraní s vyhledáváním, personami a nahráváním dokumentů.

Další informace naleznete v [dokumentaci Ollama](https://github.com/ollama/ollama/blob/main/README.md).