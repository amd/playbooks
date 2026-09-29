<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Gépi fordítás.** Ez az oldal automatikusan lett lefordítva angol nyelvről, és emberi ellenőrzésen nem esett át. Hibákat tartalmazhat, és bizonyos utasítások, parancsok, letöltések, termékelérhetőség vagy egyéb tartalmak nyelvenként vagy régiónként eltérhetnek. Bármilyen eltérés vagy ellentmondás esetén a playbook eredeti angol nyelvű változata az irányadó.
<!-- auto-translated-disclaimer:end -->

# Hermes Agent futtatása helyben a Lemonade Server segítségével

## Áttekintés

A [**Hermes Agent**](https://hermes-agent.nousresearch.com/) egy önfejlesztő AI-ügynök, amelyet a Nous Research fejlesztett. Beépített tanulási hurokkal rendelkezik, tapasztalatokból épít fel képességeket, munkameneteken átívelő állandó memóriát épít arról, hogy ki vagy, és a nevedben ütemezett automatizálásokat is futtathat. Egy egyszerű csevegőasszisztenssel ellentétben a Hermes valódi cselekvéseket hajt végre: shell parancsokat futtat, fájlokat ír, böngészi a webet, és párhuzamos munkafolyamatokat delegál alügynökök számára.

A [**Lemonade Server**](https://lemonade-server.ai/) az a helyi következtetési háttérrendszer, amely mindezt működteti. Ez egy nyílt forráskódú szerver, amely közvetlenül az AMD hardvereden futtatja a GenAI modelleket, és az iparági szabványnak számító OpenAI API-n keresztül teszi őket elérhetővé.

Együtt egy teljesen helyi AI-ügynök-stacket alkotnak: a Lemonade a modell-következtetést kezeli a GPU-n, a Hermes pedig biztosítja az ügynökhurkot, a memóriát, a képességeket és az üzenetküldő átjárót.

> **Mielőtt folytatnád:** A Hermes Agent egy nagymértékben autonóm AI-ügynök. Ha bármilyen AI-ügynöknek hozzáférést adsz a rendszeredhez, az kiszámíthatatlan vagy nem szándékolt eredményekhez vezethet. Csak akkor folytasd, ha megérted a kockázatokat, és elfogadod, hogy autonóm szoftver cselekszik a nevedben.

---

## Mit fogsz megtanulni

Ennek az útmutatónak a végére képes leszel:

- **Telepíteni a Hermes Agentet**, és beállítani, hogy a **Lemonade Servert** használja AI háttérrendszerként.
- **(Ajánlott) Engedélyezni a Docker/Podman homokozó (sandboxing) funkciót**, hogy elkülönítsd az ügynök tevékenységeit a gazdagéptől.
- **Elindítani a Hermes átjárót (gateway)**, és megerősíteni, hogy az ügynököd készen áll.
- **Csatlakoztatni egy kommunikációs csatornát** (Discord vagy Telegram), hogy bármilyen eszközről cseveghess az ügynököddel.

---

<!-- @device:halo_box,halo,stx,krk -->
## Memóriakonfiguráció beállítása

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Szoftverfrissítések ellenőrzése

<!-- @require:software-update -->
<!-- @device:end -->

## Szoftveres előfeltételek telepítése

<!-- @os:linux -->
- Egy **Ubuntu 24.04+**-t vagy egy kompatibilis, `apt-get`-et használó Debian-alapú Linux disztribúciót futtató PC
- Legalább **12 GB RAM** (nagyobb modellekhez 64 GB+ ajánlott)
- **~10–30 GB szabad lemezterület** a modellsúlyokhoz
- [Podman](https://podman.io/docs/installation) (opcionális, a Hermes Agent homokozózásához)
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @os:windows -->
- Egy **Windows 10/11**-et futtató PC
- Legalább **12 GB RAM** (nagyobb modellekhez 64 GB+ ajánlott)
- **~10–30 GB szabad lemezterület** a modellsúlyokhoz
- Podman (opcionális, a Hermes Agent homokozózásához). Telepítsd a WSL-en belül:
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @device:halo_box -->
> A Podman előre telepítve van a Halo Box-on, nincs szükség beállításra
<!-- @device:end -->

<!-- @require:lemonade -->

<!-- @var:id=hermes_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Az ajánlott modell letöltése és betöltése

Ehhez az útmutatóhoz az ajánlott modell a **Qwen3.6-35B-A3B-GGUF** az Unsloth-tól, egy erős MoE modell 263k tokenes kontextusablakkal, amely kiválóan alkalmas ügynöki feladatokra. Ez a modell UD-Q4_K_XL kvantálást használ. Töltsd le most:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Ezután töltsd be nagy kontextusablakkal, és mentsd el ezt a beállítást a jövőbeli futtatásokhoz:

<!-- @require:lemonade-ready -->
<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end -->

A modell alapértelmezett kontextushossza 262 144 token. Ha memóriafogyás (OOM) hibákat tapasztalsz, fontold meg a kontextusablak csökkentését.

> **Tipp: A gondolkodás kikapcsolása gyorsabb ügynökválaszokért:** A Qwen3.6-35B-A3B alapértelmezés szerint gondolkodási módban fut, ami minden válasz előtt késleltetést okoz. Ügynökhurkok esetén ez a többletidő gyorsan felhalmozódik. A [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) tárolóban található egy előre elkészített konfiguráció, amely kikapcsolja a gondolkodást. A használatához töltsd le a fájlt, majd importáld:
>
> ```bash
> curl -LO https://raw.githubusercontent.com/lemonade-sdk/recipes/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json
> lemonade import Qwen3.6-35B-A3B-NoThinking.json
> ```

---

<!-- @os:windows -->
<!-- @test:id=lemonade-chat-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$modelsJson = $null
for ($i = 0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}

if (-not $modelsJson) {throw "Lemonade server not ready on http://127.0.0.1:13305"}
Write-Host "OK: Lemonade server is responding"

$parsed = $modelsJson | ConvertFrom-Json
$entry = $parsed.data | Where-Object { $_.id -eq "${hermes_model}" } | Select-Object -First 1

if (-not $entry) {throw "Model ${hermes_model} is not present in Lemonade /api/v1/models."}
if (-not $entry.downloaded) {throw "Model ${hermes_model} is present but not downloaded in Lemonade. Please download it before running CI."}
Write-Host "OK: ${hermes_model} model is downloaded in Lemonade"

if ($entry.recipe_options.ctx_size -ne 262144) {
  throw "Model ${hermes_model} is not saved with ctx_size=262144. Run: lemonade load ${hermes_model} --ctx-size 262144 --save-options"
}
Write-Host "OK: ${hermes_model} is saved with ctx_size=262144"

$body = @{
  model = "${hermes_model}"
  messages = @(
    @{
      role = "user"
      content = "Reply with exactly: OK"
    }
  )
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "hermes-lemonade-chat-body.json"
[System.IO.File]::WriteAllText($tmpBody, $body, [System.Text.UTF8Encoding]::new($false))

try {
  $out = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpBody"
  if (-not $out) {throw "Empty response from Lemonade chat/completions"}
  Write-Host "OK: Lemonade chat/completions returned a response"
}
finally {
  Remove-Item $tmpBody -Force -ErrorAction SilentlyContinue
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
model_id = "${hermes_model}"

entry = None
for item in data.get("data", []):
    if item.get("id") == model_id:
        entry = item
        break

if entry is None:
    print(f"Model {model_id} is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print(f"Model {model_id} is present but not downloaded in Lemonade. Please download it before running CI.")
    sys.exit(1)

print(f"OK: {model_id} model is downloaded in Lemonade")

ctx_size = entry.get("recipe_options", {}).get("ctx_size")
if ctx_size != 262144:
    print(f"Model {model_id} is not saved with ctx_size=262144. Run: lemonade load {model_id} --ctx-size 262144 --save-options")
    sys.exit(1)
print(f"OK: {model_id} is saved with ctx_size=262144")
PY

body='{
  "model": "${hermes_model}",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 32
}'

out="$(curl -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body")"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi

echo "OK: Lemonade chat/completions returned a response"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->

## WSL beállítása

A Hermes Agentet a WSL-en belül futtatjuk, és a natívan Windows alatt futó Lemonade-hoz csatlakoztatjuk. Ez Linux shell környezetet biztosít a Hermes számára, miközben a Lemonade GPU-gyorsítása a Windows oldalon marad.

### A WSL és az Ubuntu telepítése

Nyisd meg a PowerShellt rendszergazdaként, és telepítsd a WSL kernelt:

```powershell
wsl --install --no-distribution
```

Ezután telepítsd az Ubuntut:

```powershell
wsl --install -d Ubuntu-24.04
```

### A systemd engedélyezése WSL-ben

Futtasd ezt az Ubuntu terminálban:

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

Indítsd újra a WSL-t:

```powershell
wsl --shutdown
wsl
```

### A Lemonade áthidalása Windowsból WSL-be

A WSL2 egy virtuális hálózatban fut. A Lemonade Windows alatt a `127.0.0.1` címhez kapcsolódik, amelyet a WSL nem tud közvetlenül elérni. Egy Windows portproxy továbbítja a forgalmat a WSL átjáró IP-címéről a Windows localhostra.

**Keresd meg a WSL átjáró IP-címét** (futtasd a WSL-en belül):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Add hozzá a portproxyt** (futtasd PowerShellben rendszergazdaként, cserélve a `<WSL-Gateway-IP>` értéket a saját WSL átjáró IP-címedre):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**Adj hozzá egy tűzfalszabályt** (ugyanabban az emelt jogosultságú PowerShellben):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Ellenőrizd WSL-ből**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Ha az előző lépésben már betöltötted a Qwen3.6-35B-A3B-GGUF modellt, akkor a betöltött modelledet felsoroló JSON kimenetet kell látnod.

```json
{
  "data": [
    {
      "checkpoint": "unsloth/Qwen3.6-35B-A3B-GGUF:UD-Q4_K_XL",
      "checkpoints": {
        "main": "unsloth/Qwen3.6-35B-A3B-GGUF:UD-Q4_K_XL"
      },
      "mmproj": "unsloth/Qwen3.6-35B-A3B-GGUF:mmproj-F16.gguf",
      ....
    }
  ],
  "object": "list"
}
```

> A `netsh portproxy` szabály túléli az újraindításokat, de a WSL átjáró IP-címe megváltozhat a `wsl --shutdown` után. Ha a Lemonade újraindítás után elérhetetlenné válik WSL-ből, kérd le a frissített átjáró IP-címet, és frissítsd a proxyt ezzel az új címmel.

<!-- @test:id=wsl-lemonade-bridge-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
WINDOWS_HOST="$(ip route show default | awk '{print $3}' | head -1)"

if [ -z "$WINDOWS_HOST" ]; then
  echo "Could not determine WSL gateway IP"
  exit 1
fi

echo "WSL gateway IP: $WINDOWS_HOST"

models_json="$(curl -fsS --max-time 5 "http://$WINDOWS_HOST:13305/api/v1/models")"

if [ -z "$models_json" ]; then
  echo "Could not reach Lemonade from WSL at http://$WINDOWS_HOST:13305/api/v1/models"
  echo "Check the Windows netsh portproxy and firewall rule from the README."
  exit 1
fi

echo "$models_json" | python3 -m json.tool >/dev/null
echo "OK: WSL can reach native Windows Lemonade through the bridge"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "wsl-lemonade-bridge-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "WSL Lemonade bridge test failed"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->

---
<!-- @os:end -->

## Hermes Agent telepítése

<!-- @os:windows -->
> Ebben a szakaszban futtasd a parancsokat a **WSL terminálodban**, hacsak másképp nincs jelezve.
<!-- @os:end -->

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

A `--skip-setup` jelző kihagyja az interaktív telepítővarázslót, így a modell háttérrendszerét a következő lépésben manuálisan konfigurálhatod.

Töltsd újra a shell-edet:

```bash
source ~/.bashrc
```

Erősítsd meg a telepítést:

```bash
hermes --version
```

Futtass egy önellenőrzést, hogy ellenőrizd az összes függőséget:

```bash
hermes doctor
```

> **Tipp:** Ha a telepítés után `command not found` üzenetet látsz, add hozzá a Hermes-t a PATH-hoz:
> ```bash
> export PATH="$HOME/.local/bin:$PATH"
> ```
> Ahhoz, hogy ez tartós legyen, add hozzá a fenti sort a `~/.bashrc` vagy `~/.zshrc` fájlodhoz.

<!-- @os:linux -->
<!-- @test:id=hermes-version-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
hermes --version
# hermes doctor is a self-diagnostic; run it for the logs but don't gate CI on it (it can probe live model/runtime state that varies on the runner).
hermes doctor || true
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=hermes-version-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
hermes --version
# hermes doctor is a self-diagnostic; run it for the logs but don't gate CI on it (it can probe live model/runtime state that varies on the runner).
hermes doctor || true
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-version-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "Hermes version check failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

---
## A Hermes konfigurálása a Lemonade használatához

A Hermes a modellkonfigurációját a `~/.hermes/config.yaml` fájlban tárolja. Használhatod az interaktív `hermes model` választót, vagy közvetlenül is megírhatod a konfigurációt.

### 1. lehetőség: Interaktív választó

<!-- @os:windows -->
> A következő parancsot a **WSL terminálban** futtasd.
<!-- @os:end -->

<!-- @os:linux -->
```bash
hermes model
```
<!-- @os:end -->

<!-- @os:windows -->
```bash
hermes model
```
<!-- @os:end -->

Amikor a rendszer kéri:

1. Válaszd a **Custom endpoint (enter URL manually)** lehetőséget
<!-- @os:linux -->
2. **API base URL:** `http://127.0.0.1:13305/api/v1`
<!-- @os:end -->
<!-- @os:windows -->
2. **API base URL:** használd a WSL gateway IP-t: futtasd le a `ip route show default | awk '{print $3}' | head -1` parancsot a WSL-ben a lekéréséhez, majd add meg: `http://<WSL-Gateway-IP>:13305/api/v1`
<!-- @os:end -->
3. **API key:** `lemonade`
4. **API compatibility mode:** `1` (Automatikus felismerés)
5. **Select model:** válaszd ki a `Qwen3.6-35B-A3B-GGUF` modellt a listából
6. **Context length in tokens:** `262144`
7. **Display name:** `local-lemonade` (vagy bármilyen általad választott név)

A `hermes model` elmenti mind az aktív modellválasztást, mind egy elnevezett `custom_providers` bejegyzést, amely az adott végponttal együtt tárolja a kontextushosszt is. Az eredmény a `~/.hermes/config.yaml` fájlban így néz ki:

```yaml
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://127.0.0.1:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://127.0.0.1:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
```

### 2. lehetőség: Konfiguráció közvetlen megírása

<!-- @os:linux -->

```bash
mkdir -p ~/.hermes
cat >> ~/.hermes/config.yaml <<'EOF'
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://127.0.0.1:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://127.0.0.1:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF
```

<!-- @test:id=hermes-lemonade-config-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

# Write the model config fresh so the test is idempotent across CI runs.
# (An append would create duplicate YAML keys and later break the gateway test.)
mkdir -p "$HOME/.hermes"
rm -f "$HOME/.hermes/config.yaml"
cat > "$HOME/.hermes/config.yaml" <<'EOF'
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://127.0.0.1:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://127.0.0.1:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF

config="$HOME/.hermes/config.yaml"

grep -q "provider: custom" "$config"
grep -q "Qwen3.6-35B-A3B-GGUF" "$config"
grep -q "13305" "$config"
grep -q "context_length: 262144" "$config"

echo "OK: Hermes config.yaml contains Lemonade model configuration"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->

A WSL terminálban kérd le a Windows gazdagép IP-címét, és írd meg a konfigurációt:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)

mkdir -p ~/.hermes
cat >> ~/.hermes/config.yaml <<EOF
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://$WINDOWS_HOST:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://$WINDOWS_HOST:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF
```

<!-- @test:id=hermes-lemonade-config-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

WINDOWS_HOST="$(ip route show default | awk '{print $3}' | head -1)"
if [ -z "$WINDOWS_HOST" ]; then
  echo "Could not determine WSL gateway IP"
  exit 1
fi

# Write the model config fresh so the test is idempotent across CI runs.
# (An append would create duplicate YAML keys and later break the gateway test.)
mkdir -p "$HOME/.hermes"
rm -f "$HOME/.hermes/config.yaml"
cat > "$HOME/.hermes/config.yaml" <<EOF
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://$WINDOWS_HOST:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://$WINDOWS_HOST:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF

config="$HOME/.hermes/config.yaml"

grep -q "provider: custom" "$config"
grep -q "Qwen3.6-35B-A3B-GGUF" "$config"
grep -q "13305" "$config"
grep -q "context_length: 262144" "$config"

echo "OK: Hermes config.yaml contains Lemonade model configuration (Windows host)"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-lemonade-config-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "Hermes Lemonade config check failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

---

## (Ajánlott) Podman homokozó (sandboxing) engedélyezése

A Hermes Agent képes az összes ágensművelet (parancssori és fájlműveleteket) egy izolált konténeren keresztül irányítani, ahelyett hogy közvetlenül a gazdagépeden futtatná őket. Ez korlátozza minden nem szándékos művelet hatókörét a homokozóra, így a gazdagéped fájlrendszere és hálózata érintetlen marad.

Építs egy könnyűsúlyú homokozó image-et:

<!-- @os:linux -->
```bash
podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE
```

<!-- @test:id=hermes-sandbox-image-linux timeout=1800 hidden=True -->
```bash
set -euo pipefail

podman version

podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE

podman image inspect hermes-sandbox:bookworm-slim >/dev/null

echo "OK: Hermes sandbox Podman image is available"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
Lépj be a WSL terminálba:

```powershell
wsl -d Ubuntu-24.04
```

Ezután építs egy könnyűsúlyú homokozó image-et:

```bash
podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE
```

<!-- @test:id=hermes-sandbox-image-windows timeout=1800 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

podman version

podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE

podman image inspect hermes-sandbox:bookworm-slim >/dev/null

echo "OK: Hermes sandbox Podman image is available inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-sandbox-image-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "Hermes sandbox image build failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

Ezután állítsd be a Hermest, hogy a Podmant használja konténer-futtatókörnyezetként, és állítsd be a terminál backendet:

```bash
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> ~/.hermes/.env

cat >> ~/.hermes/config.yaml <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF
```

> A `terminal.backend` továbbra is `docker`.
> A `HERMES_DOCKER_BINARY` az, ami közli a Hermesszel, hogy a Podmant használja futtatókörnyezetként a Docker helyett.

<!-- @os:linux -->
<!-- @test:id=hermes-sandbox-config-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config test first."
  exit 1
fi

# The sandbox image must exist before Hermes can use it as the terminal backend.
podman image inspect hermes-sandbox:bookworm-slim >/dev/null

# Point Hermes at Podman as the container runtime (idempotent: drop any prior line first).
mkdir -p "$HOME/.hermes"
touch "$HOME/.hermes/.env"
grep -v '^HERMES_DOCKER_BINARY=' "$HOME/.hermes/.env" > "$HOME/.hermes/.env.tmp" || true
mv "$HOME/.hermes/.env.tmp" "$HOME/.hermes/.env"
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> "$HOME/.hermes/.env"

# Append the terminal backend block (config.yaml is rewritten fresh by the model-config test each run, so this appends exactly once per run).
cat >> "$config" <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF

grep -q "HERMES_DOCKER_BINARY=/usr/bin/podman" "$HOME/.hermes/.env"
grep -q "backend: docker" "$config"
grep -q "docker_image: hermes-sandbox:bookworm-slim" "$config"

echo "OK: Hermes sandbox (Podman) configuration was written"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=hermes-sandbox-config-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config test first."
  exit 1
fi

podman image inspect hermes-sandbox:bookworm-slim >/dev/null

mkdir -p "$HOME/.hermes"
touch "$HOME/.hermes/.env"
grep -v '^HERMES_DOCKER_BINARY=' "$HOME/.hermes/.env" > "$HOME/.hermes/.env.tmp" || true
mv "$HOME/.hermes/.env.tmp" "$HOME/.hermes/.env"
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> "$HOME/.hermes/.env"

cat >> "$config" <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF

grep -q "HERMES_DOCKER_BINARY=/usr/bin/podman" "$HOME/.hermes/.env"
grep -q "backend: docker" "$config"
grep -q "docker_image: hermes-sandbox:bookworm-slim" "$config"

echo "OK: Hermes sandbox (Podman) configuration was written inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-sandbox-config-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "Hermes sandbox config failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

A Hermes ezután elindít egy állandó homokozó konténert, és ezen keresztül irányítja az összes `terminal` és fájlkezelő eszközhívást. A konténer a Hermes folyamatával együtt él, minden eszközhívásnál újrahasznosítódik, és a Hermes kilépésekor megszűnik.

> **A homokozó működésének ellenőrzése:** Indítsd el a Hermest (`hermes`), és kérd meg, hogy `run hostname` - ekkor a géped hostneve helyett egy rövid konténerazonosítót kell látnod. Azt is kérheted, hogy `rm -rf <path-to-a-dummy-file/folder>`: a Hermes megerősíti a törlést, de a mappa a gazdagépeden továbbra is megmarad. A parancs a konténer izolált `$HOME` könyvtárában futott, nem a tiéden.

> **Erősebb izolációra van szükséged?** A Hermes hivatalos Docker image-et is biztosít (`nousresearch/hermes-agent`), amely a teljes ágensfolyamatot egy konténeren belül futtatja - gateway, eszközök, minden. A beállítási részletekért lásd a [Hermes Docker dokumentációját](https://hermes-agent.nousresearch.com/docs/user-guide/docker).

---

<!-- @os:linux -->
## (Ajánlott) Hermes integráció a Firecrawl szolgáltatásokkal

A Hermes a beépített webes eszközeivel képes böngészni és tartalmat kinyerni weboldalakról. Sok modern weboldal azonban bot-felismerő rendszereket használ, amelyek blokkolják az egyszerű HTTP-kéréseket, és a tényleges tartalom helyett kihívási (challenge) oldalakat adnak vissza. Emiatt előfordulhat, hogy a Hermes nem tud megbízhatóan információt kinyerni ezekről az oldalakról.

E korlátozás leküzdésére a [Firecrawl](https://docs.firecrawl.dev/introduction) egy önállóan üzemeltethető webes crawling és tartalomkinyerő szolgáltatást biztosít, amely képes megkerülni ezeket a kihívásokat, és kiaknázni a Hermes automatizálásának teljes potenciálját.

Ebben a beállításban a Firecrawl Podmannel kezelt Docker konténerek halmazaként fut. Az életciklus-kezelés és az automatikus indítás egyszerűsítése érdekében a Firecrawlt egy felhasználói szintű `systemd` szolgáltatásként regisztráljuk, amely az alapul szolgáló Podman Compose stacket vezényli. Ez lehetővé teszi, hogy a Hermes a Firecrawl szolgáltatást a standard `systemctl --user` parancsokkal indítsa, állítsa le és ellenőrizze, ahelyett hogy közvetlenül lépne kapcsolatba a konténerekkel.

Az egyszerűség kedvéért a teljes folyamatot négy lépésre bontottuk:

---

### 1. A rendszerszolgáltatás regisztrálása
Navigálj a systemd felhasználói konfigurációs könyvtárba:
```bash
cd ~/.config/systemd/user
```
Hozz létre és nyiss meg egy új fájlt `firecrawl.service` néven.
```bash
nano firecrawl.service
```
Másold be a következő konfigurációt:
```bash
[Unit]
Description=Firecrawl
After=podman.service
Requires=podman.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=${HOME}/firecrawl

# Optional: Validate config before starting
ExecStartPre=/usr/bin/podman -f hermes-compose.yaml config --quiet

# Start containers in detached mode
ExecStart=/usr/bin/podman compose -f hermes-compose.yaml up -d --remove-orphans

# Stop containers when the service stops
ExecStop=/usr/bin/podman compose -f hermes-compose.yaml down

[Install]
WantedBy=default.target

```
Ezen a ponton a szolgáltatás már definiálva van, de még nincs regisztrálva a `systemd`-nél.
Győződj meg róla, hogy a fájlnév pontosan megegyezik a fent létrehozottal, majd futtasd:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
Sikeres végrehajtás esetén a következő kimenetet kell látnod:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

A `default.target.wants/` szimbolikus linkeket tartalmaz azokhoz a szolgáltatásokhoz, amelyek automatikus indításra vannak beállítva.

### 2. A Firecrawl konfigurálása a szolgáltatásodhoz

A [SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) ideális azok számára, akik teljes körű ellenőrzést szeretnének a scraping és adatfeldolgozási környezetük felett, de ez további karbantartási és konfigurációs erőfeszítésekkel jár.

Kezdd a repository klónozásával:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
Hozz létre egy `.env` fájlt a gyökér `/firecrawl` könyvtárban:
```bash
# ===== Required ENVS ======
PORT=3002
HOST=0.0.0.0

# ===== Firecrawl =====
# FIRECRAWL_API_KEY=""

# ===== Proxy =====
# PROXY_SERVER can be a full URL (e.g. http://0.1.2.3:1234) or just an IP and port combo (e.g. 0.1.2.3:1234)
# Do not uncomment PROXY_USERNAME and PROXY_PASSWORD if your proxy is unauthenticated
# PROXY_SERVER=
# PROXY_USERNAME=
# PROXY_PASSWORD=

# This key lets you access the queue admin panel. Change this if your deployment is publicly accessible.
BULL_AUTH_KEY=CHANGEME

# ===== System Resource Configuration =====
# Maximum CPU usage threshold (0.0-1.0). Worker will reject new jobs when CPU usage exceeds this value.
# Default: 0.8 (80%)
# MAX_CPU=0.8

# Maximum RAM usage threshold (0.0-1.0). Worker will reject new jobs when memory usage exceeds this value.
# Default: 0.8 (80%)
# MAX_RAM=0.8
```
> Állítsd be a `BULL_AUTH_KEY` értékét egy erős titkos kulcsra, különösen ha a telepítés nem megbízható hálózatokból is elérhető.
### 3. Hermes telepítése Compose segítségével

Mielőtt továbblépnénk, győződjön meg róla, hogy letöltötte a legújabb Hermes Docker image-et:
```bash
podman pull docker.io/nousresearch/hermes-agent:latest
```
Ezután töltse le a Hermes Compose fájlt [hermes-compose.yaml](assets/hermes-compose.yaml) néven, és helyezze el a gyökér `/firecrawl` könyvtárba:

> Ez a konvenció szükséges ahhoz, hogy a `systemd` megfelelően megtalálja és elindítsa a szolgáltatást, ahogy azt a `WorkingDirectory=${HOME}/firecrawl` beállítás előírja.

> A stack-et bármikor bővítheti további Firecrawl szolgáltatásokkal, szükség szerint. Az elérhető szolgáltatások teljes listája megtalálható a hivatalos [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml) fájlban.

### 4. A Hermes szolgáltatás elindítása a Firecrawl-on keresztül 

Mielőtt átadná az irányítást a `systemd`-nek, ellenőrizze, hogy minden megfelelően működik-e a stack manuális futtatásával:
```bash
podman compose -f hermes-compose.yaml up -d
```
Ha minden megfelelően van beállítva, a Hermes konténer elindul, és a parancssori kimenetnek valahogy így kell kinéznie:
<p align="center">
  <img src="assets/podman_health_verification.png" width="500" height="400" />
</p>

Az ellenőrzés után állítsa le a stack-et, mielőtt továbblépne:
```bash
podman compose -f hermes-compose.yaml down
```
Miután minden ellenőrizve lett, indítsa el a szolgáltatást a `systemd`-n keresztül:
```bash
systemctl --user start firecrawl.service
```
[A Hermes API](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server/#endpoints) elérhető az interaktív konténeren belülről, a Web Dashboard pedig ugyanazon a gépen és porton érhető el: http://127.0.0.1:9119.
<p align="center">
  <img src="assets/System_Service_launch.png" width="500" height="500" />
</p>

A szolgáltatás leállításához futtassa:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---

## Hermes Native

Indítson el egy interaktív CLI munkamenetet közvetlenül: 

```bash
hermes
```

<!-- @os:linux -->
<!-- @test:id=hermes-gateway-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config step first."
  exit 1
fi

log="/tmp/hermes-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

hermes gateway run >"$log" 2>&1 &
gateway_pid=$!

# `hermes gateway run` is a long-running message bridge + cron scheduler with no
# HTTP health endpoint, so we detect a successful boot by (1) a known startup
# marker appearing in the log and (2) the process still being alive afterwards
# (i.e. it parsed config.yaml and did not crash). "No messaging platforms
# enabled" is expected in CI (no channel token) and is not a failure.
ok=false
for i in $(seq 1 60); do
  if grep -qE "Hermes Gateway Starting|gateway\.run|cron scheduler" "$log" 2>/dev/null; then
    ok=true
    break
  fi
  if ! kill -0 "$gateway_pid" 2>/dev/null; then
    echo "Hermes gateway process exited before it finished starting"
    break
  fi
  sleep 1
done

# Give it a moment to surface any immediate post-banner crash, then confirm it is still running.
sleep 3

if [ "$ok" = "true" ] && kill -0 "$gateway_pid" 2>/dev/null; then
  echo "OK: Hermes gateway started successfully"
else
  echo "Hermes gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=hermes-gateway-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config step first."
  exit 1
fi

log="/tmp/hermes-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

hermes gateway run >"$log" 2>&1 &
gateway_pid=$!

# `hermes gateway run` is a long-running message bridge + cron scheduler with no
# HTTP health endpoint, so we detect a successful boot by (1) a known startup
# marker appearing in the log and (2) the process still being alive afterwards
# (i.e. it parsed config.yaml and did not crash). "No messaging platforms
# enabled" is expected in CI (no channel token) and is not a failure.
ok=false
for i in $(seq 1 60); do
  if grep -qE "Hermes Gateway Starting|gateway\.run|cron scheduler" "$log" 2>/dev/null; then
    ok=true
    break
  fi
  if ! kill -0 "$gateway_pid" 2>/dev/null; then
    echo "Hermes gateway process exited before it finished starting"
    break
  fi
  sleep 1
done

# Give it a moment to surface any immediate post-banner crash, then confirm it is still running.
sleep 3

if [ "$ok" = "true" ] && kill -0 "$gateway_pid" 2>/dev/null; then
  echo "OK: Hermes gateway started inside WSL"
else
  echo "Hermes gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-gateway-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "Hermes gateway test failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

**Gratulálunk, elkészítette a teljesen helyi AI-ügynök stacket.**

### Web Dashboard

A Hermes tartalmaz egy böngészőalapú felhasználói felületet a konfiguráció, API-kulcsok, modellek, munkamenetek, memória és időzített feladatok (cron jobs) kezelésére. Nyisson meg egy második terminált, miközben a gateway vagy a CLI fut, és indítsa el a következővel:

```bash
hermes dashboard
```

Ez elindít egy helyi szervert, és megnyitja a `http://127.0.0.1:9119` címet a böngészőben. A teljes funkciólistáért lásd a [dashboard dokumentációt](https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard).
<p align="center">
  <img src="assets/hermes_dashboard.jpg" width="500" height="300" />
</p>

---

## Opcionális: Kommunikációs csatorna csatlakoztatása

Miután a gateway fut, bármely eszközről elérheti a helyi ügynökét. A Hermes támogatja a [Discord](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord), [Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) és más platformokat.

---

### Discord

A Discordhoz szükség van egy szerverre, ahol **rendelkezik adminisztrátori hozzáféréssel** a bot hozzáadásához. Ha megosztott szervereket használ, de nincs sajátja, használja inkább a Telegramot.

#### Discord alkalmazás és bot létrehozása

1. Menjen a [Discord Developer Portal](https://discord.com/developers/applications) oldalra, és kattintson a **New Application** gombra. Adjon neki egy nevet (pl. "hermes-bot").
2. Az oldalsávban kattintson a **Bot** menüpontra. Állítson be egy felhasználónevet a botnak.
3. Még mindig a Bot oldalon, görgessen le a **Privileged Gateway Intents** részhez, és engedélyezze:
   - **Message Content Intent** (kötelező)
   - **Server Members Intent** (ajánlott)
4. Görgessen vissza felfelé, és kattintson a **Reset Token** gombra a bot tokenjének generálásához. Másolja ki.

#### A bot hozzáadása a szerverhez

1. Az oldalsávban kattintson az **OAuth2 / URL Generator** menüpontra.
2. A **Scopes** alatt engedélyezze a `bot` és az `applications.commands` opciókat.
3. A **Bot Permissions** alatt engedélyezze: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Másolja ki a generált URL-t, illessze be a böngészőbe, válassza ki a szerverét, és erősítse meg.

#### Az azonosítók összegyűjtése és a DM-ek engedélyezése

Engedélyezze a Fejlesztői módot a Discordban (**User Settings / Advanced / Developer Mode**), majd:
- Kattintson jobb gombbal a szerver ikonjára: **Copy Server ID**
- Kattintson jobb gombbal a saját avatarjára: **Copy User ID**

Kattintson jobb gombbal a szerver ikonjára / **Privacy Settings** / kapcsolja be a **Direct Messages** opciót. Ez szükséges a párosítási lépéshez.

#### A Hermes konfigurálása Discordhoz

Adja hozzá a következőt a `~/.hermes/.env` fájlhoz:

```bash
# Required
DISCORD_BOT_TOKEN=your-bot-token
DISCORD_ALLOWED_USERS=your-discord-user-id
```

Ezután indítsa el a gateway-t:

```bash
hermes gateway
```

A botnak néhány másodpercen belül online állapotba kell kerülnie a Discordban. Küldjön neki egy üzenetet, akár DM-ben, akár egy általa látható csatornán.

<p align="center">
  <img src="assets/discord_bot.png" width="400" height="300" />
</p>


---

### Telegram

#### Telegram bot létrehozása

1. Nyissa meg a Telegramot, és küldjön üzenetet a **@BotFather**-nek.
2. Küldje el a `/newbot` parancsot, és kövesse az utasításokat. Mentse el a kapott bot tokent.

#### A Hermes konfigurálása Telegramhoz

Adja hozzá a következőt a `~/.hermes/.env` fájlhoz:

```bash
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ALLOWED_USERS=your-telegram-user-id   # comma-separated for multiple users
```

> **Nem tudja a Telegram felhasználói azonosítóját?** Küldjön üzenetet a [@userinfobot](https://t.me/userinfobot) fióknak Telegramon,  ez válaszként elküldi a numerikus azonosítóját.

Ezután indítsa el a gateway-t:

```bash
hermes gateway
```

Küldjön egy tesztüzenetet a botjának Telegramon. Ezután Telegram DM-en keresztül is beszélgethet az ügynökével. A webhook módról és a további beállítási lehetőségekről lásd a [teljes Telegram beállítási útmutatót](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram).

---

## Következő lépések

Most, hogy az ügynöke parancsokat tud fogadni a telefonjáról, és tud cselekedni a helyi gépén, íme három érdemes irány a további felfedezéshez:

1. **Automatizált kutatási összefoglaló**: Ütemezze be a Hermest, hogy minden reggel keressen az önt érdeklő témákról a weben, foglalja össze az eredményeket a helyi modellel, és küldjön egy összefoglalót a telefonjára Telegramon vagy Discordon keresztül, mindezt a saját hardverén, felhőalapú költségek nélkül.

2. **Kódellenőrzés igény szerint**: Irányítsa a Hermest egy GitHub tárolóra, kérje meg, hogy vizsgálja meg a nyitott pull requesteket, és tegye közzé a hozzászólásokat vagy egy összefoglalót a csevegésében. A Docker terminál backenddel minden git művelet a sandboxban fut, így a hoszt gép tiszta marad.

3. **Helyi fájlasszisztens**: Adjon a Hermesnek hozzáférést egy munkakönyvtárhoz, és kérje meg, hogy szervezzen, nevezzen át, foglaljon össze vagy alakítson át fájlokat igény szerint a telefonjáról. Mivel a Docker terminál backend minden írási műveletet a sandbox munkaterületre korlátoz, a véletlen destruktív műveletek hatása korlátozott marad.