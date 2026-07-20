<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Ta priročnik uporablja posebne oznake, ki jih GitHub ne more upodobiti. Obiščite [amd.com/playbooks](https://amd.com/playbooks), da si to vsebino ogledate pravilno.
<!-- @github-only:end -->

## Pregled

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Ta priročnik zahteva vsaj **32 GB** sistemskega pomnilnika.
<!-- @device:end -->

n8n je platforma za avtomatizacijo delovnih tokov, ki omogoča povezovanje aplikacij in storitev prek vizualnega urejevalnika, temelječega na vozliščih.

Ta priročnik vas nauči, kako nastaviti povzemalnik finančnih novic, ki temelji na umetni inteligenci, ki prečeše poslovni razdelek AP News, izlušči ključne naslove in uporabi lokalni LLM, ki teče v vašem sistemu, za generiranje povzetka, prilagojenega vlagateljem.

## Kaj se boste naučili

- Kako namestiti in zagnati n8n
- Uvažanje in konfiguriranje vnaprej pripravljenega delovnega toka
- Povezovanje z Lemonade z uporabo domače integracije n8n
- Razumevanje vozlišč delovnega toka in pretoka podatkov

## Kaj je Lemonade?

[Lemonade](https://lemonade-server.ai) je platforma za lokalno strežbo LLM, zgrajena za strojno opremo AMD. Zagotavlja API, združljiv z OpenAI, ki teče v celoti na vaši napravi – vaši podatki nikoli ne zapustijo naprave.

V tem priročniku uporabljamo Lemonade za strežbo lokalnega LLM, s katerim se n8n poveže za naloge, temelječe na umetni inteligenci.

n8n vključuje **domače vozlišče Lemonade** (`Lemonade Chat Model`), ki zagotavlja prvovrstno integracijo – ni potrebe po ročni konfiguraciji. To olajša povezovanje vašega lokalnega LLM z delovnimi tokovi za avtomatizacijo.

## Nastavitev konfiguracije pomnilnika

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Preverjanje posodobitev programske opreme

<!-- @require:software-update -->
<!-- @device:end -->

## Namestitev potrebne programske opreme
<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @require:lemonade,podman -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<!-- @var:id=lemonade_model value="gpt-oss-120b-mxfp-GGUF" -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @var:id=lemonade_model value="gpt-oss-20b-mxfp4-GGUF" -->
<!-- @device:end -->


<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-chat-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

# Wait for server to come up
$modelsJson = $null
for ($i=0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}
if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

# Now that the server is responding, check if model is downloaded in Lemonade (robust JSON parse)
$parsed = $modelsJson | ConvertFrom-Json
$entry  = $parsed.data | Where-Object { $_.id -eq "${lemonade_model}" } | Select-Object -First 1
if (-not $entry) { throw "Model ${lemonade_model} is not present in Lemonade /api/v1/models." }
if (-not $entry.downloaded) { throw "Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it." }
Write-Host "OK: ${lemonade_model} model is downloaded in Lemonade"

# Model chat test
$body = @{
  model = "${lemonade_model}"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "lemonade-chat-body.json"
[System.IO.File]::WriteAllText($tmpBody, $body, [System.Text.UTF8Encoding]::new($false))

try {
  $out = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
  -H "Content-Type: application/json" `
  --data-binary "@$tmpBody"
  if (-not $out) { throw "Empty response from Lemonade chat/completions" }
}
finally {
  Remove-Item  $tmpBody -Force -ErrorAction SilentlyContinue
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
  "max_tokens": 32
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

<!-- @test:id=node-npm-version timeout=60 hidden=True -->
```bash
node -v
npm -v
```
<!-- @test:end -->

## Namestitev n8n
<!-- @os:windows -->
Namestite n8n globalno z uporabo npm.

> **Opomba**: Morda boste videli nekaj opozoril npm. To je pričakovano.

```bash
npm install -g n8n
```

<!-- @test:id=n8n-version timeout=60 hidden=True -->
```bash
n8n --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=n8n-version timeout=60 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
n8n --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
> **Nasvet**: Uporabniki sistema Windows bodo morda morali spremeniti izvedbeno politiko PowerShell (npr.
> jo nastaviti na RemoteSigned ali Unrestricted), preden zaženejo nekatere ukaze PowerShell.
<!-- @os:end -->


<!-- @os:windows -->
> **Težava s PATH**: Če `n8n --version` sporoči, da ukaz ni najden, se prepričajte, da je vaš globalni bin imenik npm v uporabniškem `PATH`. Običajna namestitvena pot je `C:\Users\<username>\AppData\Roaming\npm`.
> Dodajte to v uporabniško pot (Uredi sistemske spremenljivke okolja > Spremenljivke okolja > Uredi uporabniško pot) in ponovno naložite terminal.

<!-- @os:end -->

<!-- @os:linux -->
Zdaj bomo uporabili storitev Podman za kontejnerizacijo naše namestitve n8n.

Prosimo, prenesite naslednje v imenik po svoji izbiri: [compose.yml](assets/compose.yml)

V tem imeniku zaženite naslednji ukaz:
```bash
podman compose up -d
```

S tem se bo n8n namestil in zapisal v trajno shrambo.

Zaženite n8n tako, da v naslovno vrstico brskalnika vnesete `localhost:5678`.
<!-- @os:end -->

<!-- @os:windows -->
## Zagon n8n

Zaženite n8n iz terminala:

```bash
n8n start
```

<!-- @test:id=n8n-start-windows timeout=300 hidden=True -->
```powershell
$N8N_CMD = "$env:APPDATA\npm\n8n.cmd"
$p = Start-Process -FilePath "cmd.exe" -ArgumentList "/c `"$N8N_CMD`" start" -NoNewWindow -PassThru
try {
  $ok = $false
  for ($i=0; $i -lt 120; $i++) {
    # Check HTTP status code only (body may be empty)
    $code = curl.exe -s -o NUL -w "%{http_code}" --max-time 2 http://127.0.0.1:5678/healthz
    if ($LASTEXITCODE -eq 0 -and $code -eq "200") { $ok = $true; break }
    Start-Sleep -Seconds 1
  }
  if (-not $ok) { throw "n8n not ready on http://127.0.0.1:5678/healthz" }
  Write-Host "OK: n8n server is responding"
} finally {
  # Kill the process actually listening on 5678
  $conn = Get-NetTCPConnection -LocalPort 5678 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($conn) { Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue }
  # Also kill wrapper pid just in case
  if ($p -and -not $p.HasExited) { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue }
}
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=n8n-start-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
p=""
cleanup() {
  if [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null || true
    sleep 2
    kill -9 "$p" 2>/dev/null || true
  fi
}
trap cleanup EXIT

n8n start >/tmp/n8n-test.log 2>&1 &
p=$!

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:5678/healthz || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "n8n not ready on http://127.0.0.1:5678/healthz"
  exit 1
fi

echo "OK: n8n server is responding"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
n8n zažene lokalni spletni strežnik. Pritisnite `'o'` ali odprite svoj brskalnik na naslovu `http://localhost:5678`, da dostopate do urejevalnika.
<!-- @os:end -->


> **Nasvet**: Med uporabo n8n pustite okno terminala odprto. Če ga zaprete, se lahko strežnik ustavi.

## Zagon Lemonade

Lemonade je lokalni strežnik, ki bo zagnal model in se povezal z n8n.

<!-- @os:linux -->
Odprite grafični vmesnik Lemonade tako, da kliknete ikono Lemonade v opravilni vrstici. Tukaj lahko brskate po modelih, zaledjih (backends) in naložite vnaprej nameščene modele.
<!-- @os:end -->

<!-- @os:windows -->
Odprite grafični vmesnik Lemonade tako, da kliknete ikono Lemonade. Z desnim klikom na ikono v pladnju odprite aplikacijo. Nato lahko dodate modele, zaledja (backends) in naložite vnaprej nameščene modele.
<!-- @os:end -->

>**Nasvet**: Ko je zagnan, je grafični vmesnik Lemonade dostopen tudi na http://localhost:13305

Druga možnost je, da odprete terminal in zaženete `lemonade list`, da vidite, kateri modeli so nameščeni. Nato zaženite:

<!-- @device:halo_box -->
<!-- @os:linux -->
```bash
lemonade run gpt-oss-120b-Q4_K_M --llamacpp vulkan
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
lemonade run gpt-oss-120b-GGUF --llamacpp vulkan
```
<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo -->
```bash
lemonade run gpt-oss-120b-GGUF --llamacpp vulkan
```
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
```bash
lemonade run gpt-oss-20b-GGUF --llamacpp vulkan
```
<!-- @device:end -->


## Nastavitev delovnega toka

### 1. korak: Registracija ali prijava v n8n

Ko prvič odprete n8n, boste pozvani k ustvarjanju računa ali prijavi:

1. Odprite `http://localhost:5678` v svojem brskalniku
2. Ustvarite nov lokalni račun z e-poštnim naslovom ali se prijavite, če ga že imate
3. Ko ste prijavljeni, boste videli nadzorno ploščo n8n

> **Nasvet**: Če ste izklenjeni iz svojega računa, poskusite `n8n user-management:reset`

### 2. korak: Uvoz delovnega toka

Zagotovili smo vnaprej pripravljen delovni tok, ki ga lahko uvozite neposredno:

1. Prenesite naslednjo datoteko delovnega toka: [financial-news-workflow.json](assets/financial-news-workflow.json)
2. Kliknite **Start from Scratch**, da odprete urejevalnik delovnega toka. Druga možnost je, da kliknete gumb + zgoraj levo in nato **Add workflow**.
3. Kliknite meni **...** (tri pike) v zgornji desni vrstici in izberite **Import from file**
4. Izberite prenesено datoteko `financial-news-workflow.json`
5. Delovni tok se bo prikazal na platnu
### Korak 3: Razumevanje poteka dela

Uvoženi potek dela vsebuje 9 povezanih vozlišč:

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| Vozlišče | Namen |
|------|---------|
| **When clicking 'Execute workflow'** | Ročni sprožilec za zagon poteka dela |
| **Fetch Financial News Webpage** | Zahteva HTTP GET na `https://apnews.com/business` |
| **Delay to Ensure Page Load** | Vozlišče za čakanje, ki zagotovi popolno naložitev vsebine strani |
| **Extract News Headlines & Text** | Vozlišče HTML, ki s CSS selektorji izvleče naslove, uredniške izbore, glavne zgodbe in regionalne novice |
| **Clean Extracted News Data** | Vozlišče Set, ki združi vse izvlečene podatke v eno besedilno polje |
| **AI Financial News Summarizer** | Agent AI, ki obdela novice s sistemskim pozivom finančnega analitika |
| **Lemonade Chat Model** | Poveže se z vašim lokalnim strežnikom Lemonade, na katerem teče LLM |
| **Structured Output Parser** | Oblikuje izhod AI kot strukturiran JSON |
| **Convert to File** | Pretvori povzetek v datoteko za prenos |

### Korak 4: Konfiguracija poverilnic za Lemonade

Preden zaženete potek dela, ga morate povezati z vašim lokalnim strežnikom Lemonade:

1. Dvokliknite vozlišče **Lemonade Chat Model** v n8n
2. V spustnem meniju **Credential to connect with** izberite **Create New Credential**
3. Vnesite vrednosti iz spodnje tabele in kliknite za shranjevanje.
4. Izberite ustrezen model, ki ste ga naložili v Lemonade Server.

  | Polje | Vrednost |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **Opomba**: Pred testiranjem v terminalu zaženite `lemonade status`, da potrdite, da strežnik Lemonade deluje.
<!-- @device:halo_box -->
> Ta potek dela uporablja GPT-OSS-120B, ki je v Lemonade že vnaprej nameščen. To lahko spremenite na druge naložene modele v nastavitvah vozlišča Lemonade Chat Model.
<!-- @device:end -->

### Korak 5: Testiranje poteka dela

1. Prepričajte se, da Lemonade teče z naloženim modelom
2. Kliknite **Execute workflow** na spodnjem sredinskem delu platna
3. Opazujte, kako se posamezna vozlišča izvajajo od leve proti desni – ob dokončanju postanejo zelena
4. Dvokliknite vozlišče **AI Financial News Summarizer**, da si ogledate ustvarjeni povzetek v spodnjem podoknu.
5. Dvokliknite vozlišče **Convert to File**, da v spodnjem podoknu prenesete ustrezno besedilno datoteko.

## Razumevanje agenta AI

AI Financial News Summarizer uporablja sistemski poziv, zasnovan za finančno analizo:

```
You are an AI financial analyst. Your role is to read, understand, and
summarize key financial news from today. The goal is to provide investors
with a clear and concise market overview to support better investment decisions.

Investor Outlook
Today's news points to [bullish/bearish/neutral] sentiment. Watch for
[economic event/earnings report] tomorrow, which could influence market direction.
```

Agent prejme počiščene podatke o novicah in ustvari strukturiran povzetek s tržnim razpoloženjem.

### Shranjevanje poteka dela

Kliknite ime poteka dela na vrhu in ga po želji preimenujte. Poteki dela se med delom samodejno shranjujejo.

## Naslednji koraki

- **Načrtovanje avtomatizacije**: Zamenjajte Manual Trigger s **Schedule Trigger**, da se izvaja dnevno
- **Pošiljanje obvestil**: Dodajte vozlišče **Discord**, **Slack** ali **Email**, da prejemate povzetke
- **Preizkusite različne modele**: Spremenite model v vozlišču Lemonade Chat Model, da preizkusite različne LLM-je
- **Prilagoditev izvlečka**: Spremenite CSS selektorje vozlišča HTML Extract, da ciljate na druge razdelke novic
- **Preizkusite različna ozadja**: n8n podpira tudi [Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model), LM Studio in druga lokalna ozadja LLM

### Raziščite predloge n8n

n8n ponuja na stotine vnaprej pripravljenih predlog poteka dela. Prebrskajte uradno knjižnico predlog na:

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

Iščite "AI", "LLM" ali "automation", da najdete poteke dela, ki jih lahko uvozite in prilagodite.

Za več informacij si oglejte [dokumentacijo n8n](https://docs.n8n.io/).