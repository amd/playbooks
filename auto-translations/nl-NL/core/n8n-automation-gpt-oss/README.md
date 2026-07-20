<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Deze playbook gebruikt speciale tags die GitHub niet kan weergeven. Bezoek [amd.com/playbooks](https://amd.com/playbooks) om deze inhoud correct te bekijken.
<!-- @github-only:end -->

## Overzicht

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Deze playbook vereist minimaal **32GB** systeemgeheugen.
<!-- @device:end -->

n8n is een workflow-automatiseringsplatform waarmee je apps en services kunt koppelen via een visuele, node-gebaseerde editor.

Deze playbook leert je hoe je een AI-gestuurde samenvatter voor financieel nieuws opzet die de zakelijke sectie van AP News scraped, belangrijke kopregels extraheert en een lokale LLM op je systeem gebruikt om een samenvatting te genereren gericht op investeerders.

## Wat je gaat leren

- Hoe je n8n installeert en start
- Een vooraf gebouwde workflow importeren en configureren
- Verbinding maken met Lemonade via de native n8n-integratie
- Workflow-nodes en gegevensstroom begrijpen

## Wat is Lemonade?

[Lemonade](https://lemonade-server.ai) is een platform voor het lokaal serveren van LLM's, gebouwd voor AMD-hardware. Het biedt een OpenAI-compatibele API die volledig op je eigen machine draait—je gegevens verlaten nooit je apparaat.

In deze playbook gebruiken we Lemonade om een lokale LLM te serveren waarmee n8n verbinding maakt voor AI-gestuurde taken.

n8n bevat een **native Lemonade-node** (`Lemonade Chat Model`) die een eersteklas integratie biedt - geen handmatige configuratie nodig. Dit maakt het verbinden van je lokale LLM met automatiseringsworkflows eenvoudig.

## De geheugenconfiguratie instellen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Controleren op software-updates

<!-- @require:software-update -->
<!-- @device:end -->

## Software-vereisten installeren
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

<!-- @os:linux -->
<!-- @test:id=n8n-version timeout=60 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
n8n --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
> **Tip**: Windows-gebruikers moeten mogelijk hun PowerShell Execution Policy aanpassen (bijvoorbeeld
> instellen op RemoteSigned of Unrestricted) voordat ze bepaalde PowerShell-commando's uitvoeren.
<!-- @os:end -->


<!-- @os:windows -->
> **PAD-probleem**: Als `n8n --version` aangeeft dat het commando niet is gevonden, zorg er dan voor dat je npm globale bin-directory zich in het gebruikers-`PATH` bevindt. Het gebruikelijke installatiepad is `C:\Users\<username>\AppData\Roaming\npm`.
> Voeg dit toe aan het gebruikerspad (Systeemomgevingsvariabelen bewerken > Omgevingsvariabelen > Gebruikerspad bewerken) en herlaad de terminal.

<!-- @os:end -->

<!-- @os:linux -->
We gaan nu de Podman-service gebruiken om onze n8n-installatie te containeriseren.

Download het volgende naar een map naar keuze: [compose.yml](assets/compose.yml)

Voer in die map het volgende commando uit:
```bash
podman compose up -d
```

Dit zou n8n moeten installeren en naar persistente opslag moeten schrijven.

Start n8n door `localhost:5678` in te typen in de adresbalk van je browser.
<!-- @os:end -->

<!-- @os:windows -->
## n8n starten

Start n8n vanuit de terminal:

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
n8n start een lokale webserver. Druk op `'o'` of open je browser naar `http://localhost:5678` om toegang te krijgen tot de editor.
<!-- @os:end -->


> **Tip**: Houd het terminalvenster open terwijl je n8n gebruikt. Als je het sluit, kan de server stoppen.

## Lemonade starten

Lemonade is de lokale server die een model uitvoert en verbinding maakt met n8n.

<!-- @os:linux -->
Open de Lemonade GUI door op het Lemonade-pictogram in de taakbalk te klikken. Hier kun je modellen en backends bekijken en de vooraf geïnstalleerde modellen laden.
<!-- @os:end -->

<!-- @os:windows -->
Open de Lemonade GUI door op het Lemonade-pictogram te klikken. Klik met de rechtermuisknop op het pictogram in het systeemvak om de app te openen. Vervolgens kun je modellen en backends toevoegen en de vooraf geïnstalleerde modellen laden.
<!-- @os:end -->

>**Tip**: Zodra deze actief is, is de Lemonade GUI ook bereikbaar via http://localhost:13305

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

### Stap 1: Aanmelden bij of inloggen op n8n

Wanneer je n8n voor het eerst opent, wordt je gevraagd een account aan te maken of in te loggen:

1. Open `http://localhost:5678` in je browser
2. Maak een nieuw lokaal account aan met je e-mailadres, of log in als je er al een hebt
3. Zodra je bent ingelogd, zie je het n8n-dashboard

> **Tip**: Als je bent buitengesloten van je account, probeer dan `n8n user-management:reset`

### Stap 2: De workflow importeren

We hebben een vooraf gebouwde workflow beschikbaar gesteld die je direct kunt importeren:

1. Download het volgende workflowbestand: [financial-news-workflow.json](assets/financial-news-workflow.json)
2. Klik op **Start from Scratch** om de workfloweditor te openen. Je kunt ook op de +-knop linksboven klikken en vervolgens op **Add workflow**.
3. Klik op het **...**-menu (drie stippen) rechtsboven en selecteer **Import from file**
4. Selecteer het gedownloade bestand `financial-news-workflow.json`
5. De workflow verschijnt op het canvas
### Stap 3: De workflow begrijpen

De geïmporteerde workflow bevat 9 verbonden nodes:

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| Node | Doel |
|------|---------|
| **When clicking 'Execute workflow'** | Handmatige trigger om de workflow te starten |
| **Fetch Financial News Webpage** | HTTP GET-verzoek naar `https://apnews.com/business` |
| **Delay to Ensure Page Load** | Wait-node om ervoor te zorgen dat de paginainhoud volledig is geladen |
| **Extract News Headlines & Text** | HTML-node die koppen, redactionele keuzes, topverhalen en regionaal nieuws extraheert met behulp van CSS-selectors |
| **Clean Extracted News Data** | Set-node die alle geëxtraheerde gegevens combineert in één tekstveld |
| **AI Financial News Summarizer** | AI Agent die het nieuws verwerkt met een systeemprompt voor financiële analisten |
| **Lemonade Chat Model** | Maakt verbinding met uw lokale Lemonade-server waarop het LLM draait |
| **Structured Output Parser** | Formatteert de AI-uitvoer als gestructureerde JSON |
| **Convert to File** | Zet de samenvatting om in een downloadbaar bestand |

### Stap 4: Lemonade-referenties configureren

Voordat u de workflow uitvoert, moet u deze verbinden met uw lokale Lemonade-server:

1. Dubbelklik op de **Lemonade Chat Model**-node in n8n
2. Selecteer in het vervolgkeuzemenu **Credential to connect with** de optie **Create New Credential**
3. Voer de waarden in de onderstaande tabel in en klik op opslaan.
4. Kies het relevante model dat u in Lemonade Server hebt geladen.

  | Veld | Waarde |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **Opmerking**: Voordat u gaat testen, voert u `lemonade status` uit in een terminal om te bevestigen dat de Lemonade-server actief is.
<!-- @device:halo_box -->
> Deze workflow gebruikt GPT-OSS-120B, dat vooraf is geïnstalleerd in Lemonade. U kunt dit wijzigen naar andere geladen modellen in de instellingen van de Lemonade Chat Model-node.
<!-- @device:end -->

### Stap 5: De workflow testen

1. Zorg ervoor dat Lemonade actief is met een geladen model
2. Klik op **Execute workflow** onderaan in het midden van het canvas
3. Bekijk hoe elke node van links naar rechts wordt uitgevoerd — ze worden groen zodra ze klaar zijn
4. Dubbelklik op de **AI Financial News Summarizer**-node om de gegenereerde samenvatting in het onderste paneel te bekijken.
5. Dubbelklik op de **Convert to File**-node om het bijbehorende tekstbestand in het onderste paneel te downloaden.

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

De agent ontvangt de opgeschoonde nieuwsgegevens en genereert een gestructureerde samenvatting met marktsentiment.

### Uw workflow opslaan

Klik bovenaan op de workflownaam en hernoem deze indien gewenst. Workflows worden automatisch opgeslagen terwijl u werkt.

## Volgende stappen

- **Automatisering plannen**: Vervang de Manual Trigger door een **Schedule Trigger** om dagelijks uit te voeren
- **Meldingen versturen**: Voeg een **Discord**-, **Slack**- of **Email**-node toe om samenvattingen te ontvangen
- **Verschillende modellen proberen**: Wijzig het model in de Lemonade Chat Model-node om te experimenteren met verschillende LLM's
- **Extractie aanpassen**: Wijzig de CSS-selectors van de HTML Extract-node om verschillende nieuwssecties te targeten
- **Verschillende backends proberen**: n8n ondersteunt ook [Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model), LM Studio en andere lokale LLM-backends

### n8n-templates verkennen

n8n beschikt over honderden kant-en-klare workflowtemplates. Blader door de officiële templatebibliotheek op:

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

Zoek naar "AI", "LLM" of "automation" om workflows te vinden die u kunt importeren en aanpassen.

Raadpleeg voor meer informatie de [n8n-documentatie](https://docs.n8n.io/).