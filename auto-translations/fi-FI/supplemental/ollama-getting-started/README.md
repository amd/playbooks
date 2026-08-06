<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Konekäännös.** Tämä sivu on käännetty automaattisesti englannista, eikä sitä ole tarkistanut ihminen. Se voi sisältää virheitä, ja tietyt ohjeet, komennot, lataukset, tuotteiden saatavuus tai muu sisältö voivat vaihdella kielen tai alueen mukaan. Mahdollisten ristiriitaisuuksien tai epäjohdonmukaisuuksien ilmetessä alkuperäinen englanninkielinen playbook on ratkaiseva ja ensisijainen versio.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Yleiskatsaus

Ollama on suosittu kevyt työkalu suurten kielimallien ajamiseen paikallisesti. Se hoitaa mallien lataamisen, kvantisoinnin ja tarjoamisen yksinkertaisen komentorivikäyttöliittymän ja työpöytäsovelluksen kautta, joten voit siirtyä nollasta keskusteluun LLM:n kanssa minuuteissa.

Tämä ohjekirja opastaa sinut Ollaman asentamisessa, GPT-OSS 20B -mallin lataamisessa ja sen kanssa keskustelemisessa sekä päätteen että työpöytäsovelluksen kautta.

## Mitä opit

- Kuinka asennat ja käynnistät Ollaman järjestelmässäsi
- GPT-OSS 20B -mallin lataaminen ja ajaminen paikallisesti
- Mallien kanssa keskusteleminen CLI:n avulla
- Mallien kysely ohjelmallisesti REST-rajapinnan kautta

## Muistiasetuksen määrittäminen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Tarkista ohjelmistopäivitykset
> **Huomautus**: Jos VS Code ei ole asennettuna, voit asentaa sen Ryzen AI Developer Centerin avulla.

<!-- @require:software-update -->
<!-- @device:end -->

## Ohjelmiston esivaatimusten asentaminen

<!-- @require:driver -->

### Ollaman asentaminen

<!-- @os:windows -->

