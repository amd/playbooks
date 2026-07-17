<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Ez a playbook speciális tageket használ, amelyeket a GitHub nem tud megjeleníteni. A tartalom helyes előnézetéhez látogasson el az [amd.com/playbooks](https://amd.com/playbooks) oldalra.
<!-- @github-only:end -->

## Áttekintés

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Ez a playbook legalább **32 GB** rendszermemóriát igényel.
<!-- @device:end -->

Az n8n egy munkafolyamat-automatizálási platform, amely lehetővé teszi alkalmazások és szolgáltatások összekapcsolását egy vizuális, csomópontalapú szerkesztővel.

Ez a playbook megtanítja, hogyan állítson be egy mesterséges intelligencia által vezérelt pénzügyi hírek összefoglalóját, amely lekéri az AP News üzleti rovatát, kinyeri a legfontosabb főcímeket, és a rendszeren futó helyi LLM segítségével befektetőknek szóló összefoglalót készít.

## Mit fog megtanulni

- Hogyan telepítse és indítsa el az n8n-t
- Előre elkészített munkafolyamat importálása és konfigurálása
- Csatlakozás a Lemonade-hez a natív n8n integráción keresztül
- A munkafolyamat csomópontjainak és az adatáramlásnak a megértése

## Mi az a Lemonade?

A [Lemonade](https://lemonade-server.ai) egy helyi LLM kiszolgáló platform, amelyet AMD hardverhez fejlesztettek. OpenAI-kompatibilis API-t biztosít, amely teljes egészében a gépen fut – az adatok soha nem hagyják el az eszközt.

Ebben a playbookban a Lemonade-et egy helyi LLM kiszolgálására használjuk, amelyhez az n8n csatlakozik mesterséges intelligencia által vezérelt feladatokhoz.

Az n8n tartalmaz egy **natív Lemonade csomópontot** (`Lemonade Chat Model`), amely elsőrangú integrációt biztosít – nincs szükség manuális konfigurációra. Ez egyszerűvé teszi a helyi LLM csatlakoztatását az automatizálási munkafolyamatokhoz.

## A memóriakonfiguráció beállítása

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Szoftverfrissítések ellenőrzése

<!-- @require:software-update -->
<!-- @device:end -->

## Szoftver-előfeltételek telepítése
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
Telepítse az n8n-t globálisan az npm segítségével.

> **Megjegyzés**: Előfordulhat, hogy néhány npm figyelmeztetést lát. Ez várható.

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
> **Tipp**: A Windows-felhasználóknak előfordulhat, hogy módosítaniuk kell a PowerShell végrehajtási házirendjét (pl.
> RemoteSigned vagy Unrestricted értékre állítva) egyes PowerShell-parancsok futtatása előtt.
<!-- @os:end -->


<!-- @os:windows -->
> **PATH-probléma**: Ha az `n8n --version` azt jelzi, hogy a parancs nem található, győződjön meg arról, hogy az npm globális bin könyvtára szerepel a felhasználói `PATH`-ban. A szokásos telepítési útvonal: `C:\Users\<username>\AppData\Roaming\npm`. 
> Adja hozzá ezt a felhasználói útvonalhoz (Rendszerkörnyezeti változók szerkesztése > Környezeti változók > Felhasználói útvonal szerkesztése), majd töltse újra a terminált.

<!-- @os:end -->

<!-- @os:linux -->
Most a Podman szolgáltatást fogjuk használni az n8n telepítésünk konténerizálásához.

Töltse le a következőt egy tetszőleges könyvtárba: [compose.yml](assets/compose.yml)

Abban a könyvtárban futtassa a következő parancsot:
```bash
podman compose up -d
```

Ez telepíti az n8n-t, és tartós tárolóba ír.

Indítsa el az n8n-t úgy, hogy beírja a `localhost:5678` címet a böngésző címsorába.
<!-- @os:end -->

<!-- @os:windows -->
## Az n8n indítása

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
Az n8n elindít egy helyi webszervert. Nyomja meg a `'o'` billentyűt, vagy nyissa meg a böngészőben a `http://localhost:5678` címet a szerkesztő eléréséhez.
<!-- @os:end -->


> **Tipp**: Tartsa nyitva a terminálablakot az n8n használata közben. Bezárása leállíthatja a szervert.

## A Lemonade indítása

A Lemonade az a helyi szerver, amely futtatja a modellt és csatlakozik az n8n-hez.

<!-- @os:linux -->
Nyissa meg a Lemonade grafikus felületét a tálcán lévő Lemonade ikonra kattintva. Innen böngészhet modellek és háttérrendszerek között, valamint betöltheti az előre telepített modelleket.
<!-- @os:end -->

<!-- @os:windows -->
Nyissa meg a Lemonade grafikus felületét a Lemonade ikonra kattintva. Jobb gombbal kattintson a tálcaikonra az alkalmazás megnyitásához. Ezután modelleket, háttérrendszereket adhat hozzá, és betöltheti az előre telepített modelleket.
<!-- @os:end -->

>**Tipp**: Futás után a Lemonade grafikus felülete a http://localhost:13305 címen is elérhető.

Alternatívaként nyisson meg egy terminált, és futtassa a `lemonade list` parancsot a telepített modellek megtekintéséhez. Ezután futtassa:

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

Amikor először nyitja meg az n8n-t, a rendszer felkéri fiók létrehozására vagy bejelentkezésre:

1. Nyissa meg a `http://localhost:5678` címet a böngészőben
2. Hozzon létre egy új helyi fiókot az e-mail-címével, vagy jelentkezzen be, ha már van fiókja
3. Bejelentkezés után megjelenik az n8n irányítópultja

> **Tipp**: Ha ki van zárva a fiókjából, próbálja meg az `n8n user-management:reset` parancsot

### 2. lépés: A munkafolyamat importálása

Biztosítottunk egy előre elkészített munkafolyamatot, amelyet közvetlenül importálhat:

1. Töltse le a következő munkafolyamat-fájlt: [financial-news-workflow.json](assets/financial-news-workflow.json)
2. Kattintson a **Start from Scratch** gombra a munkafolyamat-szerkesztő megnyitásához. Alternatívaként kattintson a + gombra a bal felső sarokban, majd az **Add workflow** lehetőségre.
3. Kattintson a jobb felső sávban lévő **...** menüre (három pont), és válassza az **Import from file** lehetőséget
4. Válassza ki a letöltött `financial-news-workflow.json` fájlt
5. A munkafolyamat megjelenik a vásznon


### 3. lépés: A munkafolyamat megértése

Az importált munkafolyamat 9 összekapcsolt csomópontot tartalmaz:

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| Csomópont | Cél |
|------|---------|
| **When clicking 'Execute workflow'** | Manuális indítás a munkafolyamat elindításához |
| **Fetch Financial News Webpage** | HTTP GET kérés a `https://apnews.com/business` címre |
| **Delay to Ensure Page Load** | Várakozási csomópont az oldaltartalom teljes betöltésének biztosítására |
| **Extract News Headlines & Text** | HTML csomópont, amely CSS-szelektorok segítségével kinyeri a főcímeket, szerkesztői válogatásokat, kiemelt híreket és regionális híreket |
| **Clean Extracted News Data** | Set csomópont, amely az összes kinyert adatot egyetlen szövegmezőbe kombinálja |
| **AI Financial News Summarizer** | AI-ügynök, amely pénzügyi elemző rendszerprompttal dolgozza fel a híreket |
| **Lemonade Chat Model** | Csatlakozik a helyi Lemonade szerverhez, amely az LLM-et futtatja |
| **Structured Output Parser** | Az AI kimenetét strukturált JSON formátumba alakítja |
| **Convert to File** | Az összefoglalót letölthető fájllá alakítja |

### 4. lépés: A Lemonade hitelesítő adatok konfigurálása

A munkafolyamat futtatása előtt csatlakoztatnia kell a helyi Lemonade szerverhez:

1. Kattintson duplán az n8n-ben lévő **Lemonade Chat Model** csomópontra
2. A **Credential to connect with** legördülő menüben válassza a **Create New Credential** lehetőséget
3. Adja meg az alábbi táblázatban szereplő értékeket, majd kattintson a mentés gombra.
4. Válassza ki a Lemonade Serverben betöltött megfelelő modellt.

  | Mező | Érték |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **Megjegyzés**: A tesztelés előtt futtassa a `lemonade status` parancsot egy terminálban annak megerősítéséhez, hogy a Lemonade szerver fut.
<!-- @device:halo_box -->
> Ez a munkafolyamat a GPT-OSS-120B modellt használja, amely előre telepítve van a Lemonade-ben. Ezt más betöltött modellekre is módosíthatja a Lemonade Chat Model csomópont beállításaiban.
<!-- @device:end -->

### 5. lépés: A munkafolyamat tesztelése

1. Győződjön meg arról, hogy a Lemonade fut és egy modell be van töltve
2. Kattintson az **Execute workflow** gombra a vászon alsó közepén
3. Figyelje meg, ahogy az egyes csomópontok balról jobbra hajtódnak végre – befejezéskor zöldre váltanak
4. Kattintson duplán az **AI Financial News Summarizer** csomópontra az alsó panelen megjelenő generált összefoglaló megtekintéséhez.
5. Kattintson duplán a **Convert to File** csomópontra a megfelelő szövegfájl letöltéséhez az alsó panelről.

## Az AI-ügynök megértése

Az AI Financial News Summarizer egy pénzügyi elemzésre tervezett rendszerpromptot használ:

```
You are an AI financial analyst. Your role is to read, understand, and
summarize key financial news from today. The goal is to provide investors
with a clear and concise market overview to support better investment decisions.

Investor Outlook
Today's news points to [bullish/bearish/neutral] sentiment. Watch for
[economic event/earnings report] tomorrow, which could influence market direction.
```

Az ügynök megkapja a megtisztított híradatokat, és strukturált összefoglalót ad ki piaci hangulattal együtt.

### A munkafolyamat mentése

Kattintson a munkafolyamat nevére a tetején, és nevezze át, ha kívánja. A munkafolyamatok automatikusan mentődnek munka közben.

## Következő lépések

- **Ütemezett automatizálás**: Cserélje le a manuális indítót egy **Schedule Trigger**-re a napi futtatáshoz
- **Értesítések küldése**: Adjon hozzá egy **Discord**, **Slack** vagy **Email** csomópontot az összefoglalók fogadásához
- **Különböző modellek kipróbálása**: Módosítsa a modellt a Lemonade Chat Model csomópontban, hogy különböző LLM-ekkel kísérletezzen
- **Kinyerés testreszabása**: Módosítsa a HTML Extract csomópont CSS-szelektorait különböző hírszekciókat célozva
- **Különböző háttérrendszerek kipróbálása**: Az n8n támogatja az [Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model), LM Studio és más helyi LLM háttérrendszereket is

### n8n sablonok felfedezése

Az n8n több száz előre elkészített munkafolyamat-sablonnal rendelkezik. Böngésszen a hivatalos sablonkönyvtárban:

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

Keressen rá az „AI", „LLM" vagy „automation" kifejezésekre, hogy importálható és testreszabható munkafolyamatokat találjon.

További információkért tekintse meg az [n8n dokumentációját](https://docs.n8n.io/).