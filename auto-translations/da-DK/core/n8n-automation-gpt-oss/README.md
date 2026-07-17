<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Oversigt

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> This playbook requires a minimum of **32GB** of system memory.
<!-- @device:end -->

n8n er en platform til workflowautomatisering, der lader dig forbinde apps og tjenester ved hjælp af en visuel nodebaseret editor.

Dette playbook lærer dig, hvordan du opsætter en AI-drevet finansiel nyhedsopsummerer, der henter data fra AP News' erhvervssektion, udtrækker vigtige overskrifter og bruger en lokal LLM, der kører på dit system, til at generere et investorfokuseret resumé.

## Hvad du vil lære

- Sådan installerer og starter du n8n
- Import og konfiguration af et færdigbygget workflow
- Forbindelse til Lemonade ved hjælp af den native n8n-integration
- Forståelse af workflownoder og dataflow

## Hvad er Lemonade?

[Lemonade](https://lemonade-server.ai) er en lokal LLM-serveringsplatform bygget til AMD-hardware. Den leverer en OpenAI-kompatibel API, der kører udelukkende på din maskine – dine data forlader aldrig din enhed.

I dette playbook bruger vi Lemonade til at serve en lokal LLM, som n8n forbinder til for AI-drevne opgaver.

n8n inkluderer en **native Lemonade-node** (`Lemonade Chat Model`), der giver en førsteklasses integration – ingen manuel konfiguration er nødvendig. Dette gør det ligetil at forbinde din lokale LLM til automatiseringsworkflows.

## Indstilling af hukommelseskonfigurationen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontroller for softwareopdateringer

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
> **Tip**: Windows-brugere skal muligvis ændre deres PowerShell-udførelsespolitik (f.eks.
> indstille den til RemoteSigned eller Unrestricted) inden de kører nogle Powershell-kommandoer.
<!-- @os:end -->


<!-- @os:windows -->
> **PATH-problem**: Hvis `n8n --version` siger kommando ikke fundet, skal du sikre, at din npm globale bin-mappe er på brugerens `PATH`. Den sædvanlige installationssti er `C:\Users\<username>\AppData\Roaming\npm`. 
> Tilføj dette til brugerstien (Rediger systemets miljøvariabler > Miljøvariabler > Rediger brugersti) og genindlæs terminalen.

<!-- @os:end -->

<!-- @os:linux -->
Vi vil nu bruge Podman-tjenesten til at containerisere vores n8n-installation.

Download venligst følgende til en mappe efter eget valg: [compose.yml](assets/compose.yml)

I den mappe skal du køre følgende kommando:
```bash
podman compose up -d
```

Dette bør installere n8n og skrive til et vedvarende lager.

Start n8n ved at skrive `localhost:5678` i din browsers adresselinje.
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


> **Tip**: Hold terminalvinduet åbent, mens du bruger n8n. Lukning af det kan stoppe serveren.

## Start af Lemonade

Lemonade er den lokale server, der kører en model og forbinder til n8n.

<!-- @os:linux -->
Åbn Lemonade GUI ved at klikke på Lemonade-ikonet i proceslinjen. Du kan gennemse modeller, backends og indlæse de forudinstallerede modeller herfra.
<!-- @os:end -->

<!-- @os:windows -->
Åbn Lemonade GUI ved at klikke på Lemonade-ikonet. Højreklik på bakke-ikonet for at åbne appen. Derefter kan du tilføje modeller, backends og indlæse de forudinstallerede modeller.
<!-- @os:end -->

>**Tip**: Når den kører, er Lemonade GUI også tilgængelig på http://localhost:13305

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

### Trin 1: Opret en konto eller log ind på n8n

Når du første gang åbner n8n, bliver du bedt om at oprette en konto eller logge ind:

1. Åbn `http://localhost:5678` i din browser
2. Opret en ny lokal konto med din e-mail, eller log ind, hvis du allerede har en
3. Når du er logget ind, ser du n8n-dashboardet

> **Tip**: Hvis du er låst ude af din konto, prøv `n8n user-management:reset`

### Trin 2: Importer workflowet

Vi har leveret et færdigbygget workflow, som du kan importere direkte:

1. Download følgende workflowfil: [financial-news-workflow.json](assets/financial-news-workflow.json)
2. Klik på **Start from Scratch** for at åbne workfloweditoren. Alternativt kan du klikke på +-knappen øverst til venstre og derefter **Add workflow**.
3. Klik på **...**-menuen (tre prikker) i den øverste højre bjælke og vælg **Import from file**
4. Vælg den downloadede `financial-news-workflow.json`-fil
5. Workflowet vises på lærredet


### Trin 3: Forståelse af workflowet

Det importerede workflow indeholder 9 forbundne noder:

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| Node | Formål |
|------|---------|
| **When clicking 'Execute workflow'** | Manuel udløser til at starte workflowet |
| **Fetch Financial News Webpage** | HTTP GET-anmodning til `https://apnews.com/business` |
| **Delay to Ensure Page Load** | Ventenode for at sikre, at sideindholdet er fuldt indlæst |
| **Extract News Headlines & Text** | HTML-node, der udtrækker overskrifter, redaktørens valg, tophistorier og regionale nyheder ved hjælp af CSS-selektorer |
| **Clean Extracted News Data** | Set-node, der kombinerer alle udtrukne data til ét tekstfelt |
| **AI Financial News Summarizer** | AI-agent, der behandler nyhederne med en systemprompt til finansanalytiker |
| **Lemonade Chat Model** | Forbinder til din lokale Lemonade-server, der kører LLM'en |
| **Structured Output Parser** | Formaterer AI-outputtet som struktureret JSON |
| **Convert to File** | Konverterer resuméet til en fil, der kan downloades |

### Trin 4: Konfigurer Lemonade-legitimationsoplysninger

Inden du kører workflowet, skal du forbinde det til din lokale Lemonade-server:

1. Dobbeltklik på **Lemonade Chat Model**-noden i n8n
2. I rullemenuen **Credential to connect with** vælg **Create New Credential**
3. Indtast værdierne i tabellen nedenfor og klik gem.
4. Vælg den relevante model, du har indlæst i Lemonade Server.

  | Felt | Værdi |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **Bemærk**: Inden du tester, kør `lemonade status` i en terminal for at bekræfte, at Lemonade-serveren kører.
<!-- @device:halo_box -->
> Dette workflow bruger GPT-OSS-120B, og det er forudinstalleret i Lemonade. Du kan ændre dette til andre indlæste modeller i indstillingerne for Lemonade Chat Model-noden.
<!-- @device:end -->

### Trin 5: Test workflowet

1. Sørg for, at Lemonade kører med en model indlæst
2. Klik på **Execute workflow** nederst i midten af lærredet
3. Se hver node udføre fra venstre mod højre – de bliver grønne, når de er færdige
4. Dobbeltklik på **AI Financial News Summarizer**-noden for at se det genererede resumé i den nederste rude.
5. Dobbeltklik på **Convert to File**-noden for at downloade den tilsvarende tekstfil i den nederste rude.

## Forståelse af AI-agenten

AI Financial News Summarizer bruger en systemprompt designet til finansiel analyse:

```
You are an AI financial analyst. Your role is to read, understand, and
summarize key financial news from today. The goal is to provide investors
with a clear and concise market overview to support better investment decisions.

Investor Outlook
Today's news points to [bullish/bearish/neutral] sentiment. Watch for
[economic event/earnings report] tomorrow, which could influence market direction.
```

Agenten modtager de rensede nyhedsdata og udsender et struktureret resumé med markedssentiment.

### Gem dit workflow

Klik på workflownavnet øverst og omdøb det, hvis du ønsker det. Workflows gemmes automatisk, mens du arbejder.

## Næste skridt

- **Planlæg automatisering**: Erstat Manuel Trigger med en **Schedule Trigger** for at køre dagligt
- **Send notifikationer**: Tilføj en **Discord**-, **Slack**- eller **Email**-node for at modtage resuméer
- **Prøv forskellige modeller**: Skift modellen i Lemonade Chat Model-noden for at eksperimentere med forskellige LLM'er
- **Tilpas udtrækning**: Modificer HTML Extract-nodens CSS-selektorer for at målrette mod forskellige nyhedssektioner
- **Prøv forskellige backends**: n8n understøtter også [Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model), LM Studio og andre lokale LLM-backends

### Udforsk n8n-skabeloner

n8n har hundredvis af færdigbyggede workflowskabeloner. Gennemse det officielle skabelonbibliotek på:

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

Søg efter "AI", "LLM" eller "automation" for at finde workflows, du kan importere og tilpasse.

For mere information, se [n8n-dokumentationen](https://docs.n8n.io/).