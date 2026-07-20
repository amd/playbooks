<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->

> [!IMPORTANT]
> Denne playbook bruger specielle tags, som GitHub ikke kan gengive. Besøg venligst [amd.com/playbooks](https://amd.com/playbooks) for at få vist dette indhold korrekt.
<!-- @github-only:end -->

## Oversigt

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->

> [!NOTE]
> Denne playbook kræver mindst **32 GB** systemhukommelse.
<!-- @device:end -->

n8n er en platform til workflow-automatisering, der giver dig mulighed for at forbinde apps og tjenester ved hjælp af en visuel, node-baseret editor.

Denne playbook lærer dig, hvordan du opsætter en AI-drevet opsummering af finansnyheder, der scraper erhvervssektionen på AP News, udtrækker de vigtigste overskrifter og bruger en lokal LLM, der kører på dit system, til at generere et investorfokuseret resumé.

## Hvad du lærer

- Hvordan du installerer og starter n8n
- Import og konfiguration af et færdigbygget workflow
- Forbindelse til Lemonade ved hjælp af den indbyggede n8n-integration
- Forståelse af workflow-noder og datastrøm

## Hvad er Lemonade?

[Lemonade](https://lemonade-server.ai) er en platform til lokal servering af LLM'er, bygget til AMD-hardware. Den tilbyder en OpenAI-kompatibel API, der kører fuldstændigt på din maskine – dine data forlader aldrig din enhed.

I denne playbook bruger vi Lemonade til at servere en lokal LLM, som n8n forbinder til for AI-drevne opgaver.

n8n indeholder en **indbygget Lemonade-node** (`Lemonade Chat Model`), der giver en førsteklasses integration – ingen grund til manuel konfiguration. Dette gør det enkelt at forbinde din lokale LLM til automatiserede workflows.

## Konfiguration af hukommelse

<!-- @require:memory-config -->

<!-- @device:halo_box -->

## Tjek for softwareopdateringer

<!-- @require:software-update -->
<!-- @device:end -->

## Installation af softwareforudsætninger
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

## Installation af n8n
<!-- @os:windows -->
Installer n8n globalt ved hjælp af npm.

> **Bemærk**: Du kan se nogle npm-advarsler. Dette er forventet.

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
> **Tip**: Windows-brugere skal muligvis ændre deres PowerShell Execution Policy (f.eks.
> sætte den til RemoteSigned eller Unrestricted), før de kører nogle PowerShell-kommandoer.
<!-- @os:end -->


<!-- @os:windows -->
> **PATH-problem**: Hvis `n8n --version` siger, at kommandoen ikke blev fundet, skal du sikre dig, at din globale npm bin-mappe er tilføjet til brugerens `PATH`. Den sædvanlige installationssti er `C:\Users\<username>\AppData\Roaming\npm`.
> Tilføj denne til brugerens sti (Rediger systemets miljøvariabler > Miljøvariabler > Rediger brugersti) og genindlæs terminalen.

<!-- @os:end -->

<!-- @os:linux -->
Vi skal nu bruge Podman-tjenesten til at containerisere vores n8n-installation.

Download venligst følgende til en mappe efter eget valg: [compose.yml](assets/compose.yml)

Kør følgende kommando i den pågældende mappe:
```bash
podman compose up -d
```

Dette bør installere n8n og skrive til vedvarende lagring.

Start n8n ved at indtaste `localhost:5678` i din browsers adresselinje.
<!-- @os:end -->

<!-- @os:windows -->
## Start af n8n

Start n8n fra terminalen:

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
n8n starter en lokal webserver. Tryk på `'o'` eller åbn din browser på `http://localhost:5678` for at få adgang til editoren.
<!-- @os:end -->


> **Tip**: Hold terminalvinduet åbent, mens du bruger n8n. Hvis du lukker det, kan det stoppe serveren.

## Start af Lemonade

Lemonade er den lokale server, der kører en model og forbinder til n8n.

<!-- @os:linux -->
Åbn Lemonade-GUI'en ved at klikke på Lemonade-ikonet på proceslinjen. Herfra kan du gennemse modeller, backends og indlæse de forudinstallerede modeller.
<!-- @os:end -->

<!-- @os:windows -->
Åbn Lemonade-GUI'en ved at klikke på Lemonade-ikonet. Højreklik på bakkeikonet for at åbne appen. Herefter kan du tilføje modeller, backends og indlæse de forudinstallerede modeller.
<!-- @os:end -->

>**Tip**: Når den kører, kan Lemonade-GUI'en også tilgås på http://localhost:13305

Alternativt kan du åbne en terminal og køre `lemonade list` for at se, hvilke modeller der er installeret. Kør derefter:

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


## Opsætning af workflowet

### Trin 1: Tilmeld dig eller log ind på n8n

Når du åbner n8n for første gang, bliver du bedt om at oprette en konto eller logge ind:

1. Åbn `http://localhost:5678` i din browser
2. Opret en ny lokal konto med din e-mail, eller log ind, hvis du allerede har en
3. Når du er logget ind, ser du n8n-dashboardet

> **Tip**: Hvis du er låst ude af din konto, kan du prøve `n8n user-management:reset`

### Trin 2: Importer workflowet

Vi har leveret et færdigbygget workflow, som du kan importere direkte:

1. Download følgende workflow-fil: [financial-news-workflow.json](assets/financial-news-workflow.json)
2. Klik på **Start from Scratch** for at åbne workflow-editoren. Alternativt kan du klikke på +-knappen øverst til venstre og derefter vælge **Add workflow**.
3. Klik på **...**-menuen (tre prikker) i den øverste højre bjælke, og vælg **Import from file**
4. Vælg den downloadede fil `financial-news-workflow.json`
5. Workflowet vil nu blive vist på lærredet
### Trin 3: Forstå workflowet

Det importerede workflow indeholder 9 forbundne noder:

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| Node | Formål |
|------|---------|
| **When clicking 'Execute workflow'** | Manuel trigger til at starte workflowet |
| **Fetch Financial News Webpage** | HTTP GET-anmodning til `https://apnews.com/business` |
| **Delay to Ensure Page Load** | Wait-node, der sikrer, at sideindholdet er fuldt indlæst |
| **Extract News Headlines & Text** | HTML-node, der udtrækker overskrifter, redaktørens udvalgte, hovedhistorier og regionale nyheder ved hjælp af CSS-selektorer |
| **Clean Extracted News Data** | Set-node, der samler alle udtrukne data i et enkelt tekstfelt |
| **AI Financial News Summarizer** | AI-agent, der behandler nyhederne med en systemprompt som finansanalytiker |
| **Lemonade Chat Model** | Forbinder til din lokale Lemonade-server, der kører LLM'en |
| **Structured Output Parser** | Formaterer AI-outputtet som struktureret JSON |
| **Convert to File** | Konverterer opsummeringen til en downloadbar fil |

### Trin 4: Konfigurer Lemonade-loginoplysninger

Før du kører workflowet, skal du forbinde det til din lokale Lemonade-server:

1. Dobbeltklik på noden **Lemonade Chat Model** i n8n
2. I dropdown-menuen **Credential to connect with** vælges **Create New Credential**
3. Indtast værdierne i tabellen nedenfor, og klik på gem.
4. Vælg den relevante model, som du har indlæst i Lemonade Server.

  | Felt | Værdi |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **Bemærk**: Før du tester, skal du køre `lemonade status` i en terminal for at bekræfte, at Lemonade-serveren kører.
<!-- @device:halo_box -->
> Dette workflow bruger GPT-OSS-120B, som er præinstalleret i Lemonade. Du kan ændre dette til andre indlæste modeller i indstillingerne for noden Lemonade Chat Model.
<!-- @device:end -->

### Trin 5: Test workflowet

1. Sørg for, at Lemonade kører med en indlæst model
2. Klik på **Execute workflow** nederst i midten af arbejdsfladen
3. Følg med, mens hver node udføres fra venstre mod højre—de bliver grønne, når de er færdige
4. Dobbeltklik på noden **AI Financial News Summarizer** for at se den genererede opsummering i den nederste rude.
5. Dobbeltklik på noden **Convert to File** for at downloade den tilsvarende tekstfil i den nederste rude.

## Forstå AI-agenten

AI Financial News Summarizer bruger en systemprompt designet til finansiel analyse:

```
You are an AI financial analyst. Your role is to read, understand, and
summarize key financial news from today. The goal is to provide investors
with a clear and concise market overview to support better investment decisions.

Investor Outlook
Today's news points to [bullish/bearish/neutral] sentiment. Watch for
[economic event/earnings report] tomorrow, which could influence market direction.
```

Agenten modtager de rensede nyhedsdata og udsender en struktureret opsummering med markedsstemning.

### Gem dit workflow

Klik på workflowets navn øverst, og omdøb det, hvis du ønsker det. Workflows gemmes automatisk, mens du arbejder.

## Næste skridt

- **Planlæg automatisering**: Erstat Manual Trigger med en **Schedule Trigger** for at køre dagligt
- **Send notifikationer**: Tilføj en **Discord**-, **Slack**- eller **Email**-node for at modtage opsummeringer
- **Prøv forskellige modeller**: Skift modellen i noden Lemonade Chat Model for at eksperimentere med forskellige LLM'er
- **Tilpas udtræk**: Rediger CSS-selektorerne i HTML Extract-noden for at målrette mod forskellige nyhedssektioner
- **Prøv forskellige backends**: n8n understøtter også [Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model), LM Studio og andre lokale LLM-backends

### Udforsk n8n-skabeloner

n8n har hundredvis af færdiglavede workflow-skabeloner. Gennemse det officielle skabelonbibliotek på:

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

Søg efter "AI", "LLM" eller "automation" for at finde workflows, du kan importere og tilpasse.

For mere information kan du læse [n8n-dokumentationen](https://docs.n8n.io/).