1. Lataa asennusohjelma osoitteesta [ollama.com/download](https://ollama.com/download).
2. Suorita `.exe`-asennusohjelma ja seuraa ohjeita.
3. Kun asennus on valmis, Ollama toimii taustapalveluna ja on käytettävissä päätteestä, työpöytäsovelluksesta ja ilmaisinalueelta.

Vahvista asennus avaamalla pääte ja suorittamalla:

```powershell
ollama --version
```

<!-- @test:id=ollama-version-windows timeout=60 hidden=True -->
```powershell
ollama --version
```
<!-- @test:end --> 

Konsoliin pitäisi tulostua asennetun version numero.
<!-- @os:end -->

<!-- @os:linux -->

Suorita virallinen asennusskripti:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Vahvista asennus:

```bash
ollama --version
```

<!-- @test:id=ollama-version-linux timeout=60 hidden=True -->
```bash
ollama --version
```
<!-- @test:end --> 

Konsoliin pitäisi tulostua asennetun version numero.
<!-- @os:end -->

## Ensimmäisen mallin lataaminen

Ollama hallitsee malleja rekisterin kautta, joka muistuttaa säilöntäkuvia (container images). GPT-OSS 20B:n lataamiseksi:

```bash
ollama pull gpt-oss:20b
```

Tämä lataa mallin painot paikalliselle koneellesi (noin 12 Gt). Lataus tapahtuu vain kerran, ja seuraavat ajokerrat lataavat mallin levyltä.

Voit varmistaa, että malli on saatavilla, komennolla:

```bash
ollama list
```

Tulosteessa pitäisi näkyä `gpt-oss:20b` yhdessä sen koon ja viimeisimmän muokkauspäivämäärän kanssa.

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

### Mallien nimeäminen

Ollaman mallien nimet noudattavat muotoa `name:tag`. Tunniste (tag) ilmaisee yleensä parametrien määrän tai kvantisointivariantin. Muutamia hyödyllisiä komentoja mallien hallintaan:

| Komento | Kuvaus |
|---------|-------------|
| `ollama list` | Näyttää kaikki ladatut mallit |
| `ollama pull <model>` | Lataa mallin ajamatta sitä |
| `ollama rm <model>` | Poistaa mallin vapauttaakseen levytilaa |
| `ollama show <model>` | Näyttää mallin metatiedot ja parametrit |

## Keskustelu päätteestä

Käynnistä vuorovaikutteinen keskusteluistunto suoraan komentoriviltä:

```bash
ollama run gpt-oss:20b
```

Ollama lataa mallin muistiin ja siirtää sinut kehotteeseen. Kokeile kysyä siltä jotain:

```
>>> What is the capital of France and why is it historically significant?
```

Malli suoratoistaa vastauksensa merkki kerrallaan suoraan päätteessä. Kirjoita `/bye` tai paina `Ctrl+D` poistuaksesi istunnosta.

> **Vihje**: Ensimmäinen ajokerta vie muutaman sekunnin mallin lataamiseen muistiin. Saman istunnon myöhemmät kehotteet vastaavat paljon nopeammin, koska malli pysyy ladattuna.

<!-- @os:windows -->
## Keskustelu työpöytäsovelluksesta

Ollama sisältää myös työpöytäsovelluksen, joka tarjoaa selkeän keskusteluliittymän mallien kanssa vuorovaikutukseen.

Avaa **Ollama** Käynnistä-valikosta tai napsauta Ollama-kuvaketta ilmaisinalueella ja valitse **Open Ollama**.

Kun sovellus on auki:

1. Napsauta **New Chat** sivupalkissa.
2. Valitse **gpt-oss:20b** malli-alasvetovalikosta keskustelusyötealueen oikeassa alakulmassa.
3. Kirjoita viesti ja paina Enter aloittaaksesi keskustelun.

<p align="center">
  <img src="assets/ollama_app.png" alt="Ollama desktop app chatting with gpt-oss:20b" width="600"/>
</p>

Työpöytäsovellus pitää sivupalkissa historiaa keskusteluistasi, mikä helpottaa aiempien keskustelujen tarkastelua.
<!-- @os:end -->

## REST-rajapinnan käyttäminen

Asennuksen jälkeen Ollama toimii taustapalveluna ja tarjoaa REST-rajapinnan osoitteessa `http://localhost:11434`, jota voit käyttää mallien integroimiseen omiin sovelluksiisi ja skripteihisi.

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

### Vastauksen generointi päätteessä

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

Vastaus on JSON-objekti, joka sisältää mallin tuloksen `response`-kentässä.


### Python-esimerkki
Nyt kun voimme kutsua Ollama-rajapintaa ohjelmallisesti, kutsutaan sitä Pythonista.

#### Virtuaaliympäristön luominen päätteessä

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
#### Python-tiedoston luominen
Luo samaan hakemistoon .py-tiedosto VS Coden tai muun editorin avulla ja kopioi siihen seuraava koodi. Suorita sitten tiedosto aktivoidussa ympäristössäsi komennolla `python your_file_name.py`

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

### Tärkeimmät API-päätepisteet

| Päätepiste | Metodi | Tarkoitus |
|----------|--------|---------|
| `/api/generate` | POST | Yksivaiheinen tekstin generointi |
| `/api/chat` | POST | Monivaiheinen keskustelu viestihistorian kanssa |
| `/api/tags` | GET | Saatavilla olevien mallien listaus |
| `/api/show` | POST | Mallin tietojen näyttäminen |
| `/api/pull` | POST | Mallin lataaminen rekisteristä |

Täydellinen API-viite löytyy [Ollaman API-dokumentaatiosta](https://github.com/ollama/ollama/blob/main/docs/api.md).
## Seuraavat vaiheet

- **Kokeile eri malleja**: Selaa [Ollama-mallikirjastoa](https://ollama.com/library) tutustuaksesi satoihin saatavilla oleviin malleihin pienistä koodausavustajista suuriin päättelymalleihin.
- **Luo mukautettuja malleja**: Käytä [Modelfilea](https://github.com/ollama/ollama/blob/main/docs/modelfile.md) mukautettujen järjestelmäkehotteiden, lämpötilan ja muiden parametrien asettamiseen räätälöityä käyttökokemusta varten.
- **Kehitä API:n avulla**: Käytä [Python](https://github.com/ollama/ollama-python)- tai [JavaScript](https://github.com/ollama/ollama-js)-asiakaskirjastoja Ollaman integroimiseksi sovelluksiisi.
- **Yhdistä käyttöliittymiin**: Yhdistä Ollama esimerkiksi [Open WebUI](https://github.com/open-webui/open-webui) -työkalun kanssa saadaksesi monipuolisen keskusteluliittymän, jossa on haku, persoonat ja asiakirjojen lataus.

Lisätietoja löydät [Ollaman dokumentaatiosta](https://github.com/ollama/ollama/blob/main/README.md).