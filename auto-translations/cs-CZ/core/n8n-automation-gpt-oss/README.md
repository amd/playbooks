<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Tento playbook používá speciální tagy, které GitHub nedokáže vykreslit. Pro správné zobrazení tohoto obsahu navštivte [amd.com/playbooks](https://amd.com/playbooks).
<!-- @github-only:end -->

## Přehled

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Tento playbook vyžaduje minimálně **32 GB** systémové paměti.
<!-- @device:end -->

n8n je platforma pro automatizaci pracovních postupů, která umožňuje propojovat aplikace a služby pomocí vizuálního editoru založeného na uzlech.

Tento playbook vás naučí, jak nastavit AI-powered sumarizátor finančních zpráv, který stahuje obsah z obchodní sekce AP News, extrahuje klíčové titulky a pomocí lokálního LLM běžícího na vašem systému generuje souhrn zaměřený na investory.

## Co se naučíte

- Jak nainstalovat a spustit n8n
- Importovat a konfigurovat předpřipravený pracovní postup
- Připojit se k Lemonade pomocí nativní integrace n8n
- Porozumět uzlům pracovního postupu a toku dat

## Co je Lemonade?

[Lemonade](https://lemonade-server.ai) je lokální platforma pro obsluhu LLM vytvořená pro hardware AMD. Poskytuje OpenAI-kompatibilní API, které běží zcela na vašem počítači – vaše data nikdy neopustí vaše zařízení.

V tomto playbooku používáme Lemonade k obsluze lokálního LLM, ke kterému se n8n připojuje pro úlohy využívající AI.

n8n obsahuje **nativní uzel Lemonade** (`Lemonade Chat Model`), který poskytuje prvotřídní integraci – není potřeba ruční konfigurace. Díky tomu je připojení lokálního LLM k automatizačním pracovním postupům přímočaré.

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

> **Poznámka**: Mohou se zobrazit některá upozornění npm. To je očekávané chování.

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
> **Tip**: Uživatelé Windows mohou před spuštěním některých příkazů PowerShell potřebovat upravit zásady spouštění PowerShellu (např.
> nastavit je na RemoteSigned nebo Unrestricted).
<!-- @os:end -->


<!-- @os:windows -->
> **Problém s PATH**: Pokud příkaz `n8n --version` hlásí, že příkaz nebyl nalezen, ujistěte se, že globální adresář npm bin je uveden v uživatelské proměnné `PATH`. Obvyklá instalační cesta je `C:\Users\<username>\AppData\Roaming\npm`.
> Přidejte tuto cestu do uživatelské proměnné PATH (Upravit systémové proměnné prostředí > Proměnné prostředí > Upravit uživatelskou cestu) a restartujte terminál.

<!-- @os:end -->

<!-- @os:linux -->
Nyní použijeme službu Podman k vytvoření kontejneru pro naši instalaci n8n.

Stáhněte prosím následující soubor do vámi zvoleného adresáře: [compose.yml](assets/compose.yml)

V tomto adresáři spusťte následující příkaz:
```bash
podman compose up -d
```

Tím by se mělo nainstalovat n8n a zapsat data do trvalého úložiště.

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
n8n spustí lokální webový server. Stiskněte `'o'` nebo otevřete prohlížeč na adrese `http://localhost:5678` pro přístup k editoru.
<!-- @os:end -->


> **Tip**: Při používání n8n nechte okno terminálu otevřené. Jeho zavření může server zastavit.

## Spuštění Lemonade

Lemonade je lokální server, který spustí model a připojí se k n8n.

<!-- @os:linux -->
Otevřete grafické rozhraní Lemonade kliknutím na ikonu Lemonade na hlavním panelu. Odtud můžete procházet modely, backendy a načítat předinstalované modely.
<!-- @os:end -->

<!-- @os:windows -->
Otevřete grafické rozhraní Lemonade kliknutím na ikonu Lemonade. Pravým tlačítkem klikněte na ikonu v systémové liště a otevřete aplikaci. Poté můžete přidávat modely, backendy a načítat předinstalované modely.
<!-- @os:end -->

>**Tip**: Po spuštění je grafické rozhraní Lemonade dostupné také na adrese http://localhost:13305

Případně můžete otevřít terminál a spustit příkaz `lemonade list` pro zobrazení nainstalovaných modelů. Poté spusťte:

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

1. Otevřete `http://localhost:5678` v prohlížeči
2. Vytvořte nový lokální účet pomocí e-mailové adresy, nebo se přihlaste, pokud již účet máte
3. Po přihlášení se zobrazí řídicí panel n8n

> **Tip**: Pokud jste uzamčeni ze svého účtu, zkuste příkaz `n8n user-management:reset`

### Krok 2: Import pracovního postupu

Připravili jsme předpřipravený pracovní postup, který můžete přímo importovat:

1. Stáhněte následující soubor pracovního postupu: [financial-news-workflow.json](assets/financial-news-workflow.json)
2. Klikněte na **Start from Scratch** pro otevření editoru pracovního postupu. Případně klikněte na tlačítko + v levém horním rohu a poté na **Add workflow**.
3. Klikněte na nabídku **...** (tři tečky) v pravém horním panelu a vyberte **Import from file**
4. Vyberte stažený soubor `financial-news-workflow.json`
5. Pracovní postup se zobrazí na plátně


### Krok 3: Pochopení pracovního postupu

Importovaný pracovní postup obsahuje 9 propojených uzlů:

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| Uzel | Účel |
|------|---------|
| **When clicking 'Execute workflow'** | Ruční spouštěč pro zahájení pracovního postupu |
| **Fetch Financial News Webpage** | HTTP GET požadavek na `https://apnews.com/business` |
| **Delay to Ensure Page Load** | Čekací uzel zajišťující úplné načtení obsahu stránky |
| **Extract News Headlines & Text** | HTML uzel, který extrahuje titulky, výběr redakce, hlavní zprávy a regionální zprávy pomocí CSS selektorů |
| **Clean Extracted News Data** | Uzel Set, který kombinuje všechna extrahovaná data do jednoho textového pole |
| **AI Financial News Summarizer** | AI Agent, který zpracovává zprávy pomocí systémového promptu finančního analytika |
| **Lemonade Chat Model** | Připojuje se k vašemu lokálnímu serveru Lemonade, na kterém běží LLM |
| **Structured Output Parser** | Formátuje výstup AI jako strukturovaný JSON |
| **Convert to File** | Převádí souhrn na soubor ke stažení |

### Krok 4: Konfigurace přihlašovacích údajů Lemonade

Před spuštěním pracovního postupu je třeba jej připojit k lokálnímu serveru Lemonade:

1. Dvakrát klikněte na uzel **Lemonade Chat Model** v n8n
2. V rozevírací nabídce **Credential to connect with** vyberte **Create New Credential**
3. Zadejte hodnoty z níže uvedené tabulky a klikněte na uložit.
4. Vyberte příslušný model, který máte načtený na serveru Lemonade.

  | Pole | Hodnota |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **Poznámka**: Před testováním spusťte v terminálu příkaz `lemonade status` a ověřte, že server Lemonade běží.
<!-- @device:halo_box -->
> Tento pracovní postup používá GPT-OSS-120B, který je předinstalován v Lemonade. Toto nastavení můžete změnit na jiné načtené modely v nastavení uzlu Lemonade Chat Model.
<!-- @device:end -->

### Krok 5: Testování pracovního postupu

1. Ujistěte se, že Lemonade běží s načteným modelem
2. Klikněte na **Execute workflow** ve spodní části středu plátna
3. Sledujte, jak se jednotlivé uzly postupně spouštějí zleva doprava – po dokončení se zbarví zeleně
4. Dvakrát klikněte na uzel **AI Financial News Summarizer** pro zobrazení vygenerovaného souhrnu ve spodním panelu.
5. Dvakrát klikněte na uzel **Convert to File** pro stažení odpovídajícího textového souboru ve spodním panelu.

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

Agent přijímá vyčištěná zpravodajská data a vytváří strukturovaný souhrn s tržním sentimentem.

### Uložení pracovního postupu

Klikněte na název pracovního postupu v horní části a v případě potřeby jej přejmenujte. Pracovní postupy se při práci automaticky ukládají.

## Další kroky

- **Plánování automatizace**: Nahraďte ruční spouštěč spouštěčem **Schedule Trigger** pro každodenní spouštění
- **Odesílání oznámení**: Přidejte uzel **Discord**, **Slack** nebo **Email** pro příjem souhrnů
- **Vyzkoušejte různé modely**: Změňte model v uzlu Lemonade Chat Model a experimentujte s různými LLM
- **Přizpůsobení extrakce**: Upravte CSS selektory uzlu HTML Extract pro cílení na různé zpravodajské sekce
- **Vyzkoušejte různé backendy**: n8n také podporuje [Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model), LM Studio a další lokální LLM backendy

### Prozkoumejte šablony n8n

n8n nabízí stovky předpřipravených šablon pracovních postupů. Procházejte oficiální knihovnu šablon na adrese:

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

Vyhledejte „AI", „LLM" nebo „automation" a najděte pracovní postupy, které můžete importovat a přizpůsobit.

Další informace naleznete v [dokumentaci n8n](https://docs.n8n.io/).