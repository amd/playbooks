<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Machinevertaling.** Deze pagina is automatisch vertaald vanuit het Engels en is niet door een mens gecontroleerd. Deze pagina kan fouten bevatten en bepaalde instructies, opdrachten, downloads, productbeschikbaarheid of andere inhoud kan per taal of regio verschillen. In geval van tegenstrijdigheid of discrepantie is de oorspronkelijke Engelse versie van de playbook doorslaggevend en prevaleert deze.
<!-- auto-translated-disclaimer:end -->

Here is the translated document:

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Overzicht

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Deze playbook vereist minimaal **32GB** aan systeemgeheugen.
<!-- @device:end -->

n8n is een platform voor workflow-automatisering waarmee je apps en services kunt koppelen via een visuele, op knooppunten gebaseerde editor.

Deze playbook leert je hoe je een AI-gestuurde samenvatter voor financieel nieuws opzet die de laatste zakelijke koppen uit een nieuws-RSS-feed haalt en een lokale LLM op je systeem gebruikt om een op beleggers gerichte samenvatting te genereren.

## Wat je gaat leren

- Hoe je n8n installeert en start
- Een vooraf gebouwde workflow importeren en configureren
- Verbinding maken met Lemonade via de native n8n-integratie
- Workflow-knooppunten en gegevensstroom begrijpen

## Wat is Lemonade?

