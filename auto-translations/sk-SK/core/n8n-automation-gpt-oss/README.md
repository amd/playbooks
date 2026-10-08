<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový preklad.** Táto stránka bola automaticky preložená z angličtiny a nebola skontrolovaná človekom. Môže obsahovať chyby a niektoré pokyny, príkazy, súbory na stiahnutie, dostupnosť produktov alebo iný obsah sa môžu líšiť v závislosti od jazyka alebo regiónu. V prípade akéhokoľvek nesúladu alebo rozdielu je rozhodujúca a záväzná pôvodná anglická verzia playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->
## Prehľad
<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Táto príručka vyžaduje minimálne **32 GB** systémovej pamäte.
<!-- @device:end -->
n8n je platforma na automatizáciu pracovných postupov, ktorá umožňuje prepájať aplikácie a služby pomocou vizuálneho editora založeného na uzloch.

Táto príručka vás naučí, ako nastaviť sumarizátor finančných správ poháňaný umelou inteligenciou, ktorý získava najnovšie obchodné titulky z RSS kanála so správami a používa lokálny LLM bežiaci vo vašom systéme na vytvorenie súhrnu zameraného na investorov.

## Čo sa naučíte

- Ako nainštalovať a spustiť n8n
- Import a konfigurácia vopred vytvoreného pracovného postupu
- Pripojenie k Lemonade pomocou natívnej integrácie n8n
- Pochopenie uzlov pracovného postupu a toku dát

## Čo je Lemonade?

