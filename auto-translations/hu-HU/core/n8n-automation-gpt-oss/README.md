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
> Ehhez a playbookhoz legalább **32GB** rendszermemória szükséges.
<!-- @device:end -->

Az n8n egy munkafolyamat-automatizálási platform, amellyel vizuális, csomópont-alapú szerkesztő segítségével köthetsz össze alkalmazásokat és szolgáltatásokat.

Ez a playbook megtanítja, hogyan állíts be egy AI-alapú pénzügyi hírösszefoglalót, amely a legfrissebb üzleti híreket egy hír RSS-feedből gyűjti, és egy a rendszereden futó helyi LLM segítségével befektetőknek szóló összefoglalót készít.

## Mit fogsz tanulni

- Az n8n telepítését és elindítását
- Egy előre elkészített munkafolyamat importálását és konfigurálását
- A Lemonade-hez való kapcsolódást a natív n8n integráció használatával
- A munkafolyamat csomópontjainak és az adatfolyamnak a megértését

## Mi az a Lemonade?

A [Lemonade](https://lemonade-server.ai) egy helyi LLM-kiszolgáló platform, amelyet AMD hardverhez fejlesztettek. Egy OpenAI-kompatibilis API-t biztosít, amely teljes egészében a saját gépeden fut – az adataid soha nem hagyják el az eszközödet.

Ebben a playbookban a Lemonade-et használjuk egy helyi LLM kiszolgálására, amelyhez az n8n csatlakozik AI-alapú feladatokhoz. 

Az n8n tartalmaz egy **natív Lemonade csomópontot** (`Lemonade Chat Model`), amely elsőrangú integrációt biztosít – nincs szükség manuális konfigurációra. Ez egyszerűvé teszi a helyi LLM csatlakoztatását az automatizálási munkafolyamatokhoz.

<!-- @device:halo_box,halo,stx,krk -->
## A memóriakonfiguráció beállítása

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Szoftverfrissítések ellenőrzése

<!-- @require:software-update -->
<!-- @device:end -->

## Szoftver-előfeltételek telepítése
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

## Az n8n telepítése
<!-- @os:windows -->
Telepítsd az n8n-t globálisan npm segítségével.

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
> **Tipp**: Windows felhasználóknak esetleg módosítaniuk kell a PowerShell futtatási szabályzatát (Execution Policy) (pl.
> RemoteSigned vagy Unrestricted értékre állítva), mielőtt egyes Powershell parancsokat futtatnának.
<!-- @os:end -->


<!-- @os:windows -->
> **PATH probléma**: Ha az `n8n --version` parancsra azt a választ kapod, hogy a parancs nem található, győződj meg róla, hogy az npm globális bin könyvtára szerepel a felhasználói `PATH`-ban. A szokásos telepítési útvonal itt található: `C:\Users\<username>\AppData\Roaming\npm`. 
> Add hozzá ezt a felhasználói elérési úthoz (Rendszer környezeti változóinak szerkesztése > Környezeti változók > Felhasználói elérési út szerkesztése), majd töltsd újra a terminált. 

<!-- @os:end -->

<!-- @os:linux -->
Most a Podman szolgáltatást fogjuk használni az n8n telepítésünk konténerizálásához.

Kérjük, töltsd le a következőt egy tetszőleges könyvtárba: [compose.yml](assets/compose.yml)

Abban a könyvtárban futtasd a következő parancsot:
```bash
podman compose up -d
```

Ennek telepítenie kell az n8n-t, és írnia kell egy perzisztens tárhelyre.

Indítsd el az n8n-t a böngésző címsorába beírva: `localhost:5678`.
<!-- @os:end -->

<!-- @os:windows -->
## Az n8n elindítása

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
Az n8n elindít egy helyi webkiszolgálót. Nyomd meg az `'o'` billentyűt, vagy nyisd meg a böngésződben a `http://localhost:5678` címet a szerkesztő eléréséhez.
<!-- @os:end -->


> **Tipp**: Az n8n használata közben hagyd nyitva a terminál ablakot. Ha bezárod, az leállíthatja a szervert.

## A Lemonade elindítása

A Lemonade az a helyi szerver, amely egy modellt futtat, és csatlakozik az n8n-hez. 

<!-- @os:linux -->
Nyisd meg a Lemonade GUI-t a tálcán található Lemonade ikonra kattintva. Innen böngészhetsz a modellek és háttérrendszerek (backends) között, és betöltheted az előre telepített modelleket.
<!-- @os:end -->

<!-- @os:windows -->
Nyisd meg a Lemonade GUI-t a Lemonade ikonra kattintva. Kattints jobb gombbal a tálcaikonra az alkalmazás megnyitásához. Ezután hozzáadhatsz modelleket, háttérrendszereket, és betöltheted az előre telepített modelleket.
<!-- @os:end -->

>**Tipp**: Ha fut, a Lemonade GUI a http://localhost:13305 címen is elérhető.

Alternatív megoldásként nyiss meg egy terminált, és futtasd a `lemonade list` parancsot, hogy megnézd, milyen modellek vannak telepítve. Ezután futtasd:

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

> **Tipp**: Ha kizárod magad a fiókodból, próbáld ki az `n8n user-management:reset` parancsot.

### 2. lépés: A munkafolyamat importálása

Egy előre elkészített munkafolyamatot biztosítottunk, amelyet közvetlenül importálhatsz:

1. Töltsd le a következő munkafolyamat-fájlt: [financial-news-workflow.json](assets/financial-news-workflow.json)
2. Kattints a **Start from Scratch** gombra a munkafolyamat-szerkesztő megnyitásához. Alternatívaként kattints a + gombra a bal felső sarokban, majd az **Add workflow** opcióra.
3. Kattints a **...** menüre (három pont) a jobb felső sávban, és válaszd az **Import from file** lehetőséget
4. Válaszd ki a letöltött `financial-news-workflow.json` fájlt
5. A munkafolyamat megjelenik a vásznon
### 3. lépés: A munkafolyamat megértése

Az importált munkafolyamat 8 összekapcsolt csomópontot tartalmaz:

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| Csomópont | Cél |
|------|---------|
| **When clicking 'Execute workflow'** | Manuális trigger a munkafolyamat elindításához |
| **Fetch Financial News Feed** | RSS Read csomópont, amely lekéri a legfrissebb üzleti híreket egy RSS-hírforrásból (alapértelmezés szerint az NYT Business hírforrást használja, nem igényel API-kulcsot) |
| **Aggregate Headlines** | Aggregate csomópont, amely összegyűjti a híreket és összefoglalókat minden hírforrás-elemből egyetlen listába |
| **Clean Extracted News Data** | Set csomópont, amely az összes hírt egyetlen szöveges mezőbe egyesíti |
| **AI Financial News Summarizer** | AI Agent, amely a híreket egy pénzügyi elemző rendszerprompt alapján dolgozza fel |
| **Lemonade Chat Model** | Kapcsolódik a helyi Lemonade szerverhez, amely az LLM-et futtatja |
| **Structured Output Parser** | Strukturált JSON formátumra alakítja az AI kimenetét |
| **Convert to File** | Letölthető fájllá alakítja az összefoglalót |

> **Tipp**: Ha más hírforrást szeretne használni, kattintson duplán a **Fetch Financial News Feed** csomópontra, és cserélje le az URL-t egy tetszőleges üzleti vagy piaci RSS-hírforrásra.

### 4. lépés: A Lemonade hitelesítő adatok konfigurálása

Mielőtt futtatná a munkafolyamatot, csatlakoztatnia kell a helyi Lemonade szerverhez:

1. Kattintson duplán a **Lemonade Chat Model** csomópontra az n8n-ben
2. A **Credential to connect with** legördülő menüben válassza a **Create New Credential** opciót
3. Adja meg az alábbi táblázatban szereplő értékeket, és kattintson a mentésre.
4. Válassza ki a Lemonade Server-ben betöltött megfelelő modellt.

  | Mező | Érték |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **Megjegyzés**: Tesztelés előtt futtassa a `lemonade status` parancsot egy terminálban, hogy megerősítse a Lemonade szerver futását.
<!-- @device:halo_box -->
> Ez a munkafolyamat a GPT-OSS-120B modellt használja, amely előre telepítve van a Lemonade-ben. Ezt más, betöltött modellekre is módosíthatja a Lemonade Chat Model csomópont beállításaiban.
<!-- @device:end -->

### 5. lépés: A munkafolyamat tesztelése

1. Győződjön meg róla, hogy a Lemonade fut, és egy modell be van töltve
2. Kattintson az **Execute workflow** gombra a vászon alján, középen
3. Figyelje meg, ahogy minden csomópont balról jobbra lefut – zöldre váltanak, amikor elkészültek
4. Kattintson duplán az **AI Financial News Summarizer** csomópontra, hogy megtekinthesse a generált összefoglalót az alsó panelen.
5. Kattintson duplán a **Convert to File** csomópontra, hogy letöltse a megfelelő szöveges fájlt az alsó panelen.

## Az AI Agent megértése

Az AI Financial News Summarizer egy pénzügyi elemzéshez tervezett rendszerpromptot használ:

```
You are an AI financial analyst. Your role is to read, understand, and
summarize key financial news from today. The goal is to provide investors
with a clear and concise market overview to support better investment decisions.

Investor Outlook
Today's news points to [bullish/bearish/neutral] sentiment. Watch for
[economic event/earnings report] tomorrow, which could influence market direction.
```

Az ügynök megkapja a megtisztított hírdatokat, és egy strukturált összefoglalót ad ki a piaci hangulattal együtt.

### A munkafolyamat mentése

Kattintson a munkafolyamat nevére a tetején, és nevezze át, ha szeretné. A munkafolyamatok automatikusan mentésre kerülnek munka közben.

## Következő lépések

- **Automatizálás ütemezése**: Cserélje le a Manual Trigger-t egy **Schedule Trigger**-re, hogy naponta fusson
- **Értesítések küldése**: Adjon hozzá egy **Discord**, **Slack**, vagy **Email** csomópontot, hogy összefoglalókat kapjon
- **Próbáljon ki más modelleket**: Módosítsa a modellt a Lemonade Chat Model csomópontban, hogy különböző LLM-ekkel kísérletezzen
- **Hírforrás módosítása**: Irányítsa a **Fetch Financial News Feed** csomópontot egy másik RSS-hírforrásra, hogy más rovatokat vagy kiadványokat kövessen
- **Próbáljon ki más háttérrendszereket**: Az n8n támogatja az [Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model), LM Studio és más helyi LLM háttérrendszereket is

### n8n sablonok felfedezése

Az n8n több száz előre elkészített munkafolyamat-sablonnal rendelkezik. Böngéssze a hivatalos sablonkönyvtárat itt:

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

Keressen rá az "AI", "LLM" vagy "automation" kifejezésekre, hogy olyan munkafolyamatokat találjon, amelyeket importálhat és testre szabhat.

További információkért tekintse meg az [n8n dokumentációját](https://docs.n8n.io/).

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