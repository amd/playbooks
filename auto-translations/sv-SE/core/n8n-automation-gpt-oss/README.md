<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinöversättning.** Den här sidan har automatiskt översatts från engelska och har inte granskats av en människa. Den kan innehålla fel, och vissa instruktioner, kommandon, nedladdningar, produkttillgänglighet eller annat innehåll kan variera beroende på språk eller region. Vid eventuella motsägelser eller avvikelser är det den ursprungliga engelska versionen av playbook som gäller och har företräde.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Översikt

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Denna spelbok kräver minst **32 GB** systemminne.
<!-- @device:end -->

n8n är en plattform för arbetsflödesautomatisering som låter dig koppla samman appar och tjänster med hjälp av en visuell, nodbaserad editor.

Den här spelboken visar hur du konfigurerar en AI-driven finansnyhetssammanfattare som skrapar AP News affärsdel, extraherar viktiga rubriker och använder en lokal LLM som körs på ditt system för att generera en investerarfokuserad sammanfattning.

## Vad du kommer att lära dig

- Hur du installerar och startar n8n
- Att importera och konfigurera ett färdigbyggt arbetsflöde
- Att ansluta till Lemonade med den inbyggda n8n-integrationen
- Att förstå arbetsflödesnoder och dataflöde

## Vad är Lemonade?

[Lemonade](https://lemonade-server.ai) är en plattform för lokal LLM-servering byggd för AMD-hårdvara. Den tillhandahåller ett OpenAI-kompatibelt API som körs helt på din maskin – din data lämnar aldrig din enhet.

I den här spelboken använder vi Lemonade för att servera en lokal LLM som n8n ansluter till för AI-drivna uppgifter.

n8n har en **inbyggd Lemonade-nod** (`Lemonade Chat Model`) som ger en förstklassig integration – ingen manuell konfiguration behövs. Detta gör det enkelt att ansluta din lokala LLM till automationsarbetsflöden.

## Ange minneskonfigurationen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrollera om det finns programuppdateringar

<!-- @require:software-update -->
<!-- @device:end -->

## Installera nödvändig programvara
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
> **Tips**: Windows-användare kan behöva ändra sin PowerShell-körningsprincip (t.ex.
> ställa in den till RemoteSigned eller Unrestricted) innan vissa PowerShell-kommandon körs.
<!-- @os:end -->


<!-- @os:windows -->
> **PATH-problem**: Om `n8n --version` säger att kommandot inte hittas, se till att din npm-globala bin-katalog finns i användarens `PATH`. Den vanliga installationssökvägen är `C:\Users\<username>\AppData\Roaming\npm`.
> Lägg till denna i användarens sökväg (Redigera systemets miljövariabler > Miljövariabler > Redigera användarens sökväg) och ladda om terminalen.

<!-- @os:end -->

<!-- @os:linux -->
Vi kommer nu att använda Podman-tjänsten för att containerisera vår n8n-installation.

Ladda ner följande till en katalog du väljer: [compose.yml](assets/compose.yml)

Kör följande kommando i den katalogen:
```bash
podman compose up -d
```

Detta bör installera n8n och skriva till en beständig lagring.

Starta n8n genom att skriva `localhost:5678` i din webbläsares adressfält.
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
n8n startar en lokal webbserver. Tryck på `'o'` eller öppna din webbläsare till `http://localhost:5678` för att komma åt editorn.
<!-- @os:end -->


> **Tips**: Håll terminalfönstret öppet medan du använder n8n. Om du stänger det kan servern stoppas.

## Starta Lemonade

Lemonade är den lokala servern som kör en modell och ansluter till n8n.

<!-- @os:linux -->
Öppna Lemonade-gränssnittet genom att klicka på Lemonade-ikonen i aktivitetsfältet. Härifrån kan du bläddra bland modeller, backends och läsa in de förinstallerade modellerna.
<!-- @os:end -->

<!-- @os:windows -->
Öppna Lemonade-gränssnittet genom att klicka på Lemonade-ikonen. Högerklicka på ikonen i systemfältet för att öppna appen. Sedan kan du lägga till modeller, backends och läsa in de förinstallerade modellerna.
<!-- @os:end -->

>**Tips**: När det körs är Lemonade-gränssnittet också tillgängligt på http://localhost:13305

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

> **Tips**: Om du blir utelåst från ditt konto, prova `n8n user-management:reset`

### Steg 2: Importera arbetsflödet

Vi har tillhandahållit ett färdigbyggt arbetsflöde som du kan importera direkt:

1. Ladda ner följande arbetsflödesfil: [financial-news-workflow.json](assets/financial-news-workflow.json)
2. Klicka på **Start from Scratch** för att öppna arbetsflödeseditorn. Alternativt kan du klicka på +-knappen längst upp till vänster och sedan på **Add workflow**.
3. Klicka på **...**-menyn (tre punkter) i det övre högra hörnet och välj **Import from file**
4. Välj den nedladdade filen `financial-news-workflow.json`
5. Arbetsflödet visas på arbetsytan
### Steg 3: Förstå arbetsflödet

Det importerade arbetsflödet innehåller 9 sammankopplade noder:

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| Nod | Syfte |
|------|---------|
| **When clicking 'Execute workflow'** | Manuell utlösare för att starta arbetsflödet |
| **Fetch Financial News Webpage** | HTTP GET-förfrågan till `https://apnews.com/business` |
| **Delay to Ensure Page Load** | Wait-nod som säkerställer att sidinnehållet har laddats klart |
| **Extract News Headlines & Text** | HTML-nod som extraherar rubriker, redaktionens urval, huvudnyheter och regionala nyheter med hjälp av CSS-selektorer |
| **Clean Extracted News Data** | Set-nod som kombinerar all extraherad data till ett enda textfält |
| **AI Financial News Summarizer** | AI-agent som bearbetar nyheterna med en systemprompt för finansanalytiker |
| **Lemonade Chat Model** | Ansluter till din lokala Lemonade-server som kör LLM:en |
| **Structured Output Parser** | Formaterar AI-utdata som strukturerad JSON |
| **Convert to File** | Konverterar sammanfattningen till en nedladdningsbar fil |

### Steg 4: Konfigurera Lemonade-autentiseringsuppgifter

Innan du kör arbetsflödet behöver du ansluta det till din lokala Lemonade-server:

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
> Detta arbetsflöde använder GPT-OSS-120B och den är förinstallerad i Lemonade. Du kan ändra detta till andra laddade modeller i inställningarna för Lemonade Chat Model-noden.
<!-- @device:end -->

### Steg 5: Testa arbetsflödet

1. Se till att Lemonade körs med en modell laddad
2. Klicka på **Execute workflow** längst ned i mitten av arbetsytan
3. Följ hur varje nod körs från vänster till höger – de blir gröna när de är klara
4. Dubbelklicka på noden **AI Financial News Summarizer** för att se den genererade sammanfattningen i panelen längst ned.
5. Dubbelklicka på noden **Convert to File** för att ladda ned motsvarande textfil i panelen längst ned.

## Förstå AI-agenten

AI Financial News Summarizer använder en systemprompt utformad för finansanalys:

```
You are an AI financial analyst. Your role is to read, understand, and
summarize key financial news from today. The goal is to provide investors
with a clear and concise market overview to support better investment decisions.

Investor Outlook
Today's news points to [bullish/bearish/neutral] sentiment. Watch for
[economic event/earnings report] tomorrow, which could influence market direction.
```

Agenten tar emot den rensade nyhetsdatan och genererar en strukturerad sammanfattning med marknadssentiment.

### Spara ditt arbetsflöde

Klicka på arbetsflödets namn längst upp och byt namn om du vill. Arbetsflöden sparas automatiskt medan du arbetar.

## Nästa steg

- **Schemalägg automatisering**: Ersätt Manual Trigger med en **Schedule Trigger** för att köra dagligen
- **Skicka aviseringar**: Lägg till en **Discord**-, **Slack**- eller **Email**-nod för att ta emot sammanfattningar
- **Prova olika modeller**: Ändra modellen i Lemonade Chat Model-noden för att experimentera med olika LLM:er
- **Anpassa extrahering**: Ändra CSS-selektorerna i HTML Extract-noden för att rikta in dig på olika nyhetsavsnitt
- **Prova olika backends**: n8n stöder även [Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model), LM Studio och andra lokala LLM-backends

### Utforska n8n-mallar

n8n har hundratals färdiga arbetsflödesmallar. Bläddra i det officiella mallbiblioteket på:

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

Sök efter "AI", "LLM" eller "automation" för att hitta arbetsflöden du kan importera och anpassa.

För mer information, se [n8n-dokumentationen](https://docs.n8n.io/).

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