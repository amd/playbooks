<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Översikt

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> This playbook requires a minimum of **32GB** of system memory.
<!-- @device:end -->

n8n är en plattform för arbetsflödesautomatisering som låter dig ansluta appar och tjänster med hjälp av en visuell nodbaserad editor.

Den här playbooken lär dig hur du konfigurerar en AI-driven sammanfattare av finansiella nyheter som hämtar data från AP News affärssektion, extraherar viktiga rubriker och använder en lokal LLM som körs på ditt system för att generera en investerarfokuserad sammanfattning.

## Vad du kommer att lära dig

- Hur du installerar och startar n8n
- Importera och konfigurera ett färdigt arbetsflöde
- Ansluta till Lemonade med den inbyggda n8n-integrationen
- Förstå arbetsflödesnoder och dataflöde

## Vad är Lemonade?

[Lemonade](https://lemonade-server.ai) är en lokal LLM-serveringsplattform byggd för AMD-hårdvara. Den tillhandahåller ett OpenAI-kompatibelt API som körs helt på din maskin – dina data lämnar aldrig din enhet.

I den här playbooken använder vi Lemonade för att köra en lokal LLM som n8n ansluter till för AI-drivna uppgifter.

n8n inkluderar en **inbyggd Lemonade-nod** (`Lemonade Chat Model`) som ger en förstklassig integration – ingen manuell konfiguration behövs. Detta gör det enkelt att ansluta din lokala LLM till automatiseringsarbetsflöden.

## Ange minneskonfigurationen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrollera efter programvaruuppdateringar

<!-- @require:software-update -->
<!-- @device:end -->

## Installera programvarukrav
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

## Installera n8n
<!-- @os:windows -->
Installera n8n globalt med npm.

> **Obs**: Du kan se vissa npm-varningar. Detta är förväntat.

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
> **Tips**: Windows-användare kan behöva ändra sin PowerShell-exekveringspolicy (t.ex.
> ställa in den till RemoteSigned eller Unrestricted) innan de kör vissa Powershell-kommandon.
<!-- @os:end -->


<!-- @os:windows -->
> **PATH-problem**: Om `n8n --version` säger att kommandot inte hittades, se till att npm:s globala bin-katalog finns i användarens `PATH`. Den vanliga installationssökvägen är `C:\Users\<username>\AppData\Roaming\npm`. 
> Lägg till detta i användarsökvägen (Redigera systemmiljövariabler > Miljövariabler > Redigera användarsökväg) och ladda om terminalen.

<!-- @os:end -->

<!-- @os:linux -->
Vi ska nu använda Podman-tjänsten för att containerisera vår n8n-installation.

Ladda ned följande till en valfri katalog: [compose.yml](assets/compose.yml)

Kör följande kommando i den katalogen:
```bash
podman compose up -d
```

Detta bör installera n8n och skriva till ett beständigt lagringsutrymme.

Starta n8n genom att skriva `localhost:5678` i webbläsarens adressfält.
<!-- @os:end -->

<!-- @os:windows -->
## Starta n8n

Starta n8n från terminalen:

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
n8n startar en lokal webbserver. Tryck på `'o'` eller öppna din webbläsare på `http://localhost:5678` för att komma åt editorn.
<!-- @os:end -->


> **Tips**: Håll terminalfönstret öppet medan du använder n8n. Att stänga det kan stoppa servern.

## Starta Lemonade

Lemonade är den lokala servern som kör en modell och ansluter till n8n.

<!-- @os:linux -->
Öppna Lemonade GUI genom att klicka på Lemonade-ikonen i aktivitetsfältet. Du kan bläddra bland modeller, backends och ladda de förinstallerade modellerna härifrån.
<!-- @os:end -->

<!-- @os:windows -->
Öppna Lemonade GUI genom att klicka på Lemonade-ikonen. Högerklicka på ikonen i systemfältet för att öppna appen. Sedan kan du lägga till modeller, backends och ladda de förinstallerade modellerna.
<!-- @os:end -->

>**Tips**: När den väl körs är Lemonade GUI också tillgängligt på http://localhost:13305

Alternativt kan du öppna en terminal och köra `lemonade list` för att se vilka modeller som är installerade. Kör sedan:

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


## Konfigurera arbetsflödet

### Steg 1: Registrera dig eller logga in på n8n

När du öppnar n8n för första gången uppmanas du att skapa ett konto eller logga in:

1. Öppna `http://localhost:5678` i din webbläsare
2. Skapa ett nytt lokalt konto med din e-postadress, eller logga in om du redan har ett
3. När du är inloggad ser du n8n-instrumentpanelen

> **Tips**: Om du är utelåst från ditt konto, prova `n8n user-management:reset`

### Steg 2: Importera arbetsflödet

Vi har tillhandahållit ett färdigt arbetsflöde som du kan importera direkt:

1. Ladda ned följande arbetsflödesfil: [financial-news-workflow.json](assets/financial-news-workflow.json)
2. Klicka på **Start from Scratch** för att öppna arbetsflödesredigeraren. Alternativt, klicka på +-knappen längst upp till vänster och sedan **Add workflow**.
3. Klicka på **...**-menyn (tre punkter) i det övre högra fältet och välj **Import from file**
4. Välj den nedladdade filen `financial-news-workflow.json`
5. Arbetsflödet visas på arbetsytan


### Steg 3: Förstå arbetsflödet

Det importerade arbetsflödet innehåller 9 anslutna noder:

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| Nod | Syfte |
|------|---------|
| **When clicking 'Execute workflow'** | Manuell utlösare för att starta arbetsflödet |
| **Fetch Financial News Webpage** | HTTP GET-förfrågan till `https://apnews.com/business` |
| **Delay to Ensure Page Load** | Väntnod för att säkerställa att sidans innehåll är fullständigt laddat |
| **Extract News Headlines & Text** | HTML-nod som extraherar rubriker, redaktörens val, toppnyheter och regionala nyheter med CSS-selektorer |
| **Clean Extracted News Data** | Set-nod som kombinerar all extraherad data till ett enda textfält |
| **AI Financial News Summarizer** | AI-agent som bearbetar nyheterna med en systemprompt för finansanalytiker |
| **Lemonade Chat Model** | Ansluter till din lokala Lemonade-server som kör LLM |
| **Structured Output Parser** | Formaterar AI-utdata som strukturerad JSON |
| **Convert to File** | Konverterar sammanfattningen till en nedladdningsbar fil |

### Steg 4: Konfigurera Lemonade-autentiseringsuppgifter

Innan du kör arbetsflödet måste du ansluta det till din lokala Lemonade-server:

1. Dubbelklicka på noden **Lemonade Chat Model** i n8n
2. I rullgardinsmenyn **Credential to connect with** väljer du **Create New Credential**
3. Ange värdena i tabellen nedan och klicka på spara.
4. Välj den relevanta modell som du har laddat i Lemonade Server.

  | Fält | Värde |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **Obs**: Innan du testar, kör `lemonade status` i en terminal för att bekräfta att Lemonade-servern körs.
<!-- @device:halo_box -->
> Det här arbetsflödet använder GPT-OSS-120B och det är förinstallerat i Lemonade. Du kan ändra detta till andra laddade modeller i inställningarna för noden Lemonade Chat Model.
<!-- @device:end -->

### Steg 5: Testa arbetsflödet

1. Se till att Lemonade körs med en modell laddad
2. Klicka på **Execute workflow** längst ned i mitten av arbetsytan
3. Se varje nod köras från vänster till höger – de blir gröna när de är klara
4. Dubbelklicka på noden **AI Financial News Summarizer** för att se den genererade sammanfattningen i det nedre fönstret.
5. Dubbelklicka på noden **Convert to File** för att ladda ned motsvarande textfil i det nedre fönstret.

## Förstå AI-agenten

AI Financial News Summarizer använder en systemprompt utformad för finansiell analys:

```
You are an AI financial analyst. Your role is to read, understand, and
summarize key financial news from today. The goal is to provide investors
with a clear and concise market overview to support better investment decisions.

Investor Outlook
Today's news points to [bullish/bearish/neutral] sentiment. Watch for
[economic event/earnings report] tomorrow, which could influence market direction.
```

Agenten tar emot den rensade nyhetsdatan och producerar en strukturerad sammanfattning med marknadssentiment.

### Spara ditt arbetsflöde

Klicka på arbetsflödets namn längst upp och byt namn om du vill. Arbetsflöden sparas automatiskt medan du arbetar.

## Nästa steg

- **Schemalägg automatisering**: Ersätt den manuella utlösaren med en **Schedule Trigger** för att köra dagligen
- **Skicka aviseringar**: Lägg till en **Discord**-, **Slack**- eller **Email**-nod för att ta emot sammanfattningar
- **Prova olika modeller**: Ändra modellen i noden Lemonade Chat Model för att experimentera med olika LLM:er
- **Anpassa extraktion**: Ändra HTML Extract-nodens CSS-selektorer för att rikta in sig på olika nyhetsavsnitt
- **Prova olika backends**: n8n stöder också [Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model), LM Studio och andra lokala LLM-backends

### Utforska n8n-mallar

n8n har hundratals färdiga arbetsflödesmallar. Bläddra i det officiella mallbiblioteket på:

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

Sök efter "AI", "LLM" eller "automation" för att hitta arbetsflöden som du kan importera och anpassa.

För mer information, se [n8n-dokumentationen](https://docs.n8n.io/).