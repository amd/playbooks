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
# Pregled
<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Ovaj vodič zahteva minimum **32GB** sistemske memorije.
<!-- @device:end -->
n8n je platforma za automatizaciju radnih tokova koja vam omogućava da povežete aplikacije i usluge pomoću vizuelnog uređivača zasnovanog na čvorovima.

Ovaj vodič vas uči kako da podesite finansijski sumator vesti pokretan veštačkom inteligencijom koji preuzima najnovije poslovne naslove sa RSS fida vesti i koristi lokalni LLM koji radi na vašem sistemu da generiše sažetak orijentisan ka investitorima.

## Šta ćete naučiti

- Kako da instalirate i pokrenete n8n
- Uvoz i konfigurisanje unapred pripremljenog radnog toka
- Povezivanje sa Lemonade koristeći nativnu n8n integraciju
- Razumevanje čvorova radnog toka i protoka podataka

## Šta je Lemonade?

[Lemonade](https://lemonade-server.ai) je platforma za lokalno posluživanje LLM-ova napravljena za AMD hardver. Pruža API kompatibilan sa OpenAI-jem koji radi u potpunosti na vašem računaru—vaši podaci nikada ne napuštaju vaš uređaj.

U ovom vodiču koristimo Lemonade za posluživanje lokalnog LLM-a na koji se n8n povezuje radi zadataka pokretanih veštačkom inteligencijom.

n8n uključuje **nativni Lemonade čvor** (`Lemonade Chat Model`) koji pruža integraciju prve klase - nema potrebe za ručnim podešavanjem. Ovo čini povezivanje vašeg lokalnog LLM-a sa radnim tokovima automatizacije jednostavnim.
<!-- @device:halo_box,halo,stx,krk -->
## Podešavanje konfiguracije memorije
<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Proverite ažuriranja softvera
<!-- @require:software-update -->
<!-- @device:end -->
## Instalacija potrebnog softvera
<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @prereq:n8n,lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- Linux runs n8n as a Podman container (see compose.yml below), so Node.js and a host n8n install are not required; podman is the only extra prerequisite. -->
<!-- @require:lemonade,podman -->
<!-- @prereq:podman -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<!-- @prereq:lemonade-models-gpt-oss-120b -->
<!-- @var:id=lemonade_model value="gpt-oss-120b-mxfp-GGUF" -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @prereq:lemonade-models-gpt-oss-20b -->
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

<!-- @os:windows -->
<!-- @test:id=node-npm-version timeout=60 hidden=True -->
```bash
node -v
npm -v
```
<!-- @test:end -->
<!-- @os:end -->
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

<!-- @os:windows -->
> **Savet**: Korisnicima Windows-a možda će biti potrebno da izmene svoju PowerShell Execution Policy (npr.
> postavljanjem na RemoteSigned ili Unrestricted) pre pokretanja nekih PowerShell komandi.
<!-- @os:end -->


<!-- @os:windows -->
> **Problem sa PATH-om**: Ako `n8n --version` prijavi da komanda nije pronađena, uverite se da se vaš npm globalni bin direktorijum nalazi u korisničkom `PATH`-u. Uobičajena putanja instalacije je `C:\Users\<username>\AppData\Roaming\npm`.
> Dodajte ovo u korisničku putanju (Edit the system environment variables > Environment Variables > Edit User Path) i ponovo učitajte terminal.
<!-- @os:end -->

<!-- @os:linux -->
Sada ćemo koristiti Podman servis da kontejnerizujemo našu n8n instalaciju.

Preuzmite sledeće u direktorijum po vašem izboru: [compose.yml](assets/compose.yml)

U tom direktorijumu pokrenite sledeću komandu:
```bash
podman compose up -d
```

Ovo bi trebalo da instalira n8n i upiše podatke u trajno skladište.

Pokrenite n8n tako što ćete u adresnu traku pretraživača uneti `localhost:5678`.
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

export PODMAN_COMPOSE_PROVIDER="$(command -v podman-compose)"
cleanup() {
  podman compose -f compose.yml down >/dev/null 2>&1 || true
}
trap cleanup EXIT

podman rm -f n8n >/dev/null 2>&1 || true
podman compose -f compose.yml up -d

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
  podman ps -a || true
  podman logs n8n 2>&1 | tail -30 || true
  exit 1
fi

echo "OK: n8n server is responding"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
n8n pokreće lokalni veb server. Pritisnite `'o'` ili otvorite pregledač na `http://localhost:5678` da biste pristupili uređivaču.
<!-- @os:end -->
> **Savet**: Ostavite prozor terminala otvoren dok koristite n8n. Ako ga zatvorite, server bi mogao da se zaustavi.

## Pokretanje Lemonade

Lemonade je lokalni server koji pokreće model i povezuje se sa n8n.
<!-- @os:linux -->
Otvorite Lemonade GUI klikom na ikonu Lemonade na traci zadataka. Odavde možete pregledati modele, bekende i učitati unapred instalirane modele.
<!-- @os:end -->

<!-- @os:windows -->
Otvorite Lemonade GUI klikom na ikonu Lemonade. Kliknite desnim tasterom na ikonu u traci da biste otvorili aplikaciju. Zatim možete da dodate modele, pozadinske mehanizme (backends) i učitate unapred instalirane modele.
<!-- @os:end -->
>**Savet**: Kada se pokrene, Lemonade GUI je takođe dostupan na http://localhost:13305

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

### Korak 1: Registrujte se ili se prijavite na n8n

Kada prvi put otvorite n8n, bićete pozvani da kreirate nalog ili se prijavite:

1. Otvorite `http://localhost:5678` u pretraživaču
2. Kreirajte novi lokalni nalog pomoću svoje e-pošte ili se prijavite ako ga već imate
3. Nakon prijavljivanja, videćete n8n kontrolnu tablu

> **Savet**: Ako ste zaključani van svog naloga, probajte `n8n user-management:reset`

### Korak 2: Uvezite tok rada

Obezbedili smo unapred pripremljen tok rada koji možete direktno uvesti:

1. Preuzmite sledeću datoteku toka rada: [financial-news-workflow.json](assets/financial-news-workflow.json)
2. Kliknite na **Start from Scratch** da biste otvorili editor toka rada. Alternativno, kliknite na dugme + u gornjem levom uglu, a zatim na **Add workflow**.
3. Kliknite na meni **...** (tri tačke) u gornjoj desnoj traci i izaberite **Import from file**
4. Izaberite preuzetu datoteku `financial-news-workflow.json`
5. Tok rada će se pojaviti na platnu
### Korak 3: Razumevanje toka rada

Uvezeni tok rada sadrži 8 povezanih čvorova:

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| Čvor | Namena |
|------|---------|
| **When clicking 'Execute workflow'** | Ručni okidač za pokretanje toka rada |
| **Fetch Financial News Feed** | RSS Read čvor koji preuzima najnovije naslove iz oblasti poslovanja sa RSS feeda (podrazumevano koristi NYT Business feed, API ključ nije potreban) |
| **Aggregate Headlines** | Aggregate čvor koji sakuplja naslove i sažetke iz svake stavke feeda u jedinstvenu listu |
| **Clean Extracted News Data** | Set čvor koji kombinuje sve naslove u jedno tekstualno polje |
| **AI Financial News Summarizer** | AI Agent koji obrađuje vesti koristeći sistemski prompt finansijskog analitičara |
| **Lemonade Chat Model** | Povezuje se sa vašim lokalnim Lemonade serverom na kom je pokrenut LLM |
| **Structured Output Parser** | Formatira izlaz AI modela kao strukturirani JSON |
| **Convert to File** | Pretvara sažetak u fajl koji se može preuzeti |

> **Savet**: Da biste koristili drugačiji izvor vesti, dvaput kliknite na čvor **Fetch Financial News Feed** i zamenite URL bilo kojim poslovnim ili tržišnim RSS feedom po želji.

### Korak 4: Konfigurisanje Lemonade kredencijala

Pre pokretanja toka rada, potrebno je da ga povežete sa vašim lokalnim Lemonade serverom:

1. Dvaput kliknite na čvor **Lemonade Chat Model** u n8n
2. U padajućem meniju **Credential to connect with** izaberite **Create New Credential**
3. Unesite vrednosti iz tabele ispod i kliknite na „save".
4. Izaberite odgovarajući model koji ste učitali u Lemonade Server.

  | Polje | Vrednost |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **Napomena**: Pre testiranja, pokrenite `lemonade status` u terminalu da biste potvrdili da je Lemonade server pokrenut.
<!-- @device:halo_box -->
> Ovaj tok rada koristi GPT-OSS-120B koji je unapred instaliran u Lemonade-u. Ovo možete promeniti u druge učitane modele u podešavanjima čvora Lemonade Chat Model.
<!-- @device:end -->

### Korak 5: Testiranje toka rada

1. Proverite da je Lemonade pokrenut sa učitanim modelom
2. Kliknite na **Execute workflow** u donjem centralnom delu platna
3. Posmatrajte kako se svaki čvor izvršava sleva nadesno — postaju zeleni kada se završe
4. Dvaput kliknite na čvor **AI Financial News Summarizer** da vidite generisani sažetak u donjem panelu.
5. Dvaput kliknite na čvor **Convert to File** da preuzmete odgovarajući tekstualni fajl u donjem panelu.

## Razumevanje AI Agenta

AI Financial News Summarizer koristi sistemski prompt dizajniran za finansijsku analizu:

```
You are an AI financial analyst. Your role is to read, understand, and
summarize key financial news from today. The goal is to provide investors
with a clear and concise market overview to support better investment decisions.

Investor Outlook
Today's news points to [bullish/bearish/neutral] sentiment. Watch for
[economic event/earnings report] tomorrow, which could influence market direction.
```

Agent prima očišćene podatke o vestima i generiše strukturirani sažetak sa tržišnim sentimentom.

### Čuvanje toka rada

Kliknite na naziv toka rada pri vrhu i preimenujte ga po želji. Tokovi rada se automatski čuvaju dok radite.

## Sledeći koraci

- **Zakazivanje automatizacije**: Zamenite Manual Trigger sa **Schedule Trigger** da bi se pokretao svakodnevno
- **Slanje obaveštenja**: Dodajte **Discord**, **Slack** ili **Email** čvor da primate sažetke
- **Isprobajte različite modele**: Promenite model u čvoru Lemonade Chat Model da eksperimentišete sa različitim LLM-ovima
- **Promenite izvor vesti**: Usmerite čvor **Fetch Financial News Feed** na drugi RSS feed da pratite druge sekcije ili publikacije
- **Isprobajte različite backend-ove**: n8n takođe podržava [Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model), LM Studio i druge lokalne LLM backend-ove

### Istražite n8n šablone

n8n ima stotine unapred pripremljenih šablona toka rada. Pregledajte zvaničnu biblioteku šablona na:

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

Pretražite "AI", "LLM" ili "automation" da pronađete tokove rada koje možete uvesti i prilagoditi.

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