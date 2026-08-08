<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojni prevod.** Ta stran je bila samodejno prevedena iz angleščine in je ni pregledal človek. Lahko vsebuje napake, določena navodila, ukazi, prenosi, razpoložljivost izdelkov ali druga vsebina pa se lahko razlikujejo glede na jezik ali regijo. V primeru kakršnega koli neskladja ali razhajanja je merodajna in prevladujoča izvirna angleška različica playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->
# Pregled
<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!OPOMBA]
> Ta vodnik zahteva vsaj **32 GB** sistemskega pomnilnika.
<!-- @device:end -->
n8n je platforma za avtomatizacijo delovnih tokov, ki omogoča povezovanje aplikacij in storitev z vizualnim urejevalnikom, ki temelji na vozliščih.

Ta vodnik vas nauči, kako nastaviti s pomočjo umetne inteligence poganjan povzemalnik finančnih novic, ki poišče vsebino iz razdelka za posle na AP News, izvleče ključne naslove in uporabi lokalni LLM, ki teče v vašem sistemu, za generiranje povzetka, namenjenega vlagateljem.

## Kaj se boste naučili

- Kako namestiti in zagnati n8n
- Uvažanje in konfiguriranje vnaprej pripravljenega delovnega toka
- Povezovanje z Lemonade prek native n8n integracije
- Razumevanje vozlišč delovnega toka in pretoka podatkov

## Kaj je Lemonade?

[Lemonade](https://lemonade-server.ai) je platforma za lokalno strežbo LLM, zgrajena za strojno opremo AMD. Zagotavlja API, združljiv z OpenAI, ki teče v celoti na vaši napravi—vaši podatki nikoli ne zapustijo vaše naprave.

V tem vodniku uporabljamo Lemonade za strežbo lokalnega LLM, s katerim se n8n poveže za naloge, ki jih poganja umetna inteligenca.

n8n vključuje **native vozlišče Lemonade** (`Lemonade Chat Model`), ki zagotavlja integracijo prvega razreda - brez potrebe po ročni konfiguraciji. To omogoča preprosto povezovanje vašega lokalnega LLM z delovnimi tokovi avtomatizacije.

## Nastavljanje konfiguracije pomnilnika
<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Preveri posodobitve programske opreme
<!-- @require:software-update -->
<!-- @device:end -->
## Namestitev programskih predpogojev
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
> **Nasvet**: Uporabniki sistema Windows bodo morda morali spremeniti izvedbeno pravilnik (Execution Policy) za PowerShell (npr. ga nastaviti na RemoteSigned ali Unrestricted), preden bodo lahko zagnali nekatere ukaze PowerShell.
<!-- @os:end -->


<!-- @os:windows -->
> **Težava s PATH**: Če `n8n --version` javi, da ukaz ni najden, se prepričajte, da je vaš globalni npm bin direktorij vključen v uporabniško spremenljivko `PATH`. Običajna namestitvena pot je `C:\Users\<username>\AppData\Roaming\npm`. 
> Dodajte to pot v uporabniško spremenljivko PATH (Uredi sistemske spremenljivke okolja > Spremenljivke okolja > Uredi uporabniško pot) in znova naložite terminal.
<!-- @os:end -->

<!-- @os:linux -->
Zdaj bomo uporabili storitev Podman za vsebnikizacijo naše namestitve n8n.

Prosimo, prenesite naslednje v mapo po vaši izbiri: [compose.yml](assets/compose.yml)

V tej mapi zaženite naslednji ukaz:
```bash
podman compose up -d
```

To bi moralo namestiti n8n in zapisati podatke v trajno shrambo.

Zaženite n8n tako, da v naslovno vrstico brskalnika vnesete `localhost:5678`.
<!-- @os:end -->

<!-- @os:windows -->
## Zaganjanje n8n

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
n8n zažene lokalni spletni strežnik. Pritisnite `'o'` ali odprite brskalnik na naslovu `http://localhost:5678`, da dostopate do urejevalnika.
<!-- @os:end -->
> **Nasvet**: Med uporabo n8n naj bo okno terminala odprto. Če ga zaprete, se strežnik morda ustavi.

## Zagon Lemonade

Lemonade je lokalni strežnik, ki bo zagnal model in ga povezal z n8n.
<!-- @os:linux -->
Odprite grafični vmesnik Lemonade tako, da kliknete ikono Lemonade v opravilni vrstici. Tukaj lahko brskate po modelih, zalednih sistemih (backends) in naložite vnaprej nameščene modele.
<!-- @os:end -->

<!-- @os:windows -->
Odprite grafični vmesnik Lemonade s klikom na ikono Lemonade. Z desnim klikom na ikono v sistemski vrstici odprete aplikacijo. Nato lahko dodate modele, zaledja (backends) in naložite vnaprej nameščene modele.
<!-- @os:end -->
>**Nasvet**: Ko je zagnan, je Lemonade GUI dostopen tudi na naslovu http://localhost:13305

Druga možnost je, da odprete terminal in zaženete `lemonade list`, da si ogledate, kateri modeli so nameščeni. Nato zaženite:
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
## Nastavitev poteka dela

### 1. korak: Prijavite se ali se vpišite v n8n

Ko prvič odprete n8n, boste pozvani, da ustvarite račun ali se vpišete:

1. Odprite `http://localhost:5678` v brskalniku
2. Ustvarite nov lokalni račun z vašim e-poštnim naslovom ali se vpišite, če ga že imate
3. Ko se vpišete, boste videli nadzorno ploščo n8n

> **Nasvet**: Če ste zaklenjeni izven svojega računa, poskusite `n8n user-management:reset`

### 2. korak: Uvozite potek dela

Priskrbeli smo vam vnaprej pripravljen potek dela, ki ga lahko uvozite neposredno:

1. Prenesite naslednjo datoteko poteka dela: [financial-news-workflow.json](assets/financial-news-workflow.json)
2. Kliknite **Start from Scratch**, da odprete urejevalnik poteka dela. Lahko pa tudi kliknete gumb + v zgornjem levem kotu in nato **Add workflow**.
3. Kliknite meni **...** (tri pike) v zgornji desni vrstici in izberite **Import from file**
4. Izberite preneseno datoteko `financial-news-workflow.json`
5. Potek dela se bo pojavil na platnu
### Korak 3: Razumevanje poteka dela

Uvožen potek dela vsebuje 9 povezanih vozlišč:

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| Vozlišče | Namen |
|------|---------|
| **When clicking 'Execute workflow'** | Ročni sprožilec za začetek poteka dela |
| **Fetch Financial News Webpage** | Zahteva HTTP GET na `https://apnews.com/business` |
| **Delay to Ensure Page Load** | Vozlišče za čakanje, ki zagotovi popolno naložitev vsebine strani |
| **Extract News Headlines & Text** | Vozlišče HTML, ki z uporabo selektorjev CSS izloči naslove, uredniške izbore, glavne novice in regionalne novice |
| **Clean Extracted News Data** | Vozlišče Set, ki združi vse izločene podatke v eno besedilno polje |
| **AI Financial News Summarizer** | Agent AI, ki obdela novice z uporabo sistemskega poziva finančnega analitika |
| **Lemonade Chat Model** | Poveže se z vašim lokalnim strežnikom Lemonade, na katerem teče LLM |
| **Structured Output Parser** | Oblikuje izhod AI kot strukturiran JSON |
| **Convert to File** | Pretvori povzetek v datoteko za prenos |

### Korak 4: Konfiguracija poverilnic za Lemonade

Preden zaženete potek dela, ga morate povezati z vašim lokalnim strežnikom Lemonade:

1. Dvokliknite vozlišče **Lemonade Chat Model** v n8n
2. V spustnem meniju **Credential to connect with** izberite **Create New Credential**
3. Vnesite vrednosti iz spodnje tabele in kliknite »save«.
4. Izberite ustrezni model, ki ste ga naložili v Lemonade Server.

  | Polje | Vrednost |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **Opomba**: Pred testiranjem v terminalu zaženite `lemonade status`, da preverite, ali strežnik Lemonade deluje.
<!-- @device:halo_box -->
> Ta potek dela uporablja GPT-OSS-120B, ki je v Lemonade vnaprej nameščen. To lahko spremenite na druge naložene modele v nastavitvah vozlišča Lemonade Chat Model.
<!-- @device:end -->

### Korak 5: Preizkus poteka dela

1. Preverite, da Lemonade deluje z naloženim modelom
2. Kliknite **Execute workflow** na spodnjem sredinskem delu platna
3. Opazujte, kako se vsako vozlišče izvede od leve proti desni – ob dokončanju se obarva zeleno
4. Dvokliknite vozlišče **AI Financial News Summarizer**, da si v spodnjem podoknu ogledate ustvarjeni povzetek.
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

Agent prejme počiščene podatke o novicah in izpiše strukturiran povzetek z razpoloženjem na trgu.

### Shranjevanje poteka dela

Kliknite ime poteka dela na vrhu in ga po želji preimenujte. Poteki dela se med delom samodejno shranjujejo.

## Naslednji koraki

- **Načrtovanje avtomatizacije**: zamenjajte ročni sprožilec z vozliščem **Schedule Trigger**, da se izvaja vsak dan
- **Pošiljanje obvestil**: dodajte vozlišče **Discord**, **Slack** ali **Email**, da prejemate povzetke
- **Preizkusite različne modele**: spremenite model v vozlišču Lemonade Chat Model, da preizkusite različne LLM-je
- **Prilagajanje izločanja**: spremenite selektorje CSS v vozlišču HTML Extract, da ciljate na druge razdelke novic
- **Preizkusite različne zaledne rešitve**: n8n podpira tudi [Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model), LM Studio in druge lokalne zaledne rešitve LLM

### Raziščite predloge n8n

n8n ponuja na stotine vnaprej pripravljenih predlog za poteke dela. Prebrskajte uradno knjižnico predlog na:

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

Poiščite »AI«, »LLM« ali »automation«, da najdete poteke dela, ki jih lahko uvozite in prilagodite.

Za več informacij si oglejte [dokumentacijo n8n](https://docs.n8n.io/).

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