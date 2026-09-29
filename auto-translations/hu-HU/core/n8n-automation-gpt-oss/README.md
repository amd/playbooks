<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Gépi fordítás.** Ez az oldal automatikusan lett lefordítva angol nyelvről, és emberi ellenőrzésen nem esett át. Hibákat tartalmazhat, és bizonyos utasítások, parancsok, letöltések, termékelérhetőség vagy egyéb tartalmak nyelvenként vagy régiónként eltérhetnek. Bármilyen eltérés vagy ellentmondás esetén a playbook eredeti angol nyelvű változata az irányadó.
<!-- auto-translated-disclaimer:end -->

# <!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Áttekintés

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Ehhez a playbookhoz minimum **32 GB** rendszermemória szükséges.
<!-- @device:end -->

Az n8n egy workflow-automatizálási platform, amellyel egy vizuális, node-alapú szerkesztő segítségével kapcsolhat össze alkalmazásokat és szolgáltatásokat.

Ez a playbook megtanítja, hogyan állítson be egy AI-alapú pénzügyi hírösszefoglalót, amely a legfrissebb üzleti híreket egy hírportál RSS-hírcsatornájából gyűjti ki, és egy a rendszerén futó helyi LLM segítségével befektetőknek szóló összefoglalót készít belőlük.

## Amit meg fog tanulni

- Az n8n telepítése és elindítása
- Előre elkészített workflow importálása és konfigurálása
- Kapcsolódás a Lemonade-hez a natív n8n integráció használatával
- A workflow node-ok és az adatáramlás megértése

## Mi az a Lemonade?

A [Lemonade](https://lemonade-server.ai) egy helyi LLM-kiszolgáló platform, amelyet AMD hardverre terveztek. Egy OpenAI-kompatibilis API-t biztosít, amely teljes egészében az Ön gépén fut – az adatai soha nem hagyják el az eszközét.

Ebben a playbookban a Lemonade-et használjuk egy helyi LLM kiszolgálására, amelyhez az n8n kapcsolódik AI-alapú feladatok elvégzéséhez.

Az n8n rendelkezik egy **natív Lemonade node-dal** (`Lemonade Chat Model`), amely elsőosztályú integrációt biztosít – nincs szükség manuális konfigurálásra. Ez egyszerűvé teszi a helyi LLM összekapcsolását az automatizálási workflow-kkal.

<!-- @device:halo_box,halo,stx,krk -->
## A memóriakonfiguráció beállítása

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Szoftverfrissítések ellenőrzése

<!-- @require:software-update -->
<!-- @device:end -->

## Szoftverelőfeltételek telepítése
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
Telepítse az n8n-t globálisan npm segítségével.

> **Megjegyzés**: Néhány npm figyelmeztetést láthat. Ez normális jelenség.

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
> **Tipp**: Windows felhasználóknak esetleg módosítaniuk kell a PowerShell Execution Policy beállítását (pl.
> RemoteSigned vagy Unrestricted értékre állítva) bizonyos PowerShell parancsok futtatása előtt.
<!-- @os:end -->


<!-- @os:windows -->
> **PATH probléma**: Ha az `n8n --version` parancs "command not found" hibát ad, győződjön meg róla, hogy az npm globális bin könyvtára szerepel a felhasználói `PATH`-ban. A szokásos telepítési útvonal a `C:\Users\<username>\AppData\Roaming\npm`.
> Adja hozzá ezt a felhasználói PATH-hoz (Rendszerkörnyezeti változók szerkesztése > Környezeti változók > Felhasználói PATH szerkesztése), majd töltse újra a terminált.

<!-- @os:end -->

<!-- @os:linux -->
Most a Podman szolgáltatást fogjuk használni az n8n telepítésének konténerizálásához.

Kérjük, töltse le a következőt egy tetszőleges könyvtárba: [compose.yml](assets/compose.yml)

Abban a könyvtárban futtassa a következő parancsot:
```bash
podman compose up -d
```

Ennek telepítenie kell az n8n-t, és írnia kell egy tartós tárolóba.

Indítsa el az n8n-t úgy, hogy beírja a `localhost:5678` címet a böngésző címsorába.
<!-- @os:end -->

<!-- @os:windows -->
## Az n8n elindítása

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
Az n8n elindít egy helyi webszervert. Nyomja meg az `'o'` billentyűt, vagy nyissa meg a böngészőjében a `http://localhost:5678` címet a szerkesztő eléréséhez.
<!-- @os:end -->


> **Tipp**: Tartsa nyitva a terminálablakot az n8n használata közben. Ha bezárja, leállhat a szerver.

## A Lemonade elindítása

A Lemonade az a helyi szerver, amely egy modellt futtat, és kapcsolódik az n8n-hez.

<!-- @os:linux -->
Nyissa meg a Lemonade GUI-t a Lemonade ikonra kattintva a tálcán. Innen böngészhet a modellek és backendek között, valamint betöltheti az előre telepített modelleket.
<!-- @os:end -->

<!-- @os:windows -->
Nyissa meg a Lemonade GUI-t a Lemonade ikonra kattintva. Kattintson jobb gombbal a tálcaikonra az alkalmazás megnyitásához. Ezután hozzáadhat modelleket, backendeket, és betöltheti az előre telepített modelleket.
<!-- @os:end -->

>**Tipp**: Miután elindult, a Lemonade GUI a http://localhost:13305 címen is elérhető

Alternatívaként megnyithat egy terminált, és futtathatja a `lemonade list` parancsot, hogy megnézze, mely modellek vannak telepítve. Ezután futtassa:

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

Amikor először megnyitja az n8n-t, arra kéri, hogy hozzon létre egy fiókot, vagy jelentkezzen be:

1. Nyissa meg a `http://localhost:5678` címet a böngészőjében
2. Hozzon létre egy új helyi fiókot az e-mail címével, vagy jelentkezzen be, ha már van fiókja
3. A bejelentkezés után megjelenik az n8n irányítópultja

> **Tipp**: Ha kizárta magát a fiókjából, próbálja meg a `n8n user-management:reset` parancsot

### 2. lépés: A workflow importálása

Biztosítottunk egy előre elkészített workflow-t, amelyet közvetlenül importálhat:

1. Töltse le a következő workflow-fájlt: [financial-news-workflow.json](assets/financial-news-workflow.json)
2. Kattintson a **Start from Scratch** gombra a workflow-szerkesztő megnyitásához. Alternatívaként kattintson a bal felső sarokban lévő + gombra, majd az **Add workflow** lehetőségre.
3. Kattintson a jobb felső sávban található **...** menüre (három pont), és válassza az **Import from file** lehetőséget
4. Válassza ki a letöltött `financial-news-workflow.json` fájlt
5. A workflow megjelenik a vásznon
### 3. lépés: A munkafolyamat megértése

Az importált munkafolyamat 8 összekapcsolt csomópontot tartalmaz:

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| Csomópont | Cél |
|------|---------|
| **When clicking 'Execute workflow'** | Manuális aktiváló a munkafolyamat elindításához |
| **Fetch Financial News Feed** | RSS Read csomópont, amely lekéri a legfrissebb üzleti híreket egy RSS-hírcsatornából (alapértelmezés szerint az NYT Business hírcsatornát használja, API-kulcs nem szükséges) |
| **Aggregate Headlines** | Aggregate csomópont, amely minden hírcsatorna-elemből egyetlen listába gyűjti a cím- és összefoglaló szövegeket |
| **Clean Extracted News Data** | Set csomópont, amely az összes hírt egyetlen szövegmezőbe egyesíti |
| **AI Financial News Summarizer** | AI Agent, amely egy pénzügyi elemző rendszerpromptal dolgozza fel a híreket |
| **Lemonade Chat Model** | Kapcsolódik a helyi Lemonade szerverhez, amelyen az LLM fut |
| **Structured Output Parser** | Strukturált JSON formátumba rendezi az AI kimenetét |
| **Convert to File** | Az összefoglalót letölthető fájllá alakítja |

> **Tipp**: Ha más hírforrást szeretne használni, kattintson duplán a **Fetch Financial News Feed** csomópontra, és cserélje ki az URL-t egy tetszőleges üzleti vagy piaci RSS-hírcsatornára.

### 4. lépés: Lemonade hitelesítő adatok beállítása

Mielőtt futtatná a munkafolyamatot, össze kell kapcsolnia a helyi Lemonade szerverrel:

1. Kattintson duplán a **Lemonade Chat Model** csomópontra az n8n-ben
2. A **Credential to connect with** legördülő menüben válassza a **Create New Credential** lehetőséget
3. Adja meg az alábbi táblázatban szereplő értékeket, majd kattintson a mentésre.
4. Válassza ki a Lemonade Server-ben betöltött megfelelő modellt.

  | Mező | Érték |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **Megjegyzés**: Tesztelés előtt futtassa a `lemonade status` parancsot egy terminálban, hogy megbizonyosodjon arról, fut-e a Lemonade szerver.
<!-- @device:halo_box -->
> Ez a munkafolyamat a GPT-OSS-120B modellt használja, amely előre telepítve van a Lemonade-ben. Ezt más, a Lemonade Chat Model csomópont beállításaiban betöltött modellekre is módosíthatja.
<!-- @device:end -->

### 5. lépés: A munkafolyamat tesztelése

1. Győződjön meg róla, hogy a Lemonade fut, és egy modell be van töltve
2. Kattintson az **Execute workflow** gombra a vászon alján középen
3. Figyelje, ahogy az egyes csomópontok balról jobbra futnak – zöldre váltanak, amikor befejeződtek
4. Kattintson duplán az **AI Financial News Summarizer** csomópontra, hogy megtekintse a generált összefoglalót az alsó panelen.
5. Kattintson duplán a **Convert to File** csomópontra, hogy letöltse a megfelelő szövegfájlt az alsó panelen.

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

Az ügynök megkapja a megtisztított hírkeret adatokat, és egy strukturált összefoglalót ad ki a piaci hangulattal együtt.

### A munkafolyamat mentése

Kattintson a munkafolyamat nevére felül, és nevezze át, ha szeretné. A munkafolyamatok automatikusan mentődnek munka közben.

## Következő lépések

- **Ütemezett automatizálás**: Cserélje le a Manual Trigger-t egy **Schedule Trigger**-re, hogy naponta fusson
- **Értesítések küldése**: Adjon hozzá egy **Discord**, **Slack** vagy **Email** csomópontot, hogy összefoglalókat kapjon
- **Más modellek kipróbálása**: Módosítsa a modellt a Lemonade Chat Model csomópontban, hogy különböző LLM-ekkel kísérletezzen
- **A hírforrás módosítása**: Irányítsa a **Fetch Financial News Feed** csomópontot egy másik RSS-hírcsatornára, hogy más rovatokat vagy kiadványokat kövessen
- **Más háttérrendszerek kipróbálása**: Az n8n a [Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model), LM Studio és más helyi LLM háttérrendszereket is támogatja

### n8n sablonok felfedezése

Az n8n több száz előre elkészített munkafolyamat-sablont kínál. Böngésszen a hivatalos sablonkönyvtárban itt:

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

Keressen az „AI”, „LLM” vagy „automation” kifejezésekre, hogy megtalálja az importálható és testreszabható munkafolyamatokat.

További információért tekintse meg az [n8n dokumentációt](https://docs.n8n.io/).

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