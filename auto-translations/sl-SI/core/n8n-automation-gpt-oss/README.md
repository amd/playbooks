<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Ta priročnik uporablja posebne oznake, ki jih GitHub ne more prikazati. Za pravilen ogled te vsebine obiščite [amd.com/playbooks](https://amd.com/playbooks).
<!-- @github-only:end -->

## Pregled

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Ta priročnik zahteva najmanj **32 GB** sistemskega pomnilnika.
<!-- @device:end -->

n8n je platforma za avtomatizacijo delovnih tokov, ki vam omogoča povezovanje aplikacij in storitev z vizualnim urejevalnikom na osnovi vozlišč.

Ta priročnik vas uči, kako vzpostaviti z umetno inteligenco podprt povzemalnik finančnih novic, ki zbira vsebino iz poslovnega razdelka AP News, izvleče ključne naslove in z lokalnim jezikovnim modelom, ki deluje na vašem sistemu, ustvari povzetek za vlagatelje.

## Kaj se boste naučili

- Kako namestiti in zagnati n8n
- Uvažanje in konfiguriranje vnaprej pripravljenega delovnega toka
- Povezovanje z Lemonade z uporabo izvorne integracije n8n
- Razumevanje vozlišč delovnega toka in pretoka podatkov

## Kaj je Lemonade?

[Lemonade](https://lemonade-server.ai) je lokalna platforma za strežbo jezikovnih modelov, zgrajena za AMD strojno opremo. Zagotavlja API, združljiv z OpenAI, ki deluje v celoti na vaši napravi – vaši podatki nikoli ne zapustijo vaše naprave.

V tem priročniku uporabljamo Lemonade za strežbo lokalnega jezikovnega modela, s katerim se n8n poveže za naloge, podprte z umetno inteligenco.

n8n vključuje **izvorno vozlišče Lemonade** (`Lemonade Chat Model`), ki zagotavlja integracijo prve stopnje – ni potrebna ročna konfiguracija. To poenostavi povezovanje lokalnega jezikovnega modela z delovnimi tokovi avtomatizacije.

## Nastavitev konfiguracije pomnilnika

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Preverjanje posodobitev programske opreme

<!-- @require:software-update -->
<!-- @device:end -->

## Namestitev predpogojev programske opreme
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
Namestite n8n globalno z npm.

> **Opomba**: Morda boste videli nekatera opozorila npm. To je pričakovano.

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
> **Nasvet**: Uporabniki sistema Windows morda morajo spremeniti pravilnik izvajanja PowerShell (npr.
> nastaviti ga na RemoteSigned ali Unrestricted) pred izvajanjem nekaterih ukazov PowerShell.
<!-- @os:end -->


<!-- @os:windows -->
> **Težava s PATH**: Če `n8n --version` sporoči, da ukaz ni najden, preverite, ali je globalni imenik npm bin v uporabniški spremenljivki `PATH`. Običajna pot namestitve je `C:\Users\<username>\AppData\Roaming\npm`.
> Dodajte to v uporabniško pot (Uredi sistemske spremenljivke okolja > Spremenljivke okolja > Uredi uporabniško pot) in znova zaženite terminal.

<!-- @os:end -->

<!-- @os:linux -->
Zdaj bomo uporabili storitev Podman za vsebnikovanje naše namestitve n8n.

Prenesite naslednje v imenik po vaši izbiri: [compose.yml](assets/compose.yml)

V tem imeniku zaženite naslednji ukaz:
```bash
podman compose up -d
```

To bi moralo namestiti n8n in pisati v trajno shrambo.

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
n8n zažene lokalni spletni strežnik. Pritisnite `'o'` ali odprite brskalnik na `http://localhost:5678` za dostop do urejevalnika.
<!-- @os:end -->


> **Nasvet**: Med uporabo n8n pustite okno terminala odprto. Zapiranje ga lahko ustavi strežnik.

## Zagon Lemonade

Lemonade je lokalni strežnik, ki bo zagnal model in se povezal z n8n.

<!-- @os:linux -->
Odprite grafični vmesnik Lemonade s klikom na ikono Lemonade v opravilni vrstici. Od tu lahko brskate po modelih, zalednih sistemih in naložite vnaprej nameščene modele.
<!-- @os:end -->

<!-- @os:windows -->
Odprite grafični vmesnik Lemonade s klikom na ikono Lemonade. Z desnim klikom na ikono v sistemski vrstici odprite aplikacijo. Nato lahko dodate modele, zaledne sisteme in naložite vnaprej nameščene modele.
<!-- @os:end -->

>**Nasvet**: Ko je zagnan, je grafični vmesnik Lemonade dostopen tudi na http://localhost:13305

Lahko pa odprete terminal in zaženete `lemonade list`, da vidite, kateri modeli so nameščeni. Nato zaženite:

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

Ko prvič odprete n8n, boste pozvani k ustvaritvi računa ali prijavi:

1. Odprite `http://localhost:5678` v brskalniku
2. Ustvarite nov lokalni račun s svojim e-poštnim naslovom ali se prijavite, če račun že imate
3. Po prijavi boste videli nadzorno ploščo n8n

> **Nasvet**: Če ste zaklenjeni iz svojega računa, poskusite z `n8n user-management:reset`

### 2. korak: Uvoz delovnega toka

Zagotovili smo vnaprej pripravljen delovni tok, ki ga lahko uvozite neposredno:

1. Prenesite naslednjo datoteko delovnega toka: [financial-news-workflow.json](assets/financial-news-workflow.json)
2. Kliknite **Start from Scratch**, da odprete urejevalnik delovnega toka. Lahko pa kliknete gumb + v zgornjem levem kotu in nato **Add workflow**.
3. Kliknite meni **...** (tri pike) v zgornji desni vrstici in izberite **Import from file**
4. Izberite preneseno datoteko `financial-news-workflow.json`
5. Delovni tok se bo prikazal na platnu


### 3. korak: Razumevanje delovnega toka

Uvoženi delovni tok vsebuje 9 povezanih vozlišč:

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| Vozlišče | Namen |
|------|---------|
| **When clicking 'Execute workflow'** | Ročni sprožilec za zagon delovnega toka |
| **Fetch Financial News Webpage** | HTTP GET zahteva na `https://apnews.com/business` |
| **Delay to Ensure Page Load** | Vozlišče za čakanje, ki zagotovi, da je vsebina strani v celoti naložena |
| **Extract News Headlines & Text** | Vozlišče HTML, ki z izbirniki CSS izvleče naslove, urednikove izbire, glavne zgodbe in regionalne novice |
| **Clean Extracted News Data** | Vozlišče Set, ki združi vse izvlečene podatke v eno besedilno polje |
| **AI Financial News Summarizer** | Agent umetne inteligence, ki obdela novice s sistemskim pozivom finančnega analitika |
| **Lemonade Chat Model** | Poveže se z vašim lokalnim strežnikom Lemonade, ki poganja jezikovni model |
| **Structured Output Parser** | Oblikuje izhod umetne inteligence kot strukturiran JSON |
| **Convert to File** | Pretvori povzetek v datoteko za prenos |

### 4. korak: Konfiguracija poverilnic Lemonade

Preden zaženete delovni tok, ga morate povezati z lokalnim strežnikom Lemonade:

1. Dvokliknite vozlišče **Lemonade Chat Model** v n8n
2. V spustnem meniju **Credential to connect with** izberite **Create New Credential**
3. Vnesite vrednosti iz spodnje tabele in kliknite shrani.
4. Izberite ustrezen model, ki ste ga naložili v strežnik Lemonade.

  | Polje | Vrednost |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **Opomba**: Pred testiranjem zaženite `lemonade status` v terminalu, da potrdite, da strežnik Lemonade deluje.
<!-- @device:halo_box -->
> Ta delovni tok uporablja GPT-OSS-120B, ki je vnaprej nameščen v Lemonade. To lahko spremenite na druge naložene modele v nastavitvah vozlišča Lemonade Chat Model.
<!-- @device:end -->

### 5. korak: Testiranje delovnega toka

1. Prepričajte se, da Lemonade deluje z naloženim modelom
2. Kliknite **Execute workflow** na sredini spodnjega dela platna
3. Opazujte izvajanje vsakega vozlišča od leve proti desni – ko je dokončano, postane zeleno
4. Dvokliknite vozlišče **AI Financial News Summarizer**, da si ogledate ustvarjeni povzetek v spodnjem podoknu.
5. Dvokliknite vozlišče **Convert to File**, da prenesete ustrezno besedilno datoteko v spodnjem podoknu.

## Razumevanje agenta umetne inteligence

AI Financial News Summarizer uporablja sistemski poziv, zasnovan za finančno analizo:

```
You are an AI financial analyst. Your role is to read, understand, and
summarize key financial news from today. The goal is to provide investors
with a clear and concise market overview to support better investment decisions.

Investor Outlook
Today's news points to [bullish/bearish/neutral] sentiment. Watch for
[economic event/earnings report] tomorrow, which could influence market direction.
```

Agent prejme očiščene podatke o novicah in ustvari strukturiran povzetek s tržnim razpoloženjem.

### Shranjevanje delovnega toka

Kliknite ime delovnega toka na vrhu in ga po želji preimenujte. Delovni tokovi se samodejno shranjujejo med delom.

## Naslednji koraki

- **Načrtovanje avtomatizacije**: Zamenjajte ročni sprožilec s **Schedule Trigger** za dnevno izvajanje
- **Pošiljanje obvestil**: Dodajte vozlišče **Discord**, **Slack** ali **Email** za prejemanje povzetkov
- **Preizkusite različne modele**: Spremenite model v vozlišču Lemonade Chat Model za eksperimentiranje z različnimi jezikovnimi modeli
- **Prilagodite ekstrakcijo**: Spremenite izbirnike CSS vozlišča HTML Extract za ciljanje različnih razdelkov novic
- **Preizkusite različne zaledne sisteme**: n8n podpira tudi [Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model), LM Studio in druge lokalne zaledne sisteme jezikovnih modelov

### Raziščite predloge n8n

n8n ima na stotine vnaprej pripravljenih predlog delovnih tokov. Brskajte po uradni knjižnici predlog na:

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

Iščite »AI«, »LLM« ali »automation«, da najdete delovne tokove, ki jih lahko uvozite in prilagodite.

Za več informacij si oglejte [dokumentacijo n8n](https://docs.n8n.io/).