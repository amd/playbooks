<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový překlad.** Tato stránka byla automaticky přeložena z angličtiny a nebyla zkontrolována člověkem. Může obsahovat chyby a určité pokyny, příkazy, soubory ke stažení, dostupnost produktů nebo jiný obsah se může lišit podle jazyka nebo regionu. V případě jakéhokoli nesouladu nebo rozporu je rozhodující původní anglická verze playbooku.
<!-- auto-translated-disclaimer:end -->

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

Tento playbook vás naučí, jak nastavit shrnovač finančních zpráv poháněný umělou inteligencí, který stahuje sekci obchodních zpráv AP News, extrahuje klíčové titulky a pomocí místního LLM běžícího na vašem systému generuje shrnutí zaměřené na investory.

## Co se naučíte

- Jak nainstalovat a spustit n8n
- Import a konfigurace předpřipraveného pracovního postupu
- Připojení k Lemonade pomocí nativní integrace n8n
- Pochopení uzlů pracovního postupu a toku dat

## Co je Lemonade?

[Lemonade](https://lemonade-server.ai) je platforma pro místní obsluhu LLM postavená pro hardware AMD. Poskytuje API kompatibilní s OpenAI, které běží zcela na vašem počítači – vaše data nikdy neopustí vaše zařízení.

V tomto playbooku používáme Lemonade k obsluze místního LLM, ke kterému se n8n připojuje pro úlohy poháněné umělou inteligencí.

n8n obsahuje **nativní uzel Lemonade** (`Lemonade Chat Model`), který poskytuje plnohodnotnou integraci – není potřeba žádná ruční konfigurace. Díky tomu je připojení vašeho místního LLM k automatizovaným pracovním postupům snadné.

## Nastavení konfigurace paměti

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrola aktualizací softwaru

<!-- @require:software-update -->
<!-- @device:end -->

## Instalace softwarových předpokladů
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

## Instalace n8n
<!-- @os:windows -->
Nainstalujte n8n globálně pomocí npm.

> **Poznámka**: Může se zobrazit několik varování npm. To je očekávané chování.

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
> **Tip**: Uživatelé Windows možná budou muset upravit zásady spouštění PowerShellu (Execution Policy) (např.
> nastavením na RemoteSigned nebo Unrestricted) před spuštěním některých příkazů PowerShellu.
<!-- @os:end -->


<!-- @os:windows -->
> **Problém s PATH**: Pokud `n8n --version` hlásí, že příkaz nebyl nalezen, ujistěte se, že je globální bin adresář npm zahrnutý v uživatelské proměnné `PATH`. Obvyklá instalační cesta je `C:\Users\<username>\AppData\Roaming\npm`.
> Přidejte tuto cestu do uživatelské proměnné PATH (Upravit proměnné prostředí systému > Proměnné prostředí > Upravit uživatelskou proměnnou Path) a znovu načtěte terminál.

<!-- @os:end -->

<!-- @os:linux -->
Nyní použijeme službu Podman k containerizaci naší instalace n8n.

Stáhněte prosím následující soubor do adresáře dle vlastního výběru: [compose.yml](assets/compose.yml)

V tomto adresáři spusťte následující příkaz:
```bash
podman compose up -d
```

Tímto by se měl nainstalovat n8n a zapsat data do trvalého úložiště.

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
n8n spustí místní webový server. Stiskněte `'o'` nebo otevřete prohlížeč na adrese `http://localhost:5678`, abyste získali přístup k editoru.
<!-- @os:end -->


> **Tip**: Ponechte okno terminálu otevřené, dokud používáte n8n. Jeho zavření by mohlo server zastavit.

## Spuštění Lemonade

Lemonade je místní server, který bude spouštět model a připojovat se k n8n.

<!-- @os:linux -->
Otevřete grafické rozhraní Lemonade kliknutím na ikonu Lemonade na hlavním panelu. Zde můžete procházet modely, backendy a načítat předinstalované modely.
<!-- @os:end -->

<!-- @os:windows -->
Otevřete grafické rozhraní Lemonade kliknutím na ikonu Lemonade. Kliknutím pravým tlačítkem na ikonu v systémové liště otevřete aplikaci. Poté můžete přidávat modely, backendy a načítat předinstalované modely.
<!-- @os:end -->

>**Tip**: Po spuštění je grafické rozhraní Lemonade také dostupné na adrese http://localhost:13305

Alternativně můžete otevřít terminál a spustit `lemonade list`, čímž zjistíte, jaké modely jsou nainstalované. Poté spusťte:

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


## Nastavení pracovního postupu

### Krok 1: Registrace nebo přihlášení do n8n

Při prvním otevření n8n budete vyzváni k vytvoření účtu nebo přihlášení:

1. Otevřete `http://localhost:5678` ve svém prohlížeči
2. Vytvořte nový místní účet pomocí svého e-mailu, nebo se přihlaste, pokud již účet máte
3. Po přihlášení se zobrazí řídicí panel n8n

> **Tip**: Pokud jste uzamčeni ze svého účtu, zkuste `n8n user-management:reset`

### Krok 2: Import pracovního postupu

Poskytli jsme předpřipravený pracovní postup, který můžete přímo importovat:

1. Stáhněte si následující soubor s pracovním postupem: [financial-news-workflow.json](assets/financial-news-workflow.json)
2. Klikněte na **Start from Scratch**, čímž otevřete editor pracovních postupů. Alternativně klikněte na tlačítko + vlevo nahoře a poté na **Add workflow**.
3. Klikněte na nabídku **...** (tři tečky) v pravém horním rohu a vyberte **Import from file**
4. Vyberte stažený soubor `financial-news-workflow.json`
5. Pracovní postup se zobrazí na plátně
### Krok 3: Pochopení workflow

Importované workflow obsahuje 9 propojených uzlů:

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| Uzel | Účel |
|------|------|
| **When clicking 'Execute workflow'** | Manuální spouštěč pro spuštění workflow |
| **Fetch Financial News Webpage** | HTTP GET požadavek na `https://apnews.com/business` |
| **Delay to Ensure Page Load** | Uzel Wait zajišťující, že se obsah stránky zcela načte |
| **Extract News Headlines & Text** | Uzel HTML, který extrahuje titulky, redakční výběr, hlavní zprávy a regionální zprávy pomocí CSS selektorů |
| **Clean Extracted News Data** | Uzel Set, který spojí všechna extrahovaná data do jednoho textového pole |
| **AI Financial News Summarizer** | AI Agent, který zpracovává zprávy pomocí systémového promptu finančního analytika |
| **Lemonade Chat Model** | Připojuje se k vašemu lokálnímu serveru Lemonade se spuštěným LLM |
| **Structured Output Parser** | Formátuje výstup AI jako strukturovaný JSON |
| **Convert to File** | Převádí souhrn na soubor ke stažení |

### Krok 4: Konfigurace přihlašovacích údajů Lemonade

Před spuštěním workflow je potřeba jej propojit s vaším lokálním serverem Lemonade:

1. Dvakrát klikněte na uzel **Lemonade Chat Model** v n8n
2. V rozbalovací nabídce **Credential to connect with** vyberte **Create New Credential**
3. Zadejte hodnoty z tabulky níže a klikněte na uložení.
4. Vyberte příslušný model, který máte načtený v Lemonade Server.

  | Pole | Hodnota |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **Poznámka**: Před testováním spusťte v terminálu příkaz `lemonade status`, abyste potvrdili, že server Lemonade běží.
<!-- @device:halo_box -->
> Toto workflow používá GPT-OSS-120B, který je v Lemonade předinstalovaný. V nastavení uzlu Lemonade Chat Model jej můžete změnit na jiné načtené modely.
<!-- @device:end -->

### Krok 5: Otestování workflow

1. Ujistěte se, že Lemonade běží s načteným modelem
2. Klikněte na tlačítko **Execute workflow** dole uprostřed plátna
3. Sledujte, jak se jednotlivé uzly spouští zleva doprava — po dokončení zezelenají
4. Dvakrát klikněte na uzel **AI Financial News Summarizer**, abyste ve spodním panelu zobrazili vygenerovaný souhrn.
5. Dvakrát klikněte na uzel **Convert to File**, abyste ve spodním panelu stáhli odpovídající textový soubor.

## Pochopení AI agenta

AI Financial News Summarizer používá systémový prompt navržený pro finanční analýzu:

```
You are an AI financial analyst. Your role is to read, understand, and
summarize key financial news from today. The goal is to provide investors
with a clear and concise market overview to support better investment decisions.

Investor Outlook
Today's news points to [bullish/bearish/neutral] sentiment. Watch for
[economic event/earnings report] tomorrow, which could influence market direction.
```

Agent přijímá vyčištěná data zpráv a vrací strukturovaný souhrn s tržním sentimentem.

### Uložení vašeho workflow

Klikněte na název workflow nahoře a v případě potřeby jej přejmenujte. Workflow se během práce automaticky ukládá.

## Další kroky

- **Naplánujte automatizaci**: Nahraďte Manual Trigger uzlem **Schedule Trigger**, aby se spouštěl denně
- **Odesílejte upozornění**: Přidejte uzel **Discord**, **Slack** nebo **Email**, abyste dostávali souhrny
- **Vyzkoušejte jiné modely**: Změňte model v uzlu Lemonade Chat Model a experimentujte s různými LLM
- **Přizpůsobte extrakci**: Upravte CSS selektory v uzlu HTML Extract tak, aby cílily na jiné sekce zpráv
- **Vyzkoušejte jiné backendy**: n8n také podporuje [Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model), LM Studio a další lokální backendy pro LLM

### Prozkoumejte šablony n8n

n8n nabízí stovky předpřipravených šablon workflow. Procházejte oficiální knihovnu šablon na adrese:

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

Vyhledejte „AI“, „LLM“ nebo „automatizace“ a najděte workflow, které si můžete importovat a přizpůsobit.

Další informace najdete v [dokumentaci n8n](https://docs.n8n.io/).

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