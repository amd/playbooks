<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Ovaj priručnik koristi posebne oznake koje GitHub ne može prikazati. Posetite [amd.com/playbooks](https://amd.com/playbooks) da biste ispravno pregledali ovaj sadržaj.
<!-- @github-only:end -->

## Pregled

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Ovaj priručnik zahteva najmanje **32GB** sistemske memorije.
<!-- @device:end -->

n8n je platforma za automatizaciju radnih tokova koja vam omogućava da povežete aplikacije i usluge pomoću vizuelnog editora zasnovanog na čvorovima.

Ovaj priručnik vas uči kako da postavite AI-powered sumarizer finansijskih vesti koji preuzima poslovnu sekciju AP News-a, izvlači ključne naslove i koristi lokalni LLM koji radi na vašem sistemu za generisanje rezimea usmerenog na investitore.

## Šta ćete naučiti

- Kako da instalirate i pokrenete n8n
- Uvoz i konfiguracija unapred pripremljenog radnog toka
- Povezivanje sa Lemonade putem native n8n integracije
- Razumevanje čvorova radnog toka i toka podataka

## Šta je Lemonade?

[Lemonade](https://lemonade-server.ai) je lokalna platforma za posluživanje LLM-a izgrađena za AMD hardver. Pruža OpenAI-kompatibilan API koji radi isključivo na vašem uređaju — vaši podaci nikada ne napuštaju vaš uređaj.

U ovom priručniku koristimo Lemonade za posluživanje lokalnog LLM-a na koji se n8n povezuje za AI-powered zadatke.

n8n uključuje **native Lemonade čvor** (`Lemonade Chat Model`) koji pruža integraciju prvog reda — bez potrebe za ručnom konfiguracijom. To čini povezivanje vašeg lokalnog LLM-a sa radnim tokovima automatizacije jednostavnim.

## Postavljanje konfiguracije memorije

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Proverite ažuriranja softvera

<!-- @require:software-update -->
<!-- @device:end -->

## Instalacija softverskih preduslova
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

## Instalacija n8n
<!-- @os:windows -->
Instalirajte n8n globalno koristeći npm.

> **Napomena**: Možda ćete videti neka npm upozorenja. To je očekivano.

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
> **Savet**: Korisnici sistema Windows možda će morati da izmene PowerShell Execution Policy (npr.
> postavljanjem na RemoteSigned ili Unrestricted) pre pokretanja nekih PowerShell komandi.
<!-- @os:end -->


<!-- @os:windows -->
> **Problem sa PATH**: Ako `n8n --version` kaže da komanda nije pronađena, proverite da li je vaš npm globalni bin direktorijum u korisničkom `PATH`. Uobičajena putanja instalacije je `C:\Users\<username>\AppData\Roaming\npm`.
> Dodajte ovo u korisnički path (Uredite sistemske promenljive okruženja > Promenljive okruženja > Uredi korisnički Path) i ponovo pokrenite terminal.

<!-- @os:end -->

<!-- @os:linux -->
Sada ćemo koristiti Podman servis za kontejnerizaciju naše n8n instalacije.

Preuzmite sledeće u direktorijum po vašem izboru: [compose.yml](assets/compose.yml)

U tom direktorijumu pokrenite sledeću komandu:
```bash
podman compose up -d
```

Ovo bi trebalo da instalira n8n i upiše podatke u trajno skladište.

Pokrenite n8n upisivanjem `localhost:5678` u adresnu traku pregledača.
<!-- @os:end -->

<!-- @os:windows -->
## Pokretanje n8n

Pokrenite n8n iz terminala:

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
n8n pokreće lokalni veb server. Pritisnite `'o'` ili otvorite pregledač na adresi `http://localhost:5678` da biste pristupili editoru.
<!-- @os:end -->


> **Savet**: Ostavite prozor terminala otvorenim dok koristite n8n. Zatvaranje može zaustaviti server.

## Pokretanje Lemonade

Lemonade je lokalni server koji će pokrenuti model i povezati se sa n8n.

<!-- @os:linux -->
Otvorite Lemonade GUI klikom na ikonu Lemonade u sistemskoj traci. Ovde možete pregledati modele, bekende i učitati unapred instalirane modele.
<!-- @os:end -->

<!-- @os:windows -->
Otvorite Lemonade GUI klikom na ikonu Lemonade. Desnim klikom na ikonu u sistemskoj traci otvorite aplikaciju. Zatim možete dodavati modele, bekende i učitavati unapred instalirane modele.
<!-- @os:end -->

>**Savet**: Kada je pokrenut, Lemonade GUI je takođe dostupan na adresi http://localhost:13305

Alternativno, možete otvoriti terminal i pokrenuti `lemonade list` da vidite koji su modeli instalirani. Zatim pokrenite:

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


## Postavljanje radnog toka

### Korak 1: Registrujte se ili prijavite u n8n

Kada prvi put otvorite n8n, bićete upitani da kreirate nalog ili se prijavite:

1. Otvorite `http://localhost:5678` u pregledaču
2. Kreirajte novi lokalni nalog sa svojom e-mail adresom ili se prijavite ako već imate nalog
3. Nakon prijave, videćete n8n kontrolnu tablu

> **Savet**: Ako ste zaključani iz svog naloga, pokušajte sa `n8n user-management:reset`

### Korak 2: Uvezite radni tok

Pripremili smo unapred izgrađen radni tok koji možete direktno uvesti:

1. Preuzmite sledeću datoteku radnog toka: [financial-news-workflow.json](assets/financial-news-workflow.json)
2. Kliknite **Start from Scratch** da biste otvorili editor radnog toka. Alternativno, kliknite dugme + u gornjem levom uglu, a zatim **Add workflow**.
3. Kliknite na meni **...** (tri tačke) u gornjem desnom uglu i izaberite **Import from file**
4. Izaberite preuzetu datoteku `financial-news-workflow.json`
5. Radni tok će se pojaviti na platnu


### Korak 3: Razumevanje radnog toka

Uvezeni radni tok sadrži 9 povezanih čvorova:

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| Čvor | Svrha |
|------|---------|
| **When clicking 'Execute workflow'** | Ručni okidač za pokretanje radnog toka |
| **Fetch Financial News Webpage** | HTTP GET zahtev ka `https://apnews.com/business` |
| **Delay to Ensure Page Load** | Čvor čekanja koji osigurava da je sadržaj stranice u potpunosti učitan |
| **Extract News Headlines & Text** | HTML čvor koji izvlači naslove, urednikove izbore, najvažnije vesti i regionalne vesti koristeći CSS selektore |
| **Clean Extracted News Data** | Set čvor koji kombinuje sve izvučene podatke u jedno tekstualno polje |
| **AI Financial News Summarizer** | AI Agent koji obrađuje vesti sa sistemskim promptom finansijskog analitičara |
| **Lemonade Chat Model** | Povezuje se sa vašim lokalnim Lemonade serverom koji pokreće LLM |
| **Structured Output Parser** | Formatira AI izlaz kao strukturirani JSON |
| **Convert to File** | Konvertuje rezime u datoteku za preuzimanje |

### Korak 4: Konfigurišite Lemonade akreditive

Pre pokretanja radnog toka, potrebno je da ga povežete sa vašim lokalnim Lemonade serverom:

1. Dvaput kliknite na čvor **Lemonade Chat Model** u n8n
2. U padajućem meniju **Credential to connect with** izaberite **Create New Credential**
3. Unesite vrednosti iz tabele ispod i kliknite sačuvaj.
4. Izaberite odgovarajući model koji ste učitali u Lemonade Server.

  | Polje | Vrednost |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **Napomena**: Pre testiranja, pokrenite `lemonade status` u terminalu da biste potvrdili da Lemonade server radi.
<!-- @device:halo_box -->
> Ovaj radni tok koristi GPT-OSS-120B i unapred je instaliran u Lemonade. Možete ga promeniti na druge učitane modele u podešavanjima čvora Lemonade Chat Model.
<!-- @device:end -->

### Korak 5: Testirajte radni tok

1. Proverite da li Lemonade radi sa učitanim modelom
2. Kliknite **Execute workflow** u donjem centru platna
3. Pratite izvršavanje svakog čvora s leva na desno — postaju zeleni kada su završeni
4. Dvaput kliknite na čvor **AI Financial News Summarizer** da biste videli generisani rezime u donjem oknu.
5. Dvaput kliknite na čvor **Convert to File** da biste preuzeli odgovarajuću tekstualnu datoteku u donjem oknu.

## Razumevanje AI agenta

AI Financial News Summarizer koristi sistemski prompt dizajniran za finansijsku analizu:

```
You are an AI financial analyst. Your role is to read, understand, and
summarize key financial news from today. The goal is to provide investors
with a clear and concise market overview to support better investment decisions.

Investor Outlook
Today's news points to [bullish/bearish/neutral] sentiment. Watch for
[economic event/earnings report] tomorrow, which could influence market direction.
```

Agent prima očišćene podatke o vestima i generiše strukturirani rezime sa tržišnim sentimentom.

### Čuvanje radnog toka

Kliknite na naziv radnog toka na vrhu i preimenujte ga ako želite. Radni tokovi se automatski čuvaju dok radite.

## Sledeći koraci

- **Zakazana automatizacija**: Zamenite ručni okidač sa **Schedule Trigger** za svakodnevno pokretanje
- **Slanje obaveštenja**: Dodajte čvor **Discord**, **Slack** ili **Email** za primanje rezimea
- **Isprobajte različite modele**: Promenite model u čvoru Lemonade Chat Model da eksperimentišete sa različitim LLM-ovima
- **Prilagodite ekstrakciju**: Izmenite CSS selektore čvora HTML Extract da ciljate različite sekcije vesti
- **Isprobajte različite bekende**: n8n takođe podržava [Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model), LM Studio i druge lokalne LLM bekende

### Istražite n8n šablone

n8n ima stotine unapred izgrađenih šablona radnih tokova. Pregledajte zvaničnu biblioteku šablona na:

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

Pretražite "AI", "LLM" ili "automation" da pronađete radne tokove koje možete uvesti i prilagoditi.

Za više informacija, pogledajte [n8n dokumentaciju](https://docs.n8n.io/).