[Lemonade](https://lemonade-server.ai) is een platform voor het lokaal serveren van LLM's, gebouwd voor AMD-hardware. Het biedt een OpenAI-compatibele API die volledig op je machine draait—je gegevens verlaten nooit je apparaat.

In deze playbook gebruiken we Lemonade om een lokale LLM te serveren waarmee n8n verbinding maakt voor AI-gestuurde taken.

n8n bevat een **native Lemonade-knooppunt** (`Lemonade Chat Model`) dat een eersteklas integratie biedt - geen handmatige configuratie nodig. Dit maakt het eenvoudig om je lokale LLM te koppelen aan automatiseringsworkflows.

<!-- @device:halo_box,halo,stx,krk -->
## De geheugenconfiguratie instellen

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Controleren op software-updates

<!-- @require:software-update -->
<!-- @device:end -->

## Software-vereisten installeren
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

## n8n installeren
<!-- @os:windows -->
Installeer n8n globaal met npm.

> **Opmerking**: Je ziet mogelijk enkele npm-waarschuwingen. Dit is normaal.

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
> **Tip**: Windows-gebruikers moeten mogelijk hun PowerShell Execution Policy aanpassen (bijvoorbeeld
> instellen op RemoteSigned of Unrestricted) voordat ze bepaalde Powershell-commando's uitvoeren.
<!-- @os:end -->


<!-- @os:windows -->
> **PATH-probleem**: Als `n8n --version` aangeeft dat het commando niet wordt gevonden, zorg er dan voor dat je npm global bin-directory zich in de gebruikers-`PATH` bevindt. Het gebruikelijke installatiepad is `C:\Users\<username>\AppData\Roaming\npm`.
> Voeg dit toe aan het gebruikerspad (Bewerk de systeemomgevingsvariabelen > Omgevingsvariabelen > Gebruikerspad bewerken) en herlaad de terminal.

<!-- @os:end -->

<!-- @os:linux -->
We gaan nu de Podman-service gebruiken om onze n8n-installatie te containeriseren.

Download het volgende naar een map naar keuze: [compose.yml](assets/compose.yml)

Voer in die map het volgende commando uit:
```bash
podman compose up -d
```

Dit zou n8n moeten installeren en naar persistente opslag moeten schrijven.

Start n8n door `localhost:5678` in te typen in je browseradresbalk.
<!-- @os:end -->

<!-- @os:windows -->
## n8n starten

Start n8n vanaf de terminal:

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
n8n start een lokale webserver. Druk op `'o'` of open je browser naar `http://localhost:5678` om toegang te krijgen tot de editor.
<!-- @os:end -->


> **Tip**: Houd het terminalvenster open terwijl je n8n gebruikt. Als je het sluit, kan de server stoppen.

## Lemonade starten

Lemonade is de lokale server die een model uitvoert en verbinding maakt met n8n.

<!-- @os:linux -->
Open de Lemonade-GUI door op het Lemonade-pictogram in de taakbalk te klikken. Je kunt hier modellen en backends bekijken en de vooraf geïnstalleerde modellen laden.
<!-- @os:end -->

<!-- @os:windows -->
Open de Lemonade-GUI door op het Lemonade-pictogram te klikken. Klik met de rechtermuisknop op het systeemvakpictogram om de app te openen. Daarna kun je modellen en backends toevoegen en de vooraf geïnstalleerde modellen laden.
<!-- @os:end -->

>**Tip**: Eenmaal actief, is de Lemonade-GUI ook toegankelijk via http://localhost:13305

Als alternatief kun je een terminal openen en `lemonade list` uitvoeren om te zien welke modellen zijn geïnstalleerd. Voer vervolgens uit:

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


## De workflow instellen

### Stap 1: Aanmelden of inloggen bij n8n

Wanneer je n8n voor het eerst opent, word je gevraagd een account aan te maken of in te loggen:

1. Open `http://localhost:5678` in je browser
2. Maak een nieuw lokaal account aan met je e-mailadres, of log in als je er al een hebt
3. Zodra je bent ingelogd, zie je het n8n-dashboard

> **Tip**: Als je bent buitengesloten van je account, probeer dan `n8n user-management:reset`

### Stap 2: De workflow importeren

We hebben een vooraf gebouwde workflow beschikbaar gesteld die je direct kunt importeren:

1. Download het volgende workflowbestand: [financial-news-workflow.json](assets/financial-news-workflow.json)
2. Klik op **Start from Scratch** om de workflow-editor te openen. Je kunt ook op de +-knop linksboven klikken en vervolgens op **Add workflow**.
3. Klik op het **...**-menu (drie puntjes) in de rechterbovenbalk en selecteer **Import from file**
4. Selecteer het gedownloade bestand `financial-news-workflow.json`
5. De workflow verschijnt op het canvas
### Stap 3: De workflow begrijpen

De geïmporteerde workflow bevat 8 verbonden nodes:

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| Node | Doel |
|------|---------|
| **When clicking 'Execute workflow'** | Handmatige trigger om de workflow te starten |
| **Fetch Financial News Feed** | RSS Read-node die de nieuwste zakelijke koppen ophaalt van een RSS-feed (standaard de NYT Business-feed, geen API-sleutel vereist) |
| **Aggregate Headlines** | Aggregate-node die de titels en samenvattingen van alle feed-items verzamelt in één lijst |
| **Clean Extracted News Data** | Set-node die alle koppen combineert tot één tekstveld |
| **AI Financial News Summarizer** | AI Agent die het nieuws verwerkt met een systeemprompt voor financieel analist |
| **Lemonade Chat Model** | Maakt verbinding met je lokale Lemonade-server waarop de LLM draait |
| **Structured Output Parser** | Formatteert de AI-uitvoer als gestructureerde JSON |
| **Convert to File** | Converteert de samenvatting naar een downloadbaar bestand |

> **Tip**: Om een andere nieuwsbron te gebruiken, dubbelklik je op de node **Fetch Financial News Feed** en vervang je de URL door een zakelijke of markten-RSS-feed naar keuze.

### Stap 4: Lemonade-inloggegevens configureren

Voordat je de workflow uitvoert, moet je deze verbinden met je lokale Lemonade-server:

1. Dubbelklik op de node **Lemonade Chat Model** in n8n
2. Selecteer in het dropdownmenu **Credential to connect with** de optie **Create New Credential**
3. Voer de waarden uit onderstaande tabel in en klik op opslaan.
4. Kies het relevante model dat je in Lemonade Server hebt geladen.

  | Veld | Waarde |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **Opmerking**: Voer voordat je gaat testen `lemonade status` uit in een terminal om te bevestigen dat de Lemonade-server actief is.
<!-- @device:halo_box -->
> Deze workflow gebruikt GPT-OSS-120B en dit is vooraf geïnstalleerd in Lemonade. Je kunt dit wijzigen naar andere geladen modellen in de instellingen van de Lemonade Chat Model-node.
<!-- @device:end -->

### Stap 5: De workflow testen

1. Zorg ervoor dat Lemonade actief is met een geladen model
2. Klik op **Execute workflow** onderaan in het midden van het canvas
3. Bekijk hoe elke node van links naar rechts wordt uitgevoerd—ze worden groen zodra ze klaar zijn
4. Dubbelklik op de node **AI Financial News Summarizer** om de gegenereerde samenvatting in het onderste paneel te bekijken.
5. Dubbelklik op de node **Convert to File** om het bijbehorende tekstbestand in het onderste paneel te downloaden.

## De AI Agent begrijpen

De AI Financial News Summarizer gebruikt een systeemprompt die is ontworpen voor financiële analyse:

```
You are an AI financial analyst. Your role is to read, understand, and
summarize key financial news from today. The goal is to provide investors
with a clear and concise market overview to support better investment decisions.

Investor Outlook
Today's news points to [bullish/bearish/neutral] sentiment. Watch for
[economic event/earnings report] tomorrow, which could influence market direction.
```

De agent ontvangt de opgeschoonde nieuwsgegevens en geeft een gestructureerde samenvatting met marktsentiment als uitvoer.

### Je workflow opslaan

Klik bovenaan op de workflownaam en hernoem deze indien gewenst. Workflows worden automatisch opgeslagen terwijl je werkt.

## Volgende stappen

- **Automatisering plannen**: Vervang de Manual Trigger door een **Schedule Trigger** om dagelijks uit te voeren
- **Meldingen versturen**: Voeg een **Discord**-, **Slack**- of **Email**-node toe om samenvattingen te ontvangen
- **Verschillende modellen proberen**: Wijzig het model in de Lemonade Chat Model-node om te experimenteren met verschillende LLM's
- **De nieuwsbron wijzigen**: Laat de node **Fetch Financial News Feed** verwijzen naar een andere RSS-feed om andere rubrieken of publicaties te volgen
- **Verschillende backends proberen**: n8n ondersteunt ook [Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model), LM Studio en andere lokale LLM-backends

### n8n-sjablonen verkennen

n8n beschikt over honderden kant-en-klare workflowsjablonen. Blader door de officiële sjabloonbibliotheek op:

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

Zoek naar "AI", "LLM" of "automation" om workflows te vinden die je kunt importeren en aanpassen.

Raadpleeg voor meer informatie de [n8n-documentatie](https://docs.n8n.io/).

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