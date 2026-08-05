<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Mašinski prevod.** Ova stranica je automatski prevedena sa engleskog jezika i nije proveravana od strane čoveka. Može sadržati greške, a određena uputstva, komande, preuzimanja, dostupnost proizvoda ili drugi sadržaj mogu se razlikovati u zavisnosti od jezika ili regiona. U slučaju bilo kakve nedoslednosti ili neslaganja, merodavna je originalna verzija playbook-a na engleskom jeziku.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->
## Pregled
<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Ovaj vodič zahteva minimum **32GB** sistemske memorije.
<!-- @device:end -->
n8n je platforma za automatizaciju radnih tokova koja vam omogućava da povežete aplikacije i usluge pomoću vizuelnog uređivača zasnovanog na čvorovima.

Ovaj vodič vas uči kako da podesite finansijski sumarizator vesti pokretan veštačkom inteligencijom koji skreipuje sekciju poslovnih vesti sa AP News, izdvaja ključne naslove i koristi lokalni LLM koji radi na vašem sistemu da generiše sažetak usmeren ka investitorima.

## Šta ćete naučiti

- Kako da instalirate i pokrenete n8n
- Uvoz i konfigurisanje unapred pripremljenog radnog toka
- Povezivanje sa Lemonade koristeći nativnu n8n integraciju
- Razumevanje čvorova radnog toka i toka podataka

## Šta je Lemonade?

[Lemonade](https://lemonade-server.ai) je platforma za lokalno posluživanje LLM-a napravljena za AMD hardver. Ona pruža API kompatibilan sa OpenAI koji radi u potpunosti na vašem računaru — vaši podaci nikada ne napuštaju vaš uređaj.

U ovom vodiču koristimo Lemonade da posluži lokalni LLM na koji se n8n povezuje radi zadataka pokretanih veštačkom inteligencijom.

n8n uključuje **nativni Lemonade čvor** (`Lemonade Chat Model`) koji pruža integraciju prve klase - nema potrebe za ručnim podešavanjem. Ovo čini povezivanje vašeg lokalnog LLM-a sa radnim tokovima automatizacije jednostavnim.

## Podešavanje konfiguracije memorije
<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Proveri ažuriranja softvera
<!-- @require:software-update -->
<!-- @device:end -->
## Instaliranje softverskih preduslova
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
Instalirajte n8n globalno pomoću npm-a.

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
> **Savet**: Korisnicima operativnog sistema Windows možda će biti potrebno da izmene svoju PowerShell Execution Policy (npr.
> podešavanjem na RemoteSigned ili Unrestricted) pre pokretanja pojedinih Powershell komandi.
<!-- @os:end -->


<!-- @os:windows -->
> **Problem sa PATH-om**: Ako `n8n --version` prijavi da komanda nije pronađena, proverite da li se npm globalni bin direktorijum nalazi u korisničkoj `PATH` promenljivoj. Uobičajena putanja instalacije je `C:\Users\<username>\AppData\Roaming\npm`.
> Dodajte ovo u korisničku putanju (Edit the system environment variables > Environment Variables > Edit User Path) i ponovo pokrenite terminal.
<!-- @os:end -->

<!-- @os:linux -->
Sada ćemo koristiti Podman servis da kontejnerizujemo našu n8n instalaciju.

Preuzmite sledeće u direktorijum po vašem izboru: [compose.yml](assets/compose.yml)

U tom direktorijumu pokrenite sledeću komandu:
```bash
podman compose up -d
```

Ovo bi trebalo da instalira n8n i upiše podatke u trajno skladište.

Pokrenite n8n tako što ćete otkucati `localhost:5678` u adresnu traku pretraživača.
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
n8n pokreće lokalni veb server. Pritisnite `'o'` ili otvorite pretraživač na `http://localhost:5678` da biste pristupili editoru.
<!-- @os:end -->
> **Savet**: Ostavite terminalski prozor otvoren dok koristite n8n. Zatvaranje prozora može zaustaviti server.

## Pokretanje Lemonade

Lemonade je lokalni server koji će pokretati model i povezati se sa n8n.
<!-- @os:linux -->
Otvorite Lemonade GUI klikom na ikonu Lemonade u traci zadataka. Odavde možete pregledati modele, bekende i učitati unapred instalirane modele.
<!-- @os:end -->

<!-- @os:windows -->
Otvorite Lemonade GUI klikom na ikonu Lemonade. Kliknite desnim tasterom miša na ikonu u traci da biste otvorili aplikaciju. Zatim možete dodati modele, bekende i učitati unapred instalirane modele.
<!-- @os:end -->
**Savet**: Kada je pokrenut, Lemonade GUI je takođe dostupan na http://localhost:13305

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
## Podešavanje toka rada

### Korak 1: Registracija ili prijava na n8n

Kada prvi put otvorite n8n, bićete pozvani da napravite nalog ili se prijavite:

1. Otvorite `http://localhost:5678` u pregledaču
2. Napravite novi lokalni nalog pomoću svoje e-adrese ili se prijavite ako već imate nalog
3. Kada se prijavite, videćete n8n kontrolnu tablu

> **Savet**: Ako izgubite pristup nalogu, probajte `n8n user-management:reset`

### Korak 2: Uvoz toka rada

Obezbedili smo unapred pripremljen tok rada koji možete direktno uvesti:

1. Preuzmite sledeću datoteku toka rada: [financial-news-workflow.json](assets/financial-news-workflow.json)
2. Kliknite na **Start from Scratch** da otvorite uređivač toka rada. Alternativno, kliknite na dugme + u gornjem levom uglu, a zatim na **Add workflow**.
3. Kliknite na meni **...** (tri tačke) u gornjoj desnoj traci i izaberite **Import from file**
4. Izaberite preuzetu datoteku `financial-news-workflow.json`
5. Tok rada će se pojaviti na platnu
### Korak 3: Razumevanje toka rada

Uvezeni tok rada sadrži 9 povezanih čvorova:

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| Čvor | Namena |
|------|---------|
| **When clicking 'Execute workflow'** | Ručni okidač za pokretanje toka rada |
| **Fetch Financial News Webpage** | HTTP GET zahtev ka `https://apnews.com/business` |
| **Delay to Ensure Page Load** | Wait čvor koji obezbeđuje da se sadržaj stranice u potpunosti učita |
| **Extract News Headlines & Text** | HTML čvor koji izdvaja naslove, izbore urednika, najvažnije vesti i regionalne vesti pomoću CSS selektora |
| **Clean Extracted News Data** | Set čvor koji objedinjuje sve izdvojene podatke u jedno tekstualno polje |
| **AI Financial News Summarizer** | AI agent koji obrađuje vesti pomoću sistemskog upita finansijskog analitičara |
| **Lemonade Chat Model** | Povezuje se sa vašim lokalnim Lemonade serverom na kojem je pokrenut LLM |
| **Structured Output Parser** | Formatira izlaz AI-ja u strukturirani JSON |
| **Convert to File** | Konvertuje rezime u fajl koji se može preuzeti |

### Korak 4: Konfigurisanje Lemonade akreditiva

Pre pokretanja toka rada, potrebno je da ga povežete sa vašim lokalnim Lemonade serverom:

1. Dvaput kliknite na čvor **Lemonade Chat Model** u n8n
2. U padajućem meniju **Credential to connect with** izaberite **Create New Credential**
3. Unesite vrednosti iz tabele ispod i kliknite na sačuvaj.
4. Izaberite odgovarajući model koji ste učitali na Lemonade Server.

  | Polje | Vrednost |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **Napomena**: Pre testiranja, pokrenite `lemonade status` u terminalu kako biste potvrdili da je Lemonade server pokrenut.
<!-- @device:halo_box -->
> Ovaj tok rada koristi GPT-OSS-120B, koji je unapred instaliran u Lemonade-u. Ovo možete promeniti na druge učitane modele u podešavanjima čvora Lemonade Chat Model.
<!-- @device:end -->

### Korak 5: Testiranje toka rada

1. Proverite da li je Lemonade pokrenut sa učitanim modelom
2. Kliknite na **Execute workflow** na dnu sredine platna
3. Posmatrajte kako se svaki čvor izvršava sleva nadesno — postaju zeleni kada su završeni
4. Dvaput kliknite na čvor **AI Financial News Summarizer** da vidite generisani rezime u donjem panelu.
5. Dvaput kliknite na čvor **Convert to File** da preuzmete odgovarajući tekstualni fajl u donjem panelu.

## Razumevanje AI agenta

AI Financial News Summarizer koristi sistemski upit dizajniran za finansijsku analizu:

```
You are an AI financial analyst. Your role is to read, understand, and
summarize key financial news from today. The goal is to provide investors
with a clear and concise market overview to support better investment decisions.

Investor Outlook
Today's news points to [bullish/bearish/neutral] sentiment. Watch for
[economic event/earnings report] tomorrow, which could influence market direction.
```

Agent prima očišćene podatke o vestima i generiše strukturirani rezime sa tržišnim sentimentom.

### Čuvanje vašeg toka rada

Kliknite na naziv toka rada pri vrhu i preimenujte ga ako želite. Tokovi rada se automatski čuvaju dok radite.

## Sledeći koraci

- **Zakazivanje automatizacije**: Zamenite Manual Trigger sa **Schedule Trigger** kako bi se pokretao svakodnevno
- **Slanje obaveštenja**: Dodajte **Discord**, **Slack** ili **Email** čvor da biste primali rezimee
- **Isprobajte različite modele**: Promenite model u čvoru Lemonade Chat Model da biste eksperimentisali sa različitim LLM-ovima
- **Prilagodite izdvajanje podataka**: Izmenite CSS selektore HTML Extract čvora da ciljate druge sekcije vesti
- **Isprobajte različite bekende**: n8n takođe podržava [Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model), LM Studio i druge lokalne LLM bekende

### Istražite n8n šablone

n8n ima na stotine unapred pripremljenih šablona toka rada. Pregledajte zvaničnu biblioteku šablona na:

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

Pretražite „AI“, „LLM“ ili „automatizacija“ da biste pronašli tokove rada koje možete uvesti i prilagoditi.

Za više informacija, pogledajte [n8n dokumentaciju](https://docs.n8n.io/).

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