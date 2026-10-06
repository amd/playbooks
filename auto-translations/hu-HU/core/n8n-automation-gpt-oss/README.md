<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Gépi fordítás.** Ez az oldal automatikusan lett lefordítva angol nyelvről, és emberi ellenőrzésen nem esett át. Hibákat tartalmazhat, és bizonyos utasítások, parancsok, letöltések, termékelérhetőség vagy egyéb tartalmak nyelvenként vagy régiónként eltérhetnek. Bármilyen eltérés vagy ellentmondás esetén a playbook eredeti angol nyelvű változata az irányadó.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->
# Áttekintés
<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Ez a playbook minimum **32 GB** rendszermemóriát igényel.
<!-- @device:end -->
Az n8n egy workflow automatizálási platform, amellyel vizuális, node-alapú szerkesztő segítségével kapcsolhatsz össze alkalmazásokat és szolgáltatásokat.

Ez a playbook megmutatja, hogyan állíthatsz be egy AI-alapú pénzügyi hírösszefoglalót, amely lekéri a legfrissebb üzleti híreket egy hír RSS-feedből, majd egy, a rendszereden futó helyi LLM segítségével befektető-központú összefoglalót készít.

## Mit fogsz megtanulni

- Hogyan telepítsd és indítsd el az n8n-t
- Egy előre elkészített workflow importálását és konfigurálását
- Hogyan csatlakozz a Lemonade-hez a natív n8n integráció használatával
- A workflow node-ok és az adatáramlás megértését

## Mi az a Lemonade?

A [Lemonade](https://lemonade-server.ai) egy helyi LLM-kiszolgáló platform, amelyet kifejezetten AMD hardverekhez fejlesztettek. OpenAI-kompatibilis API-t biztosít, amely teljes egészében a gépeden fut – az adataid soha nem hagyják el az eszközödet.

Ebben a playbookban a Lemonade-et használjuk egy helyi LLM kiszolgálására, amelyhez az n8n csatlakozik az AI-alapú feladatokhoz.

Az n8n tartalmaz egy **natív Lemonade node-ot** (`Lemonade Chat Model`), amely elsőrangú integrációt biztosít – nincs szükség manuális konfigurálásra. Ez egyszerűvé teszi a helyi LLM csatlakoztatását az automatizálási workflow-khoz.
<!-- @device:halo_box,halo,stx,krk -->
## Memóriakonfiguráció beállítása
<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Szoftverfrissítések ellenőrzése
<!-- @require:software-update -->
<!-- @device:end -->
## Szoftveres előfeltételek telepítése
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
# n8n telepítése
<!-- @os:windows -->
npm segítségével telepítsd az n8n-t globálisan.

> **Megjegyzés**: Előfordulhat, hogy néhány npm figyelmeztetést látsz. Ez normális.

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
**Tipp**: Előfordulhat, hogy a Windows felhasználóknak módosítaniuk kell a PowerShell végrehajtási szabályzatát (Execution Policy) (például RemoteSigned vagy Unrestricted értékre állítva) bizonyos PowerShell parancsok futtatása előtt.
<!-- @os:end -->


<!-- @os:windows -->
**PATH probléma**: Ha a `n8n --version` parancs futtatásakor a command not found hibaüzenetet kapod, győződj meg róla, hogy az npm globális bin könyvtára szerepel a felhasználói `PATH` változóban. A szokásos telepítési útvonal a `C:\Users\<username>\AppData\Roaming\npm`.
> Add hozzá ezt a felhasználói elérési úthoz (Rendszerkörnyezeti változók szerkesztése > Környezeti változók > Felhasználói elérési út szerkesztése), majd töltsd be újra a terminált.
<!-- @os:end -->

<!-- @os:linux -->
Most a Podman szolgáltatást fogjuk használni az n8n telepítésünk konténerizálásához.

Kérjük, töltsd le a következőt egy általad választott könyvtárba: [compose.yml](assets/compose.yml)

Abban a könyvtárban futtasd a következő parancsot:
```bash
podman compose up -d
```

Ennek telepítenie kell az n8n-t, és írnia kell egy perzisztens tárolóba.

Indítsd el az n8n-t a `localhost:5678` cím böngésződ címsorába történő beírásával.
<!-- @os:end -->

<!-- @os:windows -->
## n8n indítása

Indítsa el az n8n-t a terminálból:

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
Az n8n elindít egy helyi webszervert. Nyomd meg az `'o'` billentyűt, vagy nyisd meg a böngésződet a(z) `http://localhost:5678` címen a szerkesztő eléréséhez.
<!-- @os:end -->
> **Tipp**: Hagyja nyitva a terminálablakot az n8n használata közben. Ha bezárja, leállhat a szerver.

## A Lemonade elindítása

A Lemonade az a helyi szerver, amely egy modellt futtat, és csatlakozik az n8n-hez.
<!-- @os:linux -->
A Lemonade GUI megnyitásához kattintson a Lemonade ikonra a tálcán. Innen böngészhet a modellek, a backendek között, és betöltheti az előre telepített modelleket.
<!-- @os:end -->

<!-- @os:windows -->
A Lemonade GUI megnyitásához kattintson a Lemonade ikonra. Kattintson jobb gombbal a tálca ikonjára az alkalmazás megnyitásához. Ezután hozzáadhat modelleket, háttérrendszereket, és betöltheti az előre telepített modelleket.
<!-- @os:end -->
>**Tipp**: Az indítást követően a Lemonade GUI a http://localhost:13305 címen is elérhető

Alternatív megoldásként megnyithat egy terminált, és futtassa a `lemonade list` parancsot a telepített modellek megtekintéséhez. Ezután futtassa a következőt:
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
## A munkafolyamat beállítása

### 1. lépés: Regisztráció vagy bejelentkezés az n8n-be

Amikor először megnyitod az n8n-t, egy fiók létrehozására vagy bejelentkezésre kérnek:

1. Nyisd meg a `http://localhost:5678` címet a böngésződben
2. Hozz létre egy új helyi fiókot az e-mail címeddel, vagy jelentkezz be, ha már van fiókod
3. A bejelentkezés után megjelenik az n8n irányítópult

> **Tipp**: Ha kizártad magad a fiókodból, próbáld meg a `n8n user-management:reset` parancsot

### 2. lépés: A munkafolyamat importálása

Biztosítottunk egy előre elkészített munkafolyamatot, amelyet közvetlenül importálhatsz:

1. Töltsd le a következő munkafolyamat-fájlt: [financial-news-workflow.json](assets/financial-news-workflow.json)
2. Kattints a **Start from Scratch** gombra a munkafolyamat-szerkesztő megnyitásához. Alternatívaként kattints a bal felső sarokban található + gombra, majd válaszd az **Add workflow** lehetőséget.
3. Kattints a jobb felső sarokban lévő **...** menüre (három pont), majd válaszd az **Import from file** lehetőséget
4. Válaszd ki a letöltött `financial-news-workflow.json` fájlt
5. A munkafolyamat megjelenik a vásznon
### 3. lépés: A munkafolyamat megértése

Az importált munkafolyamat 8 összekapcsolt csomópontot tartalmaz:

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| Csomópont | Cél |
|------|---------|
| **When clicking 'Execute workflow'** | Manuális indító a munkafolyamat elindításához |
| **Fetch Financial News Feed** | RSS Read csomópont, amely az RSS-forrásból lekéri a legújabb üzleti híreket (alapértelmezés szerint az NYT Business hírcsatornát használja, API-kulcs nem szükséges) |
| **Aggregate Headlines** | Aggregate csomópont, amely minden hírcsatorna-elemből összegyűjti a címsorokat és összefoglalókat egyetlen listába |
| **Clean Extracted News Data** | Set csomópont, amely az összes címsort egyetlen szöveges mezőbe egyesíti |
| **AI Financial News Summarizer** | AI Agent, amely a híreket egy pénzügyi elemzői rendszerüzenettel dolgozza fel |
| **Lemonade Chat Model** | Kapcsolódik a helyi Lemonade szerveredhez, amelyen az LLM fut |
| **Structured Output Parser** | Az AI kimenetét strukturált JSON formátumra alakítja |
| **Convert to File** | Az összefoglalót letölthető fájllá alakítja |

> **Tipp**: Ha más hírforrást szeretnél használni, kattints duplán a **Fetch Financial News Feed** csomópontra, és cseréld ki az URL-t egy tetszőleges üzleti vagy piaci RSS-forrásra.

### 4. lépés: A Lemonade hitelesítő adatainak beállítása

Mielőtt futtatnád a munkafolyamatot, csatlakoztatnod kell a helyi Lemonade szerverhez:

1. Kattints duplán az **Lemonade Chat Model** csomópontra az n8n-ben
2. A **Credential to connect with** legördülő menüben válaszd a **Create New Credential** lehetőséget
3. Add meg az alábbi táblázatban szereplő értékeket, majd kattints a mentésre.
4. Válaszd ki a Lemonade Server-ben betöltött releváns modellt.

  | Mező | Érték |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **Megjegyzés**: Tesztelés előtt futtasd a `lemonade status` parancsot egy terminálban, hogy megerősítsd, fut a Lemonade szerver.
<!-- @device:halo_box -->
> Ez a munkafolyamat a GPT-OSS-120B modellt használja, amely előre telepítve van a Lemonade-ben. Ezt a Lemonade Chat Model csomópont beállításaiban módosíthatod más betöltött modellekre.
<!-- @device:end -->

### 5. lépés: A munkafolyamat tesztelése

1. Győződj meg róla, hogy a Lemonade fut, és be van töltve egy modell
2. Kattints az **Execute workflow** gombra a vászon alsó középső részén
3. Figyeld meg, ahogy az egyes csomópontok balról jobbra végrehajtódnak – zöldre váltanak, amikor elkészültek
4. Kattints duplán az **AI Financial News Summarizer** csomópontra, hogy megtekintsd a generált összefoglalót az alsó panelen.
5. Kattints duplán a **Convert to File** csomópontra, hogy letöltsd a megfelelő szöveges fájlt az alsó panelen.

## Az AI Agent megértése

Az AI Financial News Summarizer egy pénzügyi elemzéshez tervezett rendszerüzenetet használ:

```
You are an AI financial analyst. Your role is to read, understand, and
summarize key financial news from today. The goal is to provide investors
with a clear and concise market overview to support better investment decisions.

Investor Outlook
Today's news points to [bullish/bearish/neutral] sentiment. Watch for
[economic event/earnings report] tomorrow, which could influence market direction.
```

Az ügynök megkapja a megtisztított hírek adatait, és egy strukturált összefoglalót ad ki piaci hangulattal.

### A munkafolyamat mentése

Kattints a munkafolyamat nevére a tetején, és nevezd át, ha szeretnéd. A munkafolyamatok munka közben automatikusan mentésre kerülnek.

## Következő lépések

- **Ütemezett automatizálás**: Cseréld le a Manual Trigger-t egy **Schedule Trigger**-re, hogy naponta fusson
- **Értesítések küldése**: Adj hozzá egy **Discord**, **Slack** vagy **Email** csomópontot az összefoglalók fogadásához
- **Próbálj ki más modelleket**: Módosítsd a modellt a Lemonade Chat Model csomópontban, hogy más LLM-ekkel kísérletezhess
- **Változtasd meg a hírforrást**: Irányítsd a **Fetch Financial News Feed** csomópontot egy másik RSS-forrásra, hogy más rovatokat vagy kiadványokat kövess
- **Próbálj ki más háttérrendszereket**: Az n8n támogatja az [Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model), az LM Studio és más helyi LLM háttérrendszereket is

### n8n sablonok felfedezése

Az n8n több száz előre elkészített munkafolyamat-sablonnal rendelkezik. Böngészd a hivatalos sablonkönyvtárat itt:

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

Keress az „AI”, „LLM” vagy „automation” kifejezésekre, hogy olyan munkafolyamatokat találj, amelyeket importálhatsz és testre szabhatsz.

További információért tekintsd meg az [n8n dokumentációt](https://docs.n8n.io/).

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