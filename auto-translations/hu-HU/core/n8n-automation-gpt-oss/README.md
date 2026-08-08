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

## Áttekintés

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Ehhez a playbookhoz minimum **32 GB** rendszermemória szükséges.
<!-- @device:end -->

Az n8n egy workflow-automatizálási platform, amellyel vizuális, node-alapú szerkesztő segítségével köthetsz össze alkalmazásokat és szolgáltatásokat.

Ez a playbook megtanítja, hogyan állíts be egy AI-alapú pénzügyi hírösszefoglalót, amely lekéri az AP News üzleti szekcióját, kigyűjti a legfontosabb híreket, és a rendszereden futó helyi LLM-et használja egy befektetőknek szóló összefoglaló elkészítéséhez.

## Amit meg fogsz tanulni

- Hogyan telepítsd és indítsd el az n8n-t
- Egy előre elkészített workflow importálása és konfigurálása
- Csatlakozás a Lemonade-hoz a natív n8n integráció segítségével
- A workflow node-ok és az adatáramlás megértése

## Mi az a Lemonade?

A [Lemonade](https://lemonade-server.ai) egy helyi LLM-kiszolgáló platform, amelyet kifejezetten AMD hardverekhez fejlesztettek ki. Egy OpenAI-kompatibilis API-t biztosít, amely teljes egészében a gépeden fut – az adataid soha nem hagyják el az eszközödet.

Ebben a playbookban a Lemonade-ot használjuk egy helyi LLM kiszolgálására, amelyhez az n8n csatlakozik AI-alapú feladatok végrehajtásához.

Az n8n tartalmaz egy **natív Lemonade node-ot** (`Lemonade Chat Model`), amely elsőosztályú integrációt biztosít – nincs szükség kézi konfigurációra. Ez egyszerűvé teszi a helyi LLM-ed csatlakoztatását az automatizálási workflow-khoz.

## A memóriakonfiguráció beállítása

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Szoftverfrissítések ellenőrzése

<!-- @require:software-update -->
<!-- @device:end -->

## A szoftver előfeltételeinek telepítése
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

## Az n8n telepítése
<!-- @os:windows -->
Telepítsd az n8n-t globálisan az npm segítségével.

> **Megjegyzés**: Néhány npm figyelmeztetést láthatsz. Ez normális jelenség.

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
> **Tipp**: Windows felhasználóknak szükségük lehet a PowerShell végrehajtási szabályzatának módosítására (pl.
> RemoteSigned vagy Unrestricted értékre állítva) néhány PowerShell parancs futtatása előtt.
<!-- @os:end -->


<!-- @os:windows -->
> **PATH probléma**: Ha az `n8n --version` parancsra azt a választ kapod, hogy a parancs nem található, győződj meg róla, hogy az npm globális bin könyvtára szerepel a felhasználói `PATH`-ban. A szokásos telepítési útvonal a `C:\Users\<username>\AppData\Roaming\npm`.
> Add hozzá ezt a felhasználói útvonalhoz (Rendszerkörnyezeti változók szerkesztése > Környezeti változók > Felhasználói útvonal szerkesztése), majd indítsd újra a terminált.

<!-- @os:end -->

<!-- @os:linux -->
Most a Podman szolgáltatást fogjuk használni, hogy konténerizáljuk az n8n telepítésünket.

Kérjük, töltsd le a következőt egy tetszőleges könyvtárba: [compose.yml](assets/compose.yml)

Abban a könyvtárban futtasd a következő parancsot:
```bash
podman compose up -d
```

Ennek telepítenie kell az n8n-t, és perzisztens tárolóba kell írnia.

Indítsd el az n8n-t a `localhost:5678` cím böngésződ címsorába való begépelésével.
<!-- @os:end -->

<!-- @os:windows -->
## Az n8n indítása

Indítsd el az n8n-t a terminálból:

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
Az n8n elindít egy helyi webszervert. Nyomd meg az `'o'` billentyűt, vagy nyisd meg a böngésződben a `http://localhost:5678` címet a szerkesztő eléréséhez.
<!-- @os:end -->


> **Tipp**: Hagyd nyitva a terminálablakot az n8n használata közben. Bezárása leállíthatja a szervert.

## A Lemonade indítása

A Lemonade az a helyi szerver, amely egy modellt futtat, és csatlakozik az n8n-hez.

<!-- @os:linux -->
Nyisd meg a Lemonade GUI-t a tálcán található Lemonade ikonra kattintva. Innen böngészhetsz a modellek, backendek között, és betöltheted az előre telepített modelleket.
<!-- @os:end -->

<!-- @os:windows -->
Nyisd meg a Lemonade GUI-t a Lemonade ikonra kattintva. Kattints jobb gombbal a tálcaikonra az alkalmazás megnyitásához. Ezután hozzáadhatsz modelleket, backendeket, és betöltheted az előre telepített modelleket.
<!-- @os:end -->

>**Tipp**: Futás közben a Lemonade GUI a http://localhost:13305 címen is elérhető.

Alternatívaként megnyithatsz egy terminált, és futtathatod a `lemonade list` parancsot, hogy megnézd, mely modellek vannak telepítve. Ezután futtasd:

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


## A workflow beállítása

### 1. lépés: Regisztráció vagy bejelentkezés az n8n-be

Amikor először megnyitod az n8n-t, egy fiók létrehozására vagy bejelentkezésre kérnek majd:

1. Nyisd meg a `http://localhost:5678` címet a böngésződben
2. Hozz létre egy új helyi fiókot az e-mail-címeddel, vagy jelentkezz be, ha már van fiókod
3. Bejelentkezés után megjelenik az n8n irányítópultja

> **Tipp**: Ha kizárnád magad a fiókodból, próbáld meg az `n8n user-management:reset` parancsot.

### 2. lépés: A workflow importálása

Egy előre elkészített workflow-t biztosítunk, amelyet közvetlenül importálhatsz:

1. Töltsd le a következő workflow-fájlt: [financial-news-workflow.json](assets/financial-news-workflow.json)
2. Kattints a **Start from Scratch** gombra a workflow-szerkesztő megnyitásához. Alternatívaként kattints a + gombra a bal felső sarokban, majd válaszd az **Add workflow** lehetőséget.
3. Kattints a **...** menüre (három pont) a jobb felső sávban, és válaszd az **Import from file** opciót
4. Válaszd ki a letöltött `financial-news-workflow.json` fájlt
5. A workflow megjelenik a vásznon
### 3. lépés: A munkafolyamat megértése

Az importált munkafolyamat 9 összekapcsolt csomópontot tartalmaz:

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| Csomópont | Cél |
|------|---------|
| **When clicking 'Execute workflow'** | Manuális indító a munkafolyamat elindításához |
| **Fetch Financial News Webpage** | HTTP GET kérés a következő címre: `https://apnews.com/business` |
| **Delay to Ensure Page Load** | Wait csomópont annak biztosítására, hogy az oldal tartalma teljesen betöltődjön |
| **Extract News Headlines & Text** | HTML csomópont, amely CSS-szelektorok segítségével kinyeri a szalagcímeket, a szerkesztői válogatásokat, a top híreket és a regionális híreket |
| **Clean Extracted News Data** | Set csomópont, amely az összes kinyert adatot egyetlen szövegmezőbe egyesíti |
| **AI Financial News Summarizer** | AI Agent, amely a híreket egy pénzügyi elemzői rendszerprompt alapján dolgozza fel |
| **Lemonade Chat Model** | Csatlakozik a helyi Lemonade szerverhez, amelyen az LLM fut |
| **Structured Output Parser** | Az AI kimenetét strukturált JSON formátumra alakítja |
| **Convert to File** | Az összefoglalót letölthető fájllá alakítja |

### 4. lépés: A Lemonade hitelesítő adatainak beállítása

Mielőtt futtatnád a munkafolyamatot, csatlakoztatnod kell a helyi Lemonade szerverhez:

1. Kattints duplán a **Lemonade Chat Model** csomópontra az n8n-ben
2. A **Credential to connect with** legördülő menüben válaszd a **Create New Credential** lehetőséget
3. Add meg az alábbi táblázatban szereplő értékeket, majd kattints a mentésre.
4. Válaszd ki a megfelelő modellt, amelyet betöltöttél a Lemonade Server-en.

  | Mező | Érték |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **Megjegyzés**: Tesztelés előtt futtasd a `lemonade status` parancsot egy terminálban, hogy megbizonyosodj arról, hogy a Lemonade szerver fut.
<!-- @device:halo_box -->
> Ez a munkafolyamat a GPT-OSS-120B modellt használja, amely előre telepítve van a Lemonade-ben. Ezt módosíthatod más, betöltött modellekre a Lemonade Chat Model csomópont beállításaiban.
<!-- @device:end -->

### 5. lépés: A munkafolyamat tesztelése

1. Győződj meg róla, hogy a Lemonade fut, és egy modell be van töltve
2. Kattints az **Execute workflow** gombra a vászon alsó közepén
3. Figyeld meg, ahogy az egyes csomópontok balról jobbra sorban lefutnak — készültükkor zöldre váltanak
4. Kattints duplán az **AI Financial News Summarizer** csomópontra, hogy megtekintsd a generált összefoglalót az alsó panelen.
5. Kattints duplán a **Convert to File** csomópontra, hogy letöltsd a megfelelő szövegfájlt az alsó panelen.

## Az AI Agent megértése

Az AI Financial News Summarizer egy pénzügyi elemzésre tervezett rendszerpromptot használ:

```
You are an AI financial analyst. Your role is to read, understand, and
summarize key financial news from today. The goal is to provide investors
with a clear and concise market overview to support better investment decisions.

Investor Outlook
Today's news points to [bullish/bearish/neutral] sentiment. Watch for
[economic event/earnings report] tomorrow, which could influence market direction.
```

Az ügynök megkapja a megtisztított hírdadatokat, és egy strukturált összefoglalót ad ki a piaci hangulattal együtt.

### A munkafolyamat mentése

Kattints a munkafolyamat nevére a tetején, és nevezd át, ha szeretnéd. A munkafolyamatok automatikusan mentődnek, ahogy dolgozol.

## Következő lépések

- **Automatizálás ütemezése**: Cseréld le a Manual Trigger csomópontot egy **Schedule Trigger** csomópontra, hogy naponta fusson
- **Értesítések küldése**: Adj hozzá egy **Discord**, **Slack** vagy **Email** csomópontot, hogy megkapd az összefoglalókat
- **Próbálj ki más modelleket**: Módosítsd a modellt a Lemonade Chat Model csomópontban, hogy különböző LLM-ekkel kísérletezz
- **Kinyerés testreszabása**: Módosítsd a HTML Extract csomópont CSS-szelektorait, hogy más hírrészekre célozz
- **Próbálj ki más háttérrendszereket**: Az n8n emellett támogatja az [Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model), az LM Studio és más helyi LLM háttérrendszereket

### n8n sablonok felfedezése

Az n8n számos előre elkészített munkafolyamat-sablonnal rendelkezik. Böngészd a hivatalos sablonkönyvtárat itt:

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

Keress rá az „AI”, „LLM” vagy „automatizálás” kifejezésekre, hogy olyan munkafolyamatokat találj, amelyeket importálhatsz és testreszabhatsz.

További információért nézd meg az [n8n dokumentációját](https://docs.n8n.io/).

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