[Lemonade](https://lemonade-server.ai) je platforma na lokálne spúšťanie LLM navrhnutá pre hardvér AMD. Poskytuje API kompatibilné s OpenAI, ktoré beží úplne na vašom počítači – vaše dáta nikdy neopustia vaše zariadenie.

V tejto príručke používame Lemonade na spustenie lokálneho LLM, ku ktorému sa pripája n8n pre úlohy poháňané umelou inteligenciou.

n8n obsahuje **natívny uzol Lemonade** (`Lemonade Chat Model`), ktorý poskytuje plnohodnotnú integráciu - nie je potrebná žiadna manuálna konfigurácia. Vďaka tomu je pripojenie vášho lokálneho LLM k automatizovaným pracovným postupom jednoduché.
<!-- @device:halo_box,halo,stx,krk -->
## Nastavenie konfigurácie pamäte
<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Kontrola aktualizácií softvéru
<!-- @require:software-update -->
<!-- @device:end -->
## Inštalácia softvérových predpokladov
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

<!-- @os:windows -->
> **Tip**: Používatelia systému Windows môžu potrebovať upraviť svoju politiku spúšťania PowerShell (Execution Policy) (napr.
> nastaviť ju na RemoteSigned alebo Unrestricted) pred spustením niektorých príkazov PowerShell.
<!-- @os:end -->


<!-- @os:windows -->
> **Problém s PATH**: Ak `n8n --version` hlási, že príkaz sa nenašiel, uistite sa, že adresár s globálnymi binárnymi súbormi npm je zahrnutý v používateľskej premennej `PATH`. Štandardná inštalačná cesta je `C:\Users\<username>\AppData\Roaming\npm`.
> Pridajte túto cestu do používateľskej premennej PATH (Upraviť systémové premenné prostredia > Premenné prostredia > Upraviť User Path) a reštartujte terminál.
<!-- @os:end -->

<!-- @os:linux -->
Teraz použijeme službu Podman na kontajnerizáciu našej inštalácie n8n.

Stiahnite si do adresára podľa vlastného výberu nasledovné: [compose.yml](assets/compose.yml)

V tomto adresári spustite nasledujúci príkaz:
```bash
podman compose up -d
```

Týmto by sa mal nainštalovať n8n a zapísať údaje do trvalého úložiska.

Spustite n8n zadaním `localhost:5678` do adresového riadka vášho prehliadača.
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
n8n spustí lokálny webový server. Stlačte `'o'` alebo otvorte prehliadač na adrese `http://localhost:5678`, aby ste získali prístup k editoru.
<!-- @os:end -->
> **Tip**: Nechajte okno terminálu otvorené počas používania n8n. Jeho zatvorenie môže zastaviť server.

## Spustenie Lemonade

Lemonade je lokálny server, ktorý bude spúšťať model a pripájať sa k n8n.
<!-- @os:linux -->
Otvorte Lemonade GUI kliknutím na ikonu Lemonade na paneli úloh. Odtiaľto môžete prehliadať modely, backendy a načítať predinštalované modely.
<!-- @os:end -->

<!-- @os:windows -->
Otvorte GUI aplikácie Lemonade kliknutím na ikonu Lemonade. Pravým tlačidlom kliknite na ikonu v systémovej lište a otvorte aplikáciu. Následne môžete pridávať modely, backendy a načítať predinštalované modely.
<!-- @os:end -->
>**Tip**: Po spustení je rozhranie Lemonade GUI dostupné aj na adrese http://localhost:13305

Alternatívne môžete otvoriť terminál a spustiť príkaz `lemonade list`, aby ste videli, ktoré modely sú nainštalované. Potom spustite:
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

### Krok 1: Zaregistrujte sa alebo sa prihláste do n8n

Pri prvom otvorení n8n budete vyzvaní na vytvorenie konta alebo prihlásenie:

1. Otvorte `http://localhost:5678` vo svojom prehliadači
2. Vytvorte nové lokálne konto so svojím e-mailom, alebo sa prihláste, ak už konto máte
3. Po prihlásení uvidíte prehľad n8n

> **Tip**: Ak ste uzamknutí mimo svojho konta, skúste `n8n user-management:reset`

### Krok 2: Importujte pracovný postup

Poskytli sme vopred vytvorený pracovný postup, ktorý môžete priamo importovať:

1. Stiahnite si nasledujúci súbor pracovného postupu: [financial-news-workflow.json](assets/financial-news-workflow.json)
2. Kliknite na **Start from Scratch**, čím otvoríte editor pracovného postupu. Prípadne kliknite na tlačidlo + vľavo hore a potom na **Add workflow**.
3. Kliknite na ponuku **...** (tri bodky) v pravom hornom paneli a vyberte **Import from file**
4. Vyberte stiahnutý súbor `financial-news-workflow.json`
5. Pracovný postup sa zobrazí na plátne
### Krok 3: Pochopenie pracovného postupu

Importovaný pracovný postup obsahuje 8 prepojených uzlov:

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| Uzol | Účel |
|------|---------|
| **When clicking 'Execute workflow'** | Manuálny spúšťač na spustenie pracovného postupu |
| **Fetch Financial News Feed** | Uzol RSS Read, ktorý získava najnovšie obchodné titulky z RSS kanála (predvolene z kanála NYT Business, bez potreby API kľúča) |
| **Aggregate Headlines** | Uzol Aggregate, ktorý zhromažďuje titulky a zhrnutia zo všetkých položiek kanála do jedného zoznamu |
| **Clean Extracted News Data** | Uzol Set, ktorý spája všetky titulky do jedného textového poľa |
| **AI Financial News Summarizer** | AI Agent, ktorý spracováva správy pomocou systémového promptu finančného analytika |
| **Lemonade Chat Model** | Pripája sa k vášmu lokálnemu serveru Lemonade so spusteným LLM |
| **Structured Output Parser** | Formátuje výstup AI ako štruktúrovaný JSON |
| **Convert to File** | Prevádza zhrnutie na súbor na stiahnutie |

> **Tip**: Ak chcete použiť iný zdroj správ, dvakrát kliknite na uzol **Fetch Financial News Feed** a nahraďte URL adresu ľubovoľným obchodným alebo trhovým RSS kanálom podľa vášho výberu.

### Krok 4: Konfigurácia prihlasovacích údajov Lemonade

Pred spustením pracovného postupu je potrebné pripojiť ho k vášmu lokálnemu serveru Lemonade:

1. Dvakrát kliknite na uzol **Lemonade Chat Model** v n8n
2. V rozbaľovacej ponuke **Credential to connect with** vyberte **Create New Credential**
3. Zadajte hodnoty z tabuľky nižšie a kliknite na uloženie.
4. Vyberte príslušný model, ktorý máte načítaný v Lemonade Server.

  | Pole | Hodnota |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **Poznámka**: Pred testovaním spustite v termináli príkaz `lemonade status`, aby ste potvrdili, že server Lemonade beží.
<!-- @device:halo_box -->
> Tento pracovný postup používa GPT-OSS-120B, ktorý je predinštalovaný v Lemonade. Môžete to zmeniť na iné načítané modely v nastaveniach uzla Lemonade Chat Model.
<!-- @device:end -->

### Krok 5: Otestovanie pracovného postupu

1. Uistite sa, že Lemonade beží s načítaným modelom
2. Kliknite na **Execute workflow** v dolnej strednej časti plátna
3. Sledujte, ako sa jednotlivé uzly vykonávajú zľava doprava – po dokončení sa sfarbia na zeleno
4. Dvakrát kliknite na uzol **AI Financial News Summarizer**, aby ste v spodnom paneli videli vygenerované zhrnutie.
5. Dvakrát kliknite na uzol **Convert to File**, aby ste v spodnom paneli stiahli príslušný textový súbor.

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

Agent prijíma vyčistené dáta zo správ a vytvára štruktúrované zhrnutie s informáciou o nálade na trhu.

### Uloženie vášho pracovného postupu

Kliknite na názov pracovného postupu v hornej časti a podľa potreby ho premenujte. Pracovné postupy sa počas práce automaticky ukladajú.

## Ďalšie kroky

- **Naplánovanie automatizácie**: Nahraďte Manual Trigger uzlom **Schedule Trigger**, aby sa spúšťal denne
- **Odosielanie upozornení**: Pridajte uzol **Discord**, **Slack** alebo **Email** na prijímanie zhrnutí
- **Vyskúšajte rôzne modely**: Zmeňte model v uzle Lemonade Chat Model, aby ste mohli experimentovať s rôznymi LLM
- **Zmena zdroja správ**: Nasmerujte uzol **Fetch Financial News Feed** na iný RSS kanál, aby ste sledovali iné sekcie alebo publikácie
- **Vyskúšajte rôzne backendy**: n8n tiež podporuje [Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model), LM Studio a ďalšie lokálne LLM backendy

### Preskúmajte šablóny n8n

n8n má stovky vopred pripravených šablón pracovných postupov. Prehliadajte si oficiálnu knižnicu šablón na:

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

Vyhľadajte „AI“, „LLM“ alebo „automatizácia“, aby ste našli pracovné postupy, ktoré môžete importovať a prispôsobiť.

Ďalšie informácie nájdete v [dokumentácii n8n](https://docs.n8n.io/).

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