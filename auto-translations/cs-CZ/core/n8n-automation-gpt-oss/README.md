<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový překlad.** Tato stránka byla automaticky přeložena z angličtiny a nebyla zkontrolována člověkem. Může obsahovat chyby a určité pokyny, příkazy, soubory ke stažení, dostupnost produktů nebo jiný obsah se může lišit podle jazyka nebo regionu. V případě jakéhokoli nesouladu nebo rozporu je rozhodující původní anglická verze playbooku.
<!-- auto-translated-disclaimer:end -->

# Překlad

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Přehled

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Tento playbook vyžaduje minimálně **32GB** systémové paměti.
<!-- @device:end -->

n8n je platforma pro automatizaci pracovních postupů, která umožňuje propojovat aplikace a služby pomocí vizuálního editoru založeného na uzlech.

Tento playbook vás naučí, jak nastavit sumarizátor finančních zpráv poháněný umělou inteligencí, který stahuje nejnovější obchodní titulky z RSS feedu zpráv a pomocí lokálního LLM běžícího na vašem systému vytváří shrnutí zaměřené na investory.

## Co se naučíte

- Jak nainstalovat a spustit n8n
- Import a konfigurace předpřipraveného workflow
- Připojení k Lemonade pomocí nativní integrace n8n
- Pochopení uzlů workflow a toku dat

## Co je Lemonade?

[Lemonade](https://lemonade-server.ai) je platforma pro lokální provoz LLM postavená pro hardware AMD. Poskytuje API kompatibilní s OpenAI, které běží zcela na vašem počítači – vaše data nikdy neopustí vaše zařízení.

V tomto playbooku používáme Lemonade k provozování lokálního LLM, ke kterému se n8n připojuje pro úlohy poháněné umělou inteligencí.

n8n obsahuje **nativní uzel Lemonade** (`Lemonade Chat Model`), který poskytuje integraci na profesionální úrovni – není potřeba žádná ruční konfigurace. Díky tomu je propojení vašeho lokálního LLM s automatizačními workflow jednoduché.

<!-- @device:halo_box,halo,stx,krk -->
## Nastavení konfigurace paměti

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Kontrola aktualizací softwaru

<!-- @require:software-update -->
<!-- @device:end -->

## Instalace softwarových předpokladů
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

## Instalace n8n
<!-- @os:windows -->
Nainstalujte n8n globálně pomocí npm.

> **Poznámka**: Může se zobrazit několik varování npm. To je očekávané.

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
> **Tip**: Uživatelé Windows mohou potřebovat upravit svou politiku spouštění PowerShellu (Execution Policy) (např.
> nastavit ji na RemoteSigned nebo Unrestricted) před spuštěním některých příkazů PowerShellu.
<!-- @os:end -->


<!-- @os:windows -->
> **Problém s PATH**: Pokud `n8n --version` hlásí, že příkaz nebyl nalezen, ujistěte se, že adresář globálního bin npm je zahrnut v uživatelské proměnné `PATH`. Obvyklá instalační cesta je `C:\Users\<username>\AppData\Roaming\npm`.
> Přidejte ji do uživatelské cesty (Upravit systémové proměnné prostředí > Proměnné prostředí > Upravit uživatelskou cestu) a znovu načtěte terminál.

<!-- @os:end -->

<!-- @os:linux -->
Nyní použijeme službu Podman k kontejnerizaci naší instalace n8n.

Stáhněte si prosím následující soubor do adresáře dle vlastního výběru: [compose.yml](assets/compose.yml)

V tomto adresáři spusťte následující příkaz:
```bash
podman compose up -d
```

Tím by se měl nainstalovat n8n a zapsat data do trvalého úložiště.

Spusťte n8n zadáním `localhost:5678` do adresního řádku prohlížeče.
<!-- @os:end -->

<!-- @os:windows -->
## Spuštění n8n

Spusťte n8n z terminálu:

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
n8n spustí lokální webový server. Stiskněte `'o'` nebo otevřete prohlížeč na adrese `http://localhost:5678` pro přístup k editoru.
<!-- @os:end -->


> **Tip**: Během používání n8n nechte okno terminálu otevřené. Jeho zavření by mohlo server zastavit.

## Spuštění Lemonade

Lemonade je lokální server, který bude spouštět model a propojovat se s n8n.

<!-- @os:linux -->
Otevřete GUI Lemonade kliknutím na ikonu Lemonade v hlavním panelu. Odsud můžete procházet modely, backendy a načítat předinstalované modely.
<!-- @os:end -->

<!-- @os:windows -->
Otevřete GUI Lemonade kliknutím na ikonu Lemonade. Pravým tlačítkem klikněte na ikonu v systémové liště pro otevření aplikace. Poté můžete přidávat modely, backendy a načítat předinstalované modely.
<!-- @os:end -->

>**Tip**: Po spuštění je GUI Lemonade také dostupné na adrese http://localhost:13305

Alternativně můžete otevřít terminál a spustit `lemonade list` pro zobrazení nainstalovaných modelů. Poté spusťte:

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


## Nastavení workflow

### Krok 1: Registrace nebo přihlášení do n8n

Při prvním otevření n8n budete vyzváni k vytvoření účtu nebo přihlášení:

1. Otevřete `http://localhost:5678` ve svém prohlížeči
2. Vytvořte nový lokální účet pomocí svého e-mailu, nebo se přihlaste, pokud již účet máte
3. Po přihlášení se zobrazí dashboard n8n

> **Tip**: Pokud se nemůžete přihlásit ke svému účtu, zkuste `n8n user-management:reset`

### Krok 2: Import workflow

Poskytli jsme předpřipravené workflow, které si můžete přímo importovat:

1. Stáhněte si následující soubor s workflow: [financial-news-workflow.json](assets/financial-news-workflow.json)
2. Kliknutím na **Start from Scratch** otevřete editor workflow. Alternativně klikněte na tlačítko + vlevo nahoře a poté na **Add workflow**.
3. Klikněte na nabídku **...** (tři tečky) v pravém horním rohu a vyberte **Import from file**
4. Vyberte stažený soubor `financial-news-workflow.json`
5. Workflow se zobrazí na plátně
### Krok 3: Pochopení workflow

Importované workflow obsahuje 8 propojených uzlů:

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| Uzel | Účel |
|------|---------|
| **When clicking 'Execute workflow'** | Ruční spouštěč pro zahájení workflow |
| **Fetch Financial News Feed** | Uzel RSS Read, který stahuje nejnovější obchodní titulky z RSS feedu (výchozí je feed NYT Business, není vyžadován žádný API klíč) |
| **Aggregate Headlines** | Uzel Aggregate, který shromažďuje titulky a shrnutí ze všech položek feedu do jediného seznamu |
| **Clean Extracted News Data** | Uzel Set, který spojí všechny titulky do jednoho textového pole |
| **AI Financial News Summarizer** | AI Agent, který zpracovává zprávy pomocí systémového promptu finančního analytika |
| **Lemonade Chat Model** | Připojuje se k vašemu lokálnímu serveru Lemonade se spuštěným LLM |
| **Structured Output Parser** | Formátuje výstup AI jako strukturovaný JSON |
| **Convert to File** | Převede shrnutí na soubor ke stažení |

> **Tip**: Chcete-li použít jiný zdroj zpráv, poklikejte na uzel **Fetch Financial News Feed** a nahraďte adresu URL libovolným preferovaným RSS feedem s obchodními nebo tržními zprávami.

### Krok 4: Konfigurace přihlašovacích údajů Lemonade

Než workflow spustíte, musíte jej propojit s vaším lokálním serverem Lemonade:

1. Poklikejte na uzel **Lemonade Chat Model** v n8n
2. V rozevírací nabídce **Credential to connect with** vyberte **Create New Credential**
3. Zadejte hodnoty z níže uvedené tabulky a klikněte na uložit.
4. Vyberte příslušný model, který máte načtený v Lemonade Server.

  | Pole | Hodnota |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **Poznámka**: Před testováním spusťte v terminálu příkaz `lemonade status`, abyste ověřili, že server Lemonade běží.
<!-- @device:halo_box -->
> Toto workflow používá GPT-OSS-120B, který je v Lemonade předinstalovaný. V nastavení uzlu Lemonade Chat Model jej můžete změnit na jiné načtené modely.
<!-- @device:end -->

### Krok 5: Otestování workflow

1. Ujistěte se, že Lemonade běží s načteným modelem
2. Klikněte na **Execute workflow** uprostřed dole na plátně
3. Sledujte, jak se jednotlivé uzly postupně zprava doleva vykonávají – po dokončení zezelenají
4. Poklikejte na uzel **AI Financial News Summarizer**, abyste v dolním panelu zobrazili vygenerované shrnutí.
5. Poklikejte na uzel **Convert to File**, abyste v dolním panelu stáhli odpovídající textový soubor.

## Pochopení AI Agenta

AI Financial News Summarizer používá systémový prompt navržený pro finanční analýzu:

```
You are an AI financial analyst. Your role is to read, understand, and
summarize key financial news from today. The goal is to provide investors
with a clear and concise market overview to support better investment decisions.

Investor Outlook
Today's news points to [bullish/bearish/neutral] sentiment. Watch for
[economic event/earnings report] tomorrow, which could influence market direction.
```

Agent přijímá vyčištěná data zpráv a vrací strukturované shrnutí s náladou na trhu.

### Uložení workflow

Klikněte na název workflow nahoře a podle potřeby jej přejmenujte. Workflow se během práce automaticky ukládá.

## Další kroky

- **Naplánování automatizace**: Nahraďte Manual Trigger uzlem **Schedule Trigger**, aby se workflow spouštělo denně
- **Odesílání oznámení**: Přidejte uzel **Discord**, **Slack** nebo **Email** pro přijímání shrnutí
- **Vyzkoušejte jiné modely**: Změňte model v uzlu Lemonade Chat Model a experimentujte s různými LLM
- **Změna zdroje zpráv**: Nasměrujte uzel **Fetch Financial News Feed** na jiný RSS feed, abyste sledovali jiné sekce nebo publikace
- **Vyzkoušejte jiné backendy**: n8n také podporuje [Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model), LM Studio a další lokální LLM backendy

### Prozkoumejte šablony n8n

n8n nabízí stovky předpřipravených šablon workflow. Procházejte oficiální knihovnu šablon na adrese:

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

Vyhledejte „AI“, „LLM“ nebo „automation“, abyste našli workflow, které můžete importovat a přizpůsobit.

Další informace naleznete v [dokumentaci n8n](https://docs.n8n.io/).

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