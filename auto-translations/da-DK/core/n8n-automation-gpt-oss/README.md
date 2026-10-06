<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinoversættelse.** Denne side er automatisk oversat fra engelsk og er ikke blevet gennemgået af et menneske. Den kan indeholde fejl, og visse instruktioner, kommandoer, downloads, produkttilgængelighed eller andet indhold kan variere afhængigt af sprog eller region. I tilfælde af uoverensstemmelse eller afvigelse er den oprindelige engelske version af playbook'en gældende og har forrang.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->
## Oversigt
<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Denne playbook kræver minimum **32GB** systemhukommelse.
<!-- @device:end -->
n8n er en workflow-automatiseringsplatform, der lader dig forbinde apps og tjenester ved hjælp af en visuel, nodebaseret editor.

Denne playbook lærer dig, hvordan du sætter en AI-drevet finansnyheds-opsummerer op, som henter de seneste erhvervsoverskrifter fra et RSS-feed med nyheder og bruger en lokal LLM, der kører på dit system, til at generere et investorfokuseret resumé.

## Hvad du vil lære

- Hvordan du installerer og starter n8n
- Import og konfiguration af et foruddefineret workflow
- Oprettelse af forbindelse til Lemonade ved hjælp af den native n8n-integration
- Forståelse af workflow-noder og dataflow

## Hvad er Lemonade?

[Lemonade](https://lemonade-server.ai) er en lokal LLM-serveringsplatform bygget til AMD-hardware. Den tilbyder et OpenAI-kompatibelt API, der kører udelukkende på din maskine - dine data forlader aldrig din enhed.

I denne playbook bruger vi Lemonade til at servere en lokal LLM, som n8n forbinder til for AI-drevne opgaver.

n8n inkluderer en **native Lemonade-node** (`Lemonade Chat Model`), der tilbyder en førsteklasses integration - ingen grund til manuel konfiguration. Dette gør det enkelt at forbinde din lokale LLM til automatiseringsworkflows.
<!-- @device:halo_box,halo,stx,krk -->
## Indstilling af hukommelseskonfiguration
<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Søg efter softwareopdateringer
<!-- @require:software-update -->
<!-- @device:end -->
## Installation af softwareforudsætninger
<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @prereq:n8n -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- Linux runs n8n as a Podman container (see compose.yml below), so Node.js and a host n8n install are not required; podman is the only extra prerequisite. -->
<!-- @require:lemonade,podman -->
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
## Installation af n8n
<!-- @os:windows -->
Installer n8n globalt ved hjælp af npm.

> **Bemærk**: Du kan muligvis se nogle npm-advarsler. Dette er forventet.

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
> **Tip**: Windows-brugere skal muligvis ændre deres PowerShell Execution Policy (f.eks.
> ved at sætte den til RemoteSigned eller Unrestricted), før de kører visse Powershell-kommandoer.
<!-- @os:end -->


<!-- @os:windows -->
> **PATH-problem**: Hvis `n8n --version` siger, at kommandoen ikke blev fundet, skal du sikre dig, at din globale npm-bin-mappe findes i bruger-`PATH`. Den sædvanlige installationssti er `C:\Users\<username>\AppData\Roaming\npm`. 
> Tilføj dette til brugerstien (Rediger systemets miljøvariabler > Miljøvariabler > Rediger brugersti) og genindlæs terminalen.
<!-- @os:end -->

<!-- @os:linux -->
Vi skal nu bruge Podman-tjenesten til at containerisere vores n8n-installation.

Download følgende til en mappe efter eget valg: [compose.yml](assets/compose.yml)

I den mappe skal du køre følgende kommando:
```bash
podman compose up -d
```

Dette bør installere n8n og skrive til en vedvarende lagring.

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
n8n starter en lokal webserver. Tryk på `'o'`, eller åbn din browser og gå til `http://localhost:5678` for at få adgang til editoren.
<!-- @os:end -->
> **Tip**: Hold terminalvinduet åbent, mens du bruger n8n. Hvis du lukker det, kan det stoppe serveren.

## Start af Lemonade

Lemonade er den lokale server, der vil køre en model og oprette forbindelse til n8n.
<!-- @os:linux -->
Åbn Lemonade GUI'en ved at klikke på Lemonade-ikonet i proceslinjen. Her kan du gennemse modeller, backends og indlæse de forudinstallerede modeller.
<!-- @os:end -->

<!-- @os:windows -->
Åbn Lemonade GUI'en ved at klikke på Lemonade-ikonet. Højreklik på ikonet i proceslinjen for at åbne appen. Derefter kan du tilføje modeller, backends og indlæse de forudinstallerede modeller.
<!-- @os:end -->
>**Tip**: Når Lemonade GUI'en kører, kan den også tilgås på http://localhost:13305

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

### Trin 1: Opret konto eller log ind i n8n

Når du åbner n8n for første gang, bliver du bedt om at oprette en konto eller logge ind:

1. Åbn `http://localhost:5678` i din browser
2. Opret en ny lokal konto med din e-mail, eller log ind, hvis du allerede har en
3. Når du er logget ind, vil du se n8n-dashboardet

> **Tip**: Hvis du bliver låst ude af din konto, kan du prøve `n8n user-management:reset`

### Trin 2: Importér workflowet

Vi har stillet et færdigbygget workflow til rådighed, som du kan importere direkte:

1. Download følgende workflow-fil: [financial-news-workflow.json](assets/financial-news-workflow.json)
2. Klik på **Start from Scratch** for at åbne workflow-editoren. Alternativt kan du klikke på +-knappen øverst til venstre og derefter vælge **Add workflow**.
3. Klik på **...**-menuen (tre prikker) i den øverste højre bjælke, og vælg **Import from file**
4. Vælg den downloadede fil `financial-news-workflow.json`
5. Workflowet vises nu på lærredet
### Trin 3: Forstå workflowet

Det importerede workflow indeholder 8 forbundne noder:

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| Node | Formål |
|------|---------|
| **When clicking 'Execute workflow'** | Manuel trigger til at starte workflowet |
| **Fetch Financial News Feed** | RSS Read-node, der henter de seneste erhvervsoverskrifter fra et RSS-feed (bruger som standard NYT Business-feedet, ingen API-nøgle påkrævet) |
| **Aggregate Headlines** | Aggregate-node, der samler overskrifter og resuméer fra hvert feed-element i én samlet liste |
| **Clean Extracted News Data** | Set-node, der kombinerer alle overskrifterne i ét samlet tekstfelt |
| **AI Financial News Summarizer** | AI Agent, der behandler nyhederne med en systemprompt til finansanalyse |
| **Lemonade Chat Model** | Forbinder til din lokale Lemonade-server, der kører LLM'en |
| **Structured Output Parser** | Formaterer AI-outputtet som struktureret JSON |
| **Convert to File** | Konverterer resuméet til en fil, der kan downloades |

> **Tip**: For at bruge en anden nyhedskilde skal du dobbeltklikke på noden **Fetch Financial News Feed** og erstatte URL'en med et hvilket som helst erhvervs- eller markeds-RSS-feed efter eget valg.

### Trin 4: Konfigurer Lemonade-legitimationsoplysninger

Før du kører workflowet, skal du forbinde det til din lokale Lemonade-server:

1. Dobbeltklik på noden **Lemonade Chat Model** i n8n
2. I rullemenuen **Credential to connect with** vælges **Create New Credential**
3. Indtast værdierne i tabellen nedenfor, og klik på gem.
4. Vælg den relevante model, du har indlæst i Lemonade Server.

  | Felt | Værdi |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **Bemærk**: Før du tester, skal du køre `lemonade status` i en terminal for at bekræfte, at Lemonade-serveren kører.
<!-- @device:halo_box -->
> Dette workflow bruger GPT-OSS-120B, og den er forudinstalleret i Lemonade. Du kan ændre dette til andre indlæste modeller i indstillingerne for Lemonade Chat Model-noden.
<!-- @device:end -->

### Trin 5: Test workflowet

1. Sørg for, at Lemonade kører med en indlæst model
2. Klik på **Execute workflow** nederst i midten af arbejdsfladen
3. Følg med, mens hver node udføres fra venstre mod højre—de bliver grønne, når de er færdige
4. Dobbeltklik på noden **AI Financial News Summarizer** for at se det genererede resumé i det nederste panel.
5. Dobbeltklik på noden **Convert to File** for at downloade den tilsvarende tekstfil i det nederste panel.

## Forstå AI Agent'en

AI Financial News Summarizer bruger en systemprompt designet til finansanalyse:

```
You are an AI financial analyst. Your role is to read, understand, and
summarize key financial news from today. The goal is to provide investors
with a clear and concise market overview to support better investment decisions.

Investor Outlook
Today's news points to [bullish/bearish/neutral] sentiment. Watch for
[economic event/earnings report] tomorrow, which could influence market direction.
```

Agenten modtager de rensede nyhedsdata og udsender et struktureret resumé med markedsstemning.

### Gem dit workflow

Klik på workflowets navn øverst, og omdøb det, hvis du ønsker det. Workflows gemmes automatisk, mens du arbejder.

## Næste skridt

- **Planlæg automatisering**: Erstat Manual Trigger med en **Schedule Trigger** for at køre dagligt
- **Send notifikationer**: Tilføj en **Discord**-, **Slack**- eller **Email**-node for at modtage resuméer
- **Prøv forskellige modeller**: Skift modellen i Lemonade Chat Model-noden for at eksperimentere med forskellige LLM'er
- **Skift nyhedskilde**: Lad noden **Fetch Financial News Feed** pege på et andet RSS-feed for at følge andre sektioner eller publikationer
- **Prøv forskellige backends**: n8n understøtter også [Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model), LM Studio og andre lokale LLM-backends

### Udforsk n8n-skabeloner

n8n har hundredvis af færdiglavede workflow-skabeloner. Gennemse det officielle skabelonbibliotek på:

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

Søg efter "AI", "LLM" eller "automation" for at finde workflows, du kan importere og tilpasse.

For yderligere information, se [n8n Documentation](https://docs.n8n.io/).

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