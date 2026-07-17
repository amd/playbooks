<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Tento playbook používa špeciálne značky, ktoré GitHub nedokáže vykresliť. Správny náhľad tohto obsahu nájdete na [amd.com/playbooks](https://amd.com/playbooks).
<!-- @github-only:end -->

## Prehľad

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Tento playbook vyžaduje minimálne **32 GB** systémovej pamäte.
<!-- @device:end -->

n8n je platforma na automatizáciu pracovných postupov, ktorá vám umožňuje prepájať aplikácie a služby pomocou vizuálneho editora založeného na uzloch.

Tento playbook vás naučí, ako nastaviť AI-powered sumarizátor finančných správ, ktorý prehľadáva sekciu obchodu AP News, extrahuje kľúčové titulky a používa lokálny LLM bežiaci na vašom systéme na generovanie súhrnu zameraného na investorov.

## Čo sa naučíte

- Ako nainštalovať a spustiť n8n
- Importovanie a konfigurácia vopred pripraveného pracovného postupu
- Pripojenie k Lemonade pomocou natívnej integrácie n8n
- Pochopenie uzlov pracovného postupu a toku dát

## Čo je Lemonade?

[Lemonade](https://lemonade-server.ai) je lokálna platforma na obsluhu LLM vytvorená pre hardware AMD. Poskytuje OpenAI-kompatibilné API, ktoré beží výlučne na vašom zariadení – vaše dáta nikdy neopustia vaše zariadenie.

V tomto playbooku používame Lemonade na obsluhu lokálneho LLM, ku ktorému sa n8n pripája pre úlohy s podporou AI.

n8n obsahuje **natívny uzol Lemonade** (`Lemonade Chat Model`), ktorý poskytuje prvotriednu integráciu – nie je potrebná manuálna konfigurácia. Vďaka tomu je prepojenie vášho lokálneho LLM s automatizačnými pracovnými postupmi jednoduché.

## Nastavenie konfigurácie pamäte

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrola aktualizácií softvéru

<!-- @require:software-update -->
<!-- @device:end -->

## Inštalácia softvérových predpokladov
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

## Inštalácia n8n
<!-- @os:windows -->
Nainštalujte n8n globálne pomocou npm.

> **Poznámka**: Môžu sa zobraziť niektoré upozornenia npm. Je to očakávané.

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
> **Tip**: Používatelia systému Windows môžu pred spustením niektorých príkazov PowerShell potrebovať upraviť politiku spúšťania PowerShell (napr.
> nastaviť ju na RemoteSigned alebo Unrestricted).
<!-- @os:end -->


<!-- @os:windows -->
> **Problém s PATH**: Ak `n8n --version` hlási, že príkaz nebol nájdený, uistite sa, že globálny adresár npm bin je v používateľskej premennej `PATH`. Obvyklá inštalačná cesta je `C:\Users\<username>\AppData\Roaming\npm`.
> Pridajte túto cestu do používateľskej premennej PATH (Upraviť systémové premenné prostredia > Premenné prostredia > Upraviť používateľskú cestu) a znovu načítajte terminál.

<!-- @os:end -->

<!-- @os:linux -->
Teraz použijeme službu Podman na kontajnerizáciu našej inštalácie n8n.

Stiahnite si nasledujúci súbor do adresára podľa vlastného výberu: [compose.yml](assets/compose.yml)

V tomto adresári spustite nasledujúci príkaz:
```bash
podman compose up -d
```

Tým by sa mal nainštalovať n8n a zapisovať do trvalého úložiska.

Spustite n8n zadaním `localhost:5678` do panela s adresou prehliadača.
<!-- @os:end -->

<!-- @os:windows -->
## Spustenie n8n

Spustite n8n z terminálu:

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
n8n spustí lokálny webový server. Stlačte `'o'` alebo otvorte prehliadač na adrese `http://localhost:5678` pre prístup k editoru.
<!-- @os:end -->


> **Tip**: Počas používania n8n nechajte okno terminálu otvorené. Jeho zatvorenie môže zastaviť server.

## Spustenie Lemonade

Lemonade je lokálny server, ktorý spustí model a pripojí sa k n8n.

<!-- @os:linux -->
Otvorte GUI Lemonade kliknutím na ikonu Lemonade na paneli úloh. Odtiaľ môžete prehliadať modely, backendy a načítať vopred nainštalované modely.
<!-- @os:end -->

<!-- @os:windows -->
Otvorte GUI Lemonade kliknutím na ikonu Lemonade. Kliknite pravým tlačidlom myši na ikonu v systémovej lište a otvorte aplikáciu. Potom môžete pridávať modely, backendy a načítať vopred nainštalované modely.
<!-- @os:end -->

>**Tip**: Po spustení je GUI Lemonade dostupné aj na adrese http://localhost:13305

Prípadne môžete otvoriť terminál a spustiť `lemonade list`, aby ste zistili, ktoré modely sú nainštalované. Potom spustite:

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


## Nastavenie pracovného postupu

### Krok 1: Zaregistrujte sa alebo prihláste do n8n

Pri prvom otvorení n8n budete vyzvaní na vytvorenie účtu alebo prihlásenie:

1. Otvorte `http://localhost:5678` vo svojom prehliadači
2. Vytvorte nový lokálny účet pomocou svojho e-mailu alebo sa prihláste, ak už účet máte
3. Po prihlásení sa zobrazí panel n8n

> **Tip**: Ak ste zablokovaní vo svojom účte, skúste `n8n user-management:reset`

### Krok 2: Importujte pracovný postup

Poskytli sme vopred pripravený pracovný postup, ktorý môžete priamo importovať:

1. Stiahnite si nasledujúci súbor pracovného postupu: [financial-news-workflow.json](assets/financial-news-workflow.json)
2. Kliknite na **Start from Scratch** a otvorte editor pracovného postupu. Prípadne kliknite na tlačidlo + v ľavom hornom rohu a potom na **Add workflow**.
3. Kliknite na ponuku **...** (tri bodky) v pravom hornom paneli a vyberte **Import from file**
4. Vyberte stiahnutý súbor `financial-news-workflow.json`
5. Pracovný postup sa zobrazí na plátne


### Krok 3: Pochopenie pracovného postupu

Importovaný pracovný postup obsahuje 9 prepojených uzlov:

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| Uzol | Účel |
|------|---------|
| **When clicking 'Execute workflow'** | Manuálny spúšťač na spustenie pracovného postupu |
| **Fetch Financial News Webpage** | HTTP GET požiadavka na `https://apnews.com/business` |
| **Delay to Ensure Page Load** | Čakací uzol na zabezpečenie úplného načítania obsahu stránky |
| **Extract News Headlines & Text** | HTML uzol, ktorý extrahuje titulky, výbery redaktorov, hlavné správy a regionálne správy pomocou CSS selektorov |
| **Clean Extracted News Data** | Uzol Set, ktorý kombinuje všetky extrahované dáta do jedného textového poľa |
| **AI Financial News Summarizer** | AI Agent, ktorý spracováva správy so systémovým promptom finančného analytika |
| **Lemonade Chat Model** | Pripája sa k vášmu lokálnemu serveru Lemonade, na ktorom beží LLM |
| **Structured Output Parser** | Formátuje výstup AI ako štruktúrovaný JSON |
| **Convert to File** | Konvertuje súhrn na stiahnuteľný súbor |

### Krok 4: Konfigurácia prihlasovacích údajov Lemonade

Pred spustením pracovného postupu ho musíte pripojiť k vášmu lokálnemu serveru Lemonade:

1. Dvakrát kliknite na uzol **Lemonade Chat Model** v n8n
2. V rozbaľovacej ponuke **Credential to connect with** vyberte **Create New Credential**
3. Zadajte hodnoty z tabuľky nižšie a kliknite na uložiť.
4. Vyberte príslušný model, ktorý ste načítali na serveri Lemonade.

  | Pole | Hodnota |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **Poznámka**: Pred testovaním spustite `lemonade status` v termináli, aby ste potvrdili, že server Lemonade beží.
<!-- @device:halo_box -->
> Tento pracovný postup používa GPT-OSS-120B, ktorý je vopred nainštalovaný v Lemonade. Môžete ho zmeniť na iné načítané modely v nastaveniach uzla Lemonade Chat Model.
<!-- @device:end -->

### Krok 5: Otestujte pracovný postup

1. Uistite sa, že Lemonade beží s načítaným modelom
2. Kliknite na **Execute workflow** v dolnej časti stredu plátna
3. Sledujte, ako sa každý uzol vykonáva zľava doprava – po dokončení sa zofarbia na zeleno
4. Dvakrát kliknite na uzol **AI Financial News Summarizer**, aby ste v dolnom paneli videli vygenerovaný súhrn.
5. Dvakrát kliknite na uzol **Convert to File**, aby ste v dolnom paneli stiahli zodpovedajúci textový súbor.

## Pochopenie AI agenta

AI Financial News Summarizer používa systémový prompt navrhnutý pre finančnú analýzu:

```
You are an AI financial analyst. Your role is to read, understand, and
summarize key financial news from today. The goal is to provide investors
with a clear and concise market overview to support better investment decisions.

Investor Outlook
Today's news points to [bullish/bearish/neutral] sentiment. Watch for
[economic event/earnings report] tomorrow, which could influence market direction.
```

Agent prijíma vyčistené spravodajské dáta a vytvára štruktúrovaný súhrn s trhovým sentimentom.

### Uloženie pracovného postupu

Kliknite na názov pracovného postupu v hornej časti a podľa potreby ho premenujte. Pracovné postupy sa automaticky ukladajú počas práce.

## Ďalšie kroky

- **Plánovaná automatizácia**: Nahraďte manuálny spúšťač spúšťačom **Schedule Trigger** na denné spúšťanie
- **Odosielanie upozornení**: Pridajte uzol **Discord**, **Slack** alebo **Email** na prijímanie súhrnov
- **Vyskúšajte rôzne modely**: Zmeňte model v uzle Lemonade Chat Model a experimentujte s rôznymi LLM
- **Prispôsobenie extrakcie**: Upravte CSS selektory uzla HTML Extract tak, aby cielili na rôzne sekcie správ
- **Vyskúšajte rôzne backendy**: n8n tiež podporuje [Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model), LM Studio a ďalšie lokálne LLM backendy

### Preskúmajte šablóny n8n

n8n má stovky vopred pripravených šablón pracovných postupov. Prehliadajte oficiálnu knižnicu šablón na:

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

Vyhľadajte „AI", „LLM" alebo „automation" a nájdite pracovné postupy, ktoré môžete importovať a prispôsobiť.

Ďalšie informácie nájdete v [dokumentácii n8n](https://docs.n8n.io/).