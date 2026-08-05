<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinoversettelse.** Denne siden ble automatisk oversatt fra engelsk og har ikke blitt gjennomgått av et menneske. Den kan inneholde feil, og enkelte instruksjoner, kommandoer, nedlastinger, produkttilgjengelighet eller annet innhold kan variere etter språk eller region. Ved eventuelle uoverensstemmelser eller avvik er den opprinnelige engelske versjonen av playbook-en gjeldende.
<!-- auto-translated-disclaimer:end -->

# n8n Finansnyheter-arbeidsflyt med Lemonade

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Oversikt

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Denne oppskriften krever minst **32 GB** systemminne.
<!-- @device:end -->

n8n er en plattform for arbeidsflytautomatisering som lar deg koble sammen apper og tjenester ved hjelp av en visuell, nodebasert editor.

Denne oppskriften lærer deg hvordan du setter opp en AI-drevet oppsummerer for finansnyheter som skraper businessdelen av AP News, trekker ut viktige overskrifter, og bruker en lokal LLM som kjører på systemet ditt for å generere et investorfokusert sammendrag.

## Hva du vil lære

- Hvordan installere og starte n8n
- Importere og konfigurere en ferdiglaget arbeidsflyt
- Koble til Lemonade ved hjelp av den innebygde n8n-integrasjonen
- Forstå arbeidsflytnoder og dataflyt

## Hva er Lemonade?

[Lemonade](https://lemonade-server.ai) er en plattform for lokal LLM-servering bygget for AMD-maskinvare. Den tilbyr et OpenAI-kompatibelt API som kjører helt lokalt på maskinen din — dataene dine forlater aldri enheten din.

I denne oppskriften bruker vi Lemonade til å tilby en lokal LLM som n8n kobler til for AI-drevne oppgaver.

n8n har en **innebygd Lemonade-node** (`Lemonade Chat Model`) som tilbyr en førsteklasses integrasjon - ingen behov for manuell konfigurasjon. Dette gjør det enkelt å koble den lokale LLM-en din til automatiseringsarbeidsflyter.

## Konfigurere minneinnstillinger

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Sjekk etter programvareoppdateringer

<!-- @require:software-update -->
<!-- @device:end -->

## Installere programvareforutsetninger
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

## Installere n8n
<!-- @os:windows -->
Installer n8n globalt ved hjelp av npm.

> **Merk**: Du kan se noen npm-advarsler. Dette er forventet.

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
> **Tips**: Windows-brukere kan trenge å endre PowerShell Execution Policy (f.eks.
> sette den til RemoteSigned eller Unrestricted) før de kjører enkelte Powershell-kommandoer.
<!-- @os:end -->


<!-- @os:windows -->
> **PATH-problem**: Hvis `n8n --version` sier command not found, sørg for at npm sin globale bin-mappe ligger i bruker-`PATH`. Den vanlige installasjonsbanen er `C:\Users\<username>\AppData\Roaming\npm`. 
> Legg denne til i brukerens PATH (Rediger systemets miljøvariabler > Miljøvariabler > Rediger brukerens Path) og last inn terminalen på nytt. 

<!-- @os:end -->

<!-- @os:linux -->
Vi skal nå bruke Podman-tjenesten til å containerisere n8n-installasjonen vår.

Vennligst last ned følgende til en mappe etter eget valg: [compose.yml](assets/compose.yml)

I den mappen kjører du følgende kommando:
```bash
podman compose up -d
```

Dette skal installere n8n og skrive til persistent lagring.

Start n8n ved å skrive `localhost:5678` i adressefeltet i nettleseren.
<!-- @os:end -->

<!-- @os:windows -->
## Starte n8n

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
n8n starter en lokal webserver. Trykk `'o'` eller åpne nettleseren din på `http://localhost:5678` for å få tilgang til editoren.
<!-- @os:end -->


> **Tips**: Hold terminalvinduet åpent mens du bruker n8n. Hvis du lukker det, kan det stoppe serveren.

## Starte Lemonade

Lemonade er den lokale serveren som vil kjøre en modell og koble til n8n.

<!-- @os:linux -->
Åpne Lemonade-GUI-et ved å klikke på Lemonade-ikonet i verktøylinjen. Herfra kan du bla gjennom modeller, backender og laste inn de forhåndsinstallerte modellene.
<!-- @os:end -->

<!-- @os:windows -->
Åpne Lemonade-GUI-et ved å klikke på Lemonade-ikonet. Høyreklikk på ikonet i systemstatusfeltet for å åpne appen. Deretter kan du legge til modeller, backender og laste inn de forhåndsinstallerte modellene.
<!-- @os:end -->

>**Tips**: Når den kjører, er Lemonade-GUI-et også tilgjengelig på http://localhost:13305

Alternativt kan du åpne en terminal og kjøre `lemonade list` for å se hvilke modeller som er installert. Deretter kjører du:

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


## Sette opp arbeidsflyten

### Trinn 1: Registrer deg eller logg inn på n8n

Når du åpner n8n for første gang, blir du bedt om å opprette en konto eller logge inn:

1. Åpne `http://localhost:5678` i nettleseren din
2. Opprett en ny lokal konto med e-posten din, eller logg inn hvis du allerede har en
3. Når du er logget inn, vil du se n8n-dashbordet

> **Tips**: Hvis du blir låst ute av kontoen din, prøv `n8n user-management:reset`

### Trinn 2: Importer arbeidsflyten

Vi har laget en ferdig arbeidsflyt som du kan importere direkte:

1. Last ned følgende arbeidsflytfil: [financial-news-workflow.json](assets/financial-news-workflow.json)
2. Klikk på **Start from Scratch** for å åpne arbeidsflyteditoren. Alternativt kan du klikke på +-knappen øverst til venstre, og deretter **Add workflow**.
3. Klikk på **...**-menyen (tre prikker) i den øverste linjen til høyre og velg **Import from file**
4. Velg den nedlastede filen `financial-news-workflow.json`
5. Arbeidsflyten vil vises på lerretet
### Steg 3: Forstå arbeidsflyten

Den importerte arbeidsflyten inneholder 9 tilkoblede noder:

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| Node | Formål |
|------|---------|
| **When clicking 'Execute workflow'** | Manuell utløser for å starte arbeidsflyten |
| **Fetch Financial News Webpage** | HTTP GET-forespørsel til `https://apnews.com/business` |
| **Delay to Ensure Page Load** | Wait-node som sørger for at sideinnholdet er fullstendig lastet |
| **Extract News Headlines & Text** | HTML-node som trekker ut overskrifter, redaksjonens utvalg, toppsaker og regionale nyheter ved bruk av CSS-velgere |
| **Clean Extracted News Data** | Set-node som kombinerer alle uttrukne data i ett enkelt tekstfelt |
| **AI Financial News Summarizer** | AI Agent som behandler nyhetene med en systemprompt for finansanalyse |
| **Lemonade Chat Model** | Kobler til den lokale Lemonade-serveren som kjører LLM-en |
| **Structured Output Parser** | Formaterer AI-utdataen som strukturert JSON |
| **Convert to File** | Konverterer sammendraget til en nedlastbar fil |

### Steg 4: Konfigurer Lemonade-legitimasjon

Før du kjører arbeidsflyten må du koble den til den lokale Lemonade-serveren din:

1. Dobbeltklikk på **Lemonade Chat Model**-noden i n8n
2. I nedtrekksmenyen **Credential to connect with** velger du **Create New Credential**
3. Skriv inn verdiene i tabellen nedenfor og klikk lagre.
4. Velg den relevante modellen du har lastet inn i Lemonade Server.

  | Felt | Verdi |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **Merk**: Før du tester, kjør `lemonade status` i en terminal for å bekrefte at Lemonade-serveren kjører.
<!-- @device:halo_box -->
> Denne arbeidsflyten bruker GPT-OSS-120B, og den er forhåndsinstallert i Lemonade. Du kan endre dette til andre innlastede modeller i innstillingene til Lemonade Chat Model-noden.
<!-- @device:end -->

### Steg 5: Test arbeidsflyten

1. Sørg for at Lemonade kjører med en innlastet modell
2. Klikk **Execute workflow** nederst i midten av lerretet
3. Se hver node kjøre fra venstre til høyre – de blir grønne når de er fullført
4. Dobbeltklikk på **AI Financial News Summarizer**-noden for å se det genererte sammendraget i det nedre panelet.
5. Dobbeltklikk på **Convert to File**-noden for å laste ned den tilhørende tekstfilen i det nedre panelet.

## Forstå AI-agenten

AI Financial News Summarizer bruker en systemprompt utformet for finansanalyse:

```
You are an AI financial analyst. Your role is to read, understand, and
summarize key financial news from today. The goal is to provide investors
with a clear and concise market overview to support better investment decisions.

Investor Outlook
Today's news points to [bullish/bearish/neutral] sentiment. Watch for
[economic event/earnings report] tomorrow, which could influence market direction.
```

Agenten mottar de rensede nyhetsdataene og produserer et strukturert sammendrag med markedsstemning.

### Lagre arbeidsflyten din

Klikk på arbeidsflytnavnet øverst og gi det nytt navn om ønskelig. Arbeidsflyter lagres automatisk mens du jobber.

## Neste steg

- **Planlegg automatisering**: Erstatt Manual Trigger med en **Schedule Trigger** for å kjøre daglig
- **Send varsler**: Legg til en **Discord**-, **Slack**- eller **Email**-node for å motta sammendrag
- **Prøv forskjellige modeller**: Endre modellen i Lemonade Chat Model-noden for å eksperimentere med ulike LLM-er
- **Tilpass ekstrahering**: Endre CSS-velgerne i HTML Extract-noden for å målrette mot ulike nyhetsseksjoner
- **Prøv forskjellige backend-løsninger**: n8n støtter også [Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model), LM Studio og andre lokale LLM-backend-løsninger

### Utforsk n8n-maler

n8n har hundrevis av ferdigbygde arbeidsflytmaler. Bla gjennom det offisielle malbiblioteket på:

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

Søk etter "AI", "LLM" eller "automatisering" for å finne arbeidsflyter du kan importere og tilpasse.

For mer informasjon, se [n8n-dokumentasjonen](https://docs.n8n.io/).

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