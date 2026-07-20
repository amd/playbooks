<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->
# Suorita OpenClaw Lemonade Serverillä taustajärjestelmänä

## Yleiskatsaus

[**OpenClaw**](https://openclaw.ai/) on autonominen tekoälyagentti, joka pystyy kirjoittamaan ja suorittamaan koodia, hallitsemaan tiedostoja ja suorittamaan monimutkaisia moniosaisia tehtäviä puolestasi. Toisin kuin chat-avustaja, joka vain vastaa kysymyksiin, OpenClaw suorittaa todellisia toimia järjestelmässäsi, mikä tarkoittaa, että se tarvitsee nopean ja tehokkaan tekoälytaustajärjestelmän, joka pysyy vaativan agenttisilmukan tahdissa.

[**Lemonade Server**](https://lemonade-server.ai/) on tämä taustajärjestelmä. Se on avoimen lähdekoodin paikallinen päättelypalvelin, joka suorittaa GenAI-malleja suoraan laitteistollasi ja tarjoaa ne käyttöön alan standardin OpenAI API:n kautta.

Yhdessä ne muodostavat täysin paikallisen tekoälyagenttipinon: Lemonade huolehtii mallin päättelystä, ja OpenClaw tarjoaa agenttisilmukan, joka muuttaa mallin tulosteet todellisiksi toimiksi.

> **Ennen kuin jatkat:** OpenClaw on erittäin autonominen tekoälyagentti. Minkä tahansa tekoälyagentin päästäminen käsiksi järjestelmääsi voi johtaa arvaamattomiin tai tahattomiin lopputuloksiin. Jatka vain, jos ymmärrät riskit ja hyväksyt sen, että autonominen ohjelmisto toimii puolestasi.

---

## Mitä opit

Tämän ohjeen lopussa osaat:

- Tutustua **Lemonade Serveriin**
- **Asentaa OpenClaw'n** ja **määrittää sen käyttämään Lemonade Serveriä** tekoälytaustajärjestelmänään.
- **Käynnistää OpenClaw-yhdyskäytävän** ja varmistaa, että agenttisi on valmis työskentelemään.
- **Yhdistää viestintäkanavan** (Discord tai Telegram), jotta voit keskustella agenttisi kanssa mistä tahansa laitteesta.

---

## Muistiasetuksen määrittäminen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Tarkista ohjelmistopäivitykset

<!-- @require:software-update -->
<!-- @device:end -->

## Ohjelmiston edellytysten asentaminen

<!-- @os:linux -->
- PC, jossa on **Ubuntu 24.04+** tai yhteensopiva Debian-pohjainen Linux-jakelu, jossa on `apt-get`
- Vähintään **12 Gt RAM-muistia** (64 Gt+ suositellaan suuremmille malleille)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (valinnainen, OpenClaw'n hiekkalaatikointiin)

- **~10–30 Gt vapaata levytilaa** mallien painoille
<!-- @os:end -->
<!-- @os:windows -->
- PC, jossa on **Windows 10/11**
- Vähintään **12 Gt RAM-muistia** (64 Gt+ suositellaan suuremmille malleille)
- **~10–30 Gt vapaata levytilaa** mallien painoille
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (valinnainen, OpenClaw'n hiekkalaatikointiin)
<!-- @os:end -->

<!-- @require:lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Lataa ja avaa suositeltu malli

Tämän ohjeen suositeltu malli on **Qwen3.6-35B-A3B-GGUF** Unslothilta, vahva MoE-malli, jossa on 263k-tokenin kontekstiikkuna ja joka soveltuu hyvin agenttityökuormiin. Tämä malli käyttää UD-Q4_K_XL-kvantisointia. Lataa se nyt:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Avaa se sitten laajalla kontekstiikkunalla ja tallenna tämä asetus tulevia ajokertoja varten:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

Mallin oletuskontekstipituus on 262 144 tokenia. Jos kohtaat muistin loppumisesta johtuvia (OOM) virheitä, harkitse kontekstiikkunan pienentämistä. Koska Qwen3.6 kuitenkin hyödyntää laajennettua kontekstia monimutkaisissa tehtävissä, suosittelemme pitämään kontekstipituuden vähintään 128K tokenissa ajattelukyvyn säilyttämiseksi.

> **Vinkki: Poista ajattelu käytöstä nopeampia agenttivastauksia varten:** Qwen3.6-35B-A3B toimii oletusarvoisesti ajattelutilassa, mikä lisää viivettä ennen jokaista vastausta. Agenttisilmukoissa tämä ylimääräinen viive kertyy nopeasti. [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) -repositorio tarjoaa valmiin määrityksen, joka poistaa ajattelun käytöstä. Käytä sitä lataamalla tiedosto ja tuomalla se:
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
$entry = $parsed.data | Where-Object { $_.id -eq "${openclaw_model}" } | Select-Object -First 1

if (-not $entry) {throw "Model ${openclaw_model} is not present in Lemonade /api/v1/models."}
if (-not $entry.downloaded) {throw "Model ${openclaw_model} is present but not downloaded in Lemonade. Please download it before running CI."}
Write-Host "OK: ${openclaw_model} model is downloaded in Lemonade"

if ($entry.recipe_options.ctx_size -ne 262144) {
  throw "Model ${openclaw_model} is not saved with ctx_size=262144. Run: lemonade load ${openclaw_model} --ctx-size 262144 --save-options"
}
Write-Host "OK: ${openclaw_model} is saved with ctx_size=262144"

$body = @{
  model = "${openclaw_model}"
  messages = @(
    @{
      role = "user"
      content = "Reply with exactly: OK"
    }
  )
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "openclaw-lemonade-chat-body.json"
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
model_id = "${openclaw_model}"

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
  "model": "${openclaw_model}",
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

## Asenna WSL

Suoritamme OpenClaw'n WSL:n sisällä (suositeltu) ja yhdistämme sen Windowsissa natiivisti käynnissä olevaan Lemonadeen. Tämä antaa sinulle Linux-komentoriviympäristön OpenClaw'lle säilyttäen samalla Lemonaden GPU-kiihdytyksen Windows-puolella.

### Asenna WSL ja Ubuntu

Avaa PowerShell järjestelmänvalvojana ja asenna WSL-ydin:

```powershell
wsl --install --no-distribution
```

Asenna sitten Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### Ota systemd käyttöön WSL:ssä

Suorita tämä Ubuntu-päätteessä:

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

Käynnistä WSL uudelleen:

```powershell
wsl --shutdown
wsl
```

### Yhdistä Lemonade Windowsista WSL:ään

WSL2 toimii virtuaaliverkossa. Windowsissa toimiva Lemonade sitoutuu osoitteeseen `127.0.0.1`, johon WSL ei pääse suoraan käsiksi. Windowsin porttiproksi ohjaa liikenteen WSL-yhdyskäytävän IP-osoitteesta Windowsin localhostiin.

**Etsi WSL-yhdyskäytäväsi IP-osoite** (suorita WSL:n sisällä):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Lisää porttiproksi** (suorita PowerShellissä järjestelmänvalvojana, korvaa `<WSL-Gateway-IP>` WSL-yhdyskäytäväsi IP-osoitteella):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**Lisää palomuurisääntö** (samassa korotetuissa oikeuksissa toimivassa PowerShellissä):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Vahvista WSL:stä**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Jos olet jo ladannut Qwen3.6-35B-A3B-GGUF-mallin edellisessä vaiheessa, sinun pitäisi nähdä tämänkaltainen JSON-tuloste:

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

> `netsh portproxy` -sääntö säilyy uudelleenkäynnistysten yli, mutta WSL-yhdyskäytävän IP-osoite voi muuttua `wsl --shutdown` -komennon jälkeen. Jos Lemonade ei ole enää tavoitettavissa WSL:stä uudelleenkäynnistyksen jälkeen, hae päivitetty yhdyskäytävän IP-osoite ja päivitä proksi tällä uudella osoitteella.

<!-- @test:id=wsl-lemonade-bridge-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
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

## Asenna ja määritä OpenClaw

### Asenna OpenClaw
<!-- @os:windows -->
> Suorita tämän osion komennot **WSL-päätteessäsi**.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

`--no-onboard`-lippu ohittaa interaktiivisen asennusvelhon; määrität mallitaustajärjestelmän manuaalisesti seuraavassa vaiheessa, mikä antaa sinulle tarkan hallinnan siitä, mitä mallia ja palvelinta käytetään.

Avaa uusi pääte ja vahvista asennus:

```bash
openclaw --version
```

> **Vinkki:** Jos näet asennuksen jälkeen viestin `command not found`, lisää npm:n globaali bin-hakemisto PATH-muuttujaan:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Tehdäksesi tästä pysyvän, lisää yllä oleva rivi `~/.bashrc`- tai `~/.zshrc`-tiedostoosi.

<!-- @os:linux -->
<!-- @test:id=openclaw-version-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
echo "HOME=$HOME"
echo "PATH=$PATH"
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
node -v
npm -v
openclaw --version
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openclaw-version-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
echo "HOME=$HOME"
echo "PATH=$PATH"
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
node -v
npm -v
openclaw --version
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-version-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "OpenClaw version check failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->
### Configure OpenClaw käyttämään Lemonadea

Suorita OpenClaw:n ei-interaktiivinen käyttöönotto.
<!-- @os:linux -->
```bash
openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://127.0.0.1:13305/api/v1" \
  --custom-model-id "Qwen3.6-35B-A3B-GGUF" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk
```
<!-- @os:end -->
<!-- @os:windows -->
```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://$WINDOWS_HOST:13305/api/v1" \
  --custom-model-id "Qwen3.6-35B-A3B-GGUF" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk
```
<!-- @os:end -->

Tämä komento kirjoittaa OpenClaw:n määrityksen tiedostoon `~/.openclaw/openclaw.json`.

> **OpenClaw-kontekstiikkunan koko:** OpenClaw:n tiivistys käynnistyy, kun `contextTokens > contextWindow − reserveTokens`. Oletusarvoinen `reserveTokensFloor` on 20 000 tokenia, mikä on alaraja, joka ohittaa arvon `reserveTokens`, kun se on pienempi, joten mikä tahansa mallin konteksti alle noin 37 000 tokenin käynnistää loputtoman tiivistyssilmukan. Aseta pieni reservi ja poista alaraja käytöstä kerran omassa määrityksessäsi, ja se pätee jokaiseen malliin, ilman mallikohtaista säätöä:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` on *alaraja* (vähimmäissuoja), ei itse reservi, joten pelkän alarajan asettamisella ei ole vaikutusta. `reserveTokensFloor: 0` poistaa suojan käytöstä, jotta pienempi `reserveTokens`-arvo hyväksytään.
>
> **Milloin tätä sovelletaan:** Käytä tätä määritystä, jos mallisi tehokas kontekstiikkuna on alle noin 37 000 tokenia, joko siksi, että malli on pieni (esim. 8k, 16k, 32k) tai siksi, että olet tarkoituksella rajoittanut sen pienempään arvoon (esim. ladannut 128k-mallin mutta asettanut kontekstin arvoon 16k Lemonadessa). Ilman tätä OpenClaw ajautuu loputtomaan tiivistyssilmukkaan käynnistyksessä.
>
> **Suuren kontekstin mallit täydellä kontekstilla:** Voit ohittaa tämän kokonaan. Oletusasetukset toimivat hyvin, tiivistys käynnistyy hyvissä ajoin ennen ikkunan täyttymistä, ja mallilla on runsaasti tilaa pitkien vastausten tuottamiseen. Jos sovellat tätä silti, huomioi, että `reserveTokens: 4096` rajoittaa vastauksen pituuden noin 4k tokeniin, mikä voi katkaista pitkien tiedostojen luonnin tai yksityiskohtaiset suunnitelmat.
>
> **Mihin tämä lisätään:** Sijoita `compaction`-lohko `agents.defaults`-osion sisään `openclaw.json`-tiedostossasi (yleensä polussa `~/.openclaw/openclaw.json`):
>
> ```json
> {
>   "agents": {
>     "defaults": {
>       "workspace": "/home/<you>/.openclaw/workspace",
>       "model": {
>         "primary": "lemonade/<your-model-id>"
>       },
>       "compaction": {
>         "reserveTokens": 4096,
>         "reserveTokensFloor": 0
>       }
>     }
>   }
> }
> ```
>
> Määrityksen loppuosa (gateway, kanavat, mallit jne.) pysyy ennallaan, vain `compaction`-avain tarvitsee lisätä.

### (Suositeltu) Ota Docker-hiekkalaatikointi käyttöön

OpenClaw voi ohjata kaikki agentin tiedosto- ja koodioperaatiot eristetyn Docker-säiliön kautta sen sijaan, että ne suoritettaisiin suoraan isäntäkoneella. Tämä rajoittaa minkä tahansa tahattoman toiminnon vaikutuksen hiekkalaatikkoon, jättäen isäntäkoneesi tiedostojärjestelmän ja verkon koskemattomaksi.

Rakenna hiekkalaatikkokuva kerran (Dockerin on oltava asennettuna):

```bash
docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
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

<!-- @os:linux -->
<!-- @test:id=openclaw-sandbox-image-linux timeout=1800 hidden=True -->
```bash
set -euo pipefail

docker version

docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
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

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

echo "OK: OpenClaw sandbox Docker image is available"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openclaw-sandbox-image-windows timeout=1800 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="/mnt/wsl/docker-desktop/cli-tools/usr/bin:$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

docker_config="$(mktemp -d)"
cleanup() {
  rm -rf "$docker_config"
}
trap cleanup EXIT
export DOCKER_CONFIG="$docker_config"
printf '{ "auths": {} }\n' > "$DOCKER_CONFIG/config.json"

docker version

docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
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

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

echo "OK: OpenClaw sandbox Docker image is available inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-sandbox-image-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "OpenClaw sandbox image build failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

Suorita tämä lisätäksesi `sandbox`-avaimen olemassa olevan `agents.defaults`-lohkon sisään tiedostossa `~/.openclaw/openclaw.json`:

```bash
cat > sandbox.patch.json5 <<JSON5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none"
      }
    }
  }
}
JSON5
openclaw config patch --file ./sandbox.patch.json5
```

Hiekkalaatikkosäiliöillä **ei ole verkkoyhteyttä** oletuksena. Katso [hiekkalaatikoinnin viitedokumentaatio](https://docs.openclaw.ai/gateway/sandboxing) bind-liitoksia ja verkkoasetusten ohituksia varten.

> #### Vianmääritys: Dockerin käyttöoikeus evätty
> 
> Jos saat "permission denied" -virheen Docker-komentoja suorittaessasi:
> 
> **Vaihe 1: Lisää käyttäjäsi docker-ryhmään**
> 
> ```bash
> sudo groupadd docker                    # Create group if needed
> sudo usermod -aG docker $USER           # Add yourself to the group
> newgrp docker                           # Activate the change
> docker run hello-world                  # Test it
> ```
> 
> **Vaihe 2: Jos virhe jatkuu, tee pysyvä korjaus**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> Käynnistä sitten järjestelmäsi **uudelleen**.
> 
> **Nopea väliaikainen korjaus** (nollautuu uudelleenkäynnistyksen jälkeen):
> ```bash
> sudo chmod 666 /var/run/docker.sock
> ```

<!-- @os:linux -->
<!-- @test:id=openclaw-onboard-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

mkdir -p "$HOME/.openclaw"
rm -f "$HOME/.openclaw/openclaw.json"

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://127.0.0.1:13305/api/v1" \
  --custom-model-id "${openclaw_model}" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk

config="$HOME/.openclaw/openclaw.json"
test -f "$config"

grep -q "lemonade" "$config"
grep -q "${openclaw_model}" "$config"
grep -q "127.0.0.1:13305" "$config"

echo "OK: OpenClaw onboarding wrote Lemonade configuration"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=openclaw-sandbox-config-linux timeout=120 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
config="$HOME/.openclaw/openclaw.json"

if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

cat > sandbox.patch.json5 <<JSON5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none"
      }
    }
  }
}
JSON5

openclaw config patch --file ./sandbox.patch.json5

grep -q '"sandbox"' "$config"
grep -Eq '"mode"[[:space:]]*:[[:space:]]*"non-main"' "$config"
grep -Eq '"scope"[[:space:]]*:[[:space:]]*"session"' "$config"
grep -Eq '"workspaceAccess"[[:space:]]*:[[:space:]]*"none"' "$config"

echo "OK: OpenClaw sandbox configuration was written"
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=openclaw-onboard-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

mkdir -p "$HOME/.openclaw"
rm -f "$HOME/.openclaw/openclaw.json"

WINDOWS_HOST="$(ip route show default | awk '{print $3}' | head -1)"

if [ -z "$WINDOWS_HOST" ]; then
  echo "Could not determine WSL gateway IP"
  exit 1
fi

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://$WINDOWS_HOST:13305/api/v1" \
  --custom-model-id "${openclaw_model}" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk

config="$HOME/.openclaw/openclaw.json"
test -f "$config"

grep -q "lemonade" "$config"
grep -q "${openclaw_model}" "$config"
grep -q "$WINDOWS_HOST:13305" "$config"

echo "OK: OpenClaw onboarding wrote Lemonade configuration inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-onboard-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "OpenClaw onboarding failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=openclaw-sandbox-config-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="/mnt/wsl/docker-desktop/cli-tools/usr/bin:$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

docker_config="$(mktemp -d)"
cleanup() {
  rm -rf "$docker_config"
}
trap cleanup EXIT
export DOCKER_CONFIG="$docker_config"
printf '{ "auths": {} }\n' > "$DOCKER_CONFIG/config.json"

config="$HOME/.openclaw/openclaw.json"

if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

cat > sandbox.patch.json5 <<JSON5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none"
      }
    }
  }
}
JSON5

openclaw config patch --file ./sandbox.patch.json5

grep -q '"sandbox"' "$config"
grep -Eq '"mode"[[:space:]]*:[[:space:]]*"non-main"' "$config"
grep -Eq '"scope"[[:space:]]*:[[:space:]]*"session"' "$config"
grep -Eq '"workspaceAccess"[[:space:]]*:[[:space:]]*"none"' "$config"

echo "OK: OpenClaw sandbox configuration was written inside WSL"
'@

$script = $script -replace "`r`n", "`n"
$tmp = Join-Path $env:TEMP "openclaw-sandbox-config-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "OpenClaw sandbox config patch failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->

### Käynnistä OpenClaw-yhdyskäytävä

Yhdyskäytävä on OpenClaw-prosessi, joka hallinnoi agenttisilmukkaa ja tarjoilee kojelautaa:

```bash
openclaw gateway run --bind loopback --port 18789
```

<!-- @os:linux -->
<!-- @test:id=openclaw-gateway-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.openclaw/openclaw.json"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi
log="/tmp/openclaw-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

openclaw gateway run --bind loopback --port 18789 >"$log" 2>&1 &
gateway_pid=$!

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:18789/ || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "OpenClaw gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi

echo "OK: OpenClaw gateway is reachable"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openclaw-gateway-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.openclaw/openclaw.json"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi
log="/tmp/openclaw-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

openclaw gateway run --bind loopback --port 18789 >"$log" 2>&1 &
gateway_pid=$!

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:18789/ || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "OpenClaw gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi

echo "OK: OpenClaw gateway is reachable inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-gateway-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "OpenClaw gateway test failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->

Avataksesi kojelaudan, suorita tämä toisessa päätteessä yhdyskäytävän ollessa yhä käynnissä:

```bash
openclaw dashboard
```

Koska yhdyskäytävä sitoutuu takaisinkytkentäosoitteeseen, kojelauta todentaa automaattisesti, kun se avataan samalta koneelta, eikä tunnuksen syöttöä tai laitteen hyväksyntää tarvita paikallista käyttöä varten. Sinun pitäisi nähdä OpenClaw-kojelauta, jossa Lemonade-mallisi näkyy aktiivisena taustajärjestelmänä.

> Jos olet ottanut hiekkalaatikoinnin käyttöön, voit vahvistaa sen pyytämällä agenttia suorittamaan `run hostname` kojelaudalta. Jos näet lyhyen säiliötunnuksen koneesi isäntänimen sijaan, hiekkalaatikko toimii.

**Onnittelut, olet rakentanut täysin paikallisen tekoälyagenttipinon alusta alkaen.**

> **Tarvitsetko yhdyskäytävän tunnuksen?** Suorita `openclaw dashboard --no-open` tulostaaksesi kojelaudan osoitteen, jossa tunnus on mukana (se myös yrittää kopioida sen leikepöydälle). Vaihtoehtoisesti tunnus löytyy kohdasta `gateway.auth.token` tiedostossa `~/.openclaw/openclaw.json`.
>
> **Etälaitteen hyväksyminen:** Kun avaat kojelaudan toiselta koneelta tai puhelimelta, selain näyttää pyyntötunnuksen. Suorita yhdyskäytävää ajavalla koneella:
> ```bash
> openclaw devices approve <requestId>
> ```
> Tätä tarvitaan vain etä- tai toissijaisille laitteille, saman koneen takaisinkytkentäkäyttö todentaa automaattisesti.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Valinnainen: Yhdistä viestintäkanava

Kun yhdyskäytävä on käynnissä, voit tavoittaa paikallisen agenttisi mistä tahansa laitteesta. Valitse asetuksiisi sopiva vaihtoehto. OpenClaw tukee [Discordia](https://docs.openclaw.ai/channels/discord), [Telegramia](https://docs.openclaw.ai/channels/telegram) ja muita kanavia, katso täydellinen luettelo osoitteesta [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Vaihtoehto A: Discord

Discord vaatii palvelimen, jossa **sinulla on ylläpitäjän oikeudet** bottia lisätäksesi. Jos jaat palvelimia, mutta et omista yhtään, käytä sen sijaan vaihtoehtoa B (Telegram).
#### Luo Discord-tili ja -palvelin

Jos sinulla ei ole Discord-tiliä, rekisteröidy osoitteessa [discord.com](https://discord.com). Tarvitset myös palvelimen, jossa olet järjestelmänvalvoja. Luo sellainen napsauttamalla **+**-kuvaketta Discordin sivupalkissa ja valitsemalla **Create My Own**. Yksityinen palvelin käy hyvin.

#### Luo Discord-sovellus ja botti

1. Siirry [Discord Developer Portal](https://discord.com/developers/applications) -sivulle ja napsauta **New Application**. Anna sille nimi (esim. "openclaw-bot").
2. Napsauta sivupalkista **Bot**. Aseta botille käyttäjänimi.
3. Vieritä edelleen Bot-sivulla kohtaan **Privileged Gateway Intents** ja ota käyttöön:
   - **Message Content Intent** (pakollinen)
   - **Server Members Intent** (suositeltu)
4. Vieritä takaisin ylös ja napsauta **Reset Token** luodaksesi botin tunnuksen (token). Kopioi se.

#### Lisää botti palvelimeesi

1. Napsauta sivupalkista **OAuth2/ URL Generator**.
2. Ota kohdassa **Scopes** käyttöön `bot` ja `applications.commands`.
3. Ota kohdassa **Bot Permissions** käyttöön: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Kopioi luotu URL-osoite, liitä se selaimeesi, valitse palvelimesi ja vahvista. Botin pitäisi nyt näkyä palvelimesi jäsenluettelossa.

#### Kerää tunnisteesi

Ota Discordissa käyttöön Developer Mode (**User Settings/ Advanced/ Developer Mode**) ja tee sitten seuraavat:
- Napsauta palvelimesi kuvaketta hiiren kakkospainikkeella: **Copy Server ID**
- Napsauta omaa avatariasi hiiren kakkospainikkeella: **Copy User ID**

#### Salli yksityisviestit palvelimen jäseniltä

Napsauta palvelimesi kuvaketta hiiren kakkospainikkeella / **Privacy Settings** / kytke päälle **Direct Messages**. Tämä sallii botin lähettää sinulle yksityisviestin, mikä on vaadittu pariliitosvaihetta varten.

#### Määritä OpenClaw Discordia varten

Tallenna botin tunnus (token) ympäristömuuttujaan ja luo sitten yksi patch-tiedosto, joka ottaa Discordin käyttöön, viittaa tunnukseen ja sallii palvelimesi (allowlist). Korvaa `<server_id>` ja `<user_id>` yllä kerätyillä tunnisteilla.

```bash
export DISCORD_BOT_TOKEN="YOUR_BOT_TOKEN"

cat > discord.patch.json5 <<JSON5
{
  channels: {
    discord: {
      enabled: true,
      token: { source: "env", provider: "default", id: "DISCORD_BOT_TOKEN" },
      dmPolicy: "pairing",
      groupPolicy: "allowlist",
      guilds: {
        "<server_id>": {
          requireMention: false,
          users: ["<user_id>"],
        },
      },
    },
  },
}
JSON5
openclaw config patch --file ./discord.patch.json5
```

> **Älä luota siihen, että pyydät agenttia määrittämään tämän.** Kun hiekkalaatikointi (sandboxing) on käytössä, agentti ei voi kirjoittaa tiedostoon `~/.openclaw/openclaw.json` hiekkalaatikon sisältä, käytä sen sijaan yllä olevia CLI-komentoja isäntäkoneella.

Käynnistä yhdyskäytävä (gateway) uudelleen, jotta se ottaa käyttöön uuden kanava-asetuksen:

```bash
openclaw gateway run --bind loopback --port 18789
```

Sinun pitäisi nähdä `logged in to discord as <bot-name>` yhdyskäytävän tulosteessa muutaman sekunnin sisällä.

#### Yhdistä Discord-tilisi

Lähetä botille yksityisviesti Discordissa. Se vastaa lyhyellä pariliitoskoodilla.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Hyväksy se koneella, jolla OpenClaw on käynnissä:
```bash
openclaw pairing approve discord <CODE>
```

> Pariliitoskoodit vanhenevat tunnin kuluttua.

Voit nyt keskustella agenttisi kanssa suoraan Discordista ja siirtää tehtäviä paikalliselle laitteistollesi.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Vaihtoehto B: Telegram

Telegram on useimmille käyttäjille yksinkertaisempi kuin Discord, se ei vaadi palvelinta eikä ylläpitäjän oikeuksia.

#### Luo Telegram-botti

1. Avaa Telegram ja lähetä viesti käyttäjälle **@BotFather**.
2. Lähetä `/newbot` ja seuraa ohjeita. Tallenna botin tunnus (token), jonka saat.

#### Määritä OpenClaw Telegramia varten

Tallenna tunnus ympäristömuuttujaan:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Lisää kanavan määritykset tiedostoon `~/.openclaw/openclaw.json` (tai patchaa se hallintapaneelin kautta):

```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "botToken": "YOUR_BOT_TOKEN",
      "dmPolicy": "pairing"
    }
  }
}
```

Käynnistä yhdyskäytävä uudelleen ja lähetä sitten botillesi mikä tahansa viesti Telegramissa. Hyväksy pariliitos:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Pariliitoskoodit vanhenevat tunnin kuluttua. Voit nyt keskustella agenttisi kanssa Telegramin yksityisviestien kautta.

---

## Seuraavat vaiheet

Nyt kun agenttisi voi vastaanottaa komentoja puhelimestasi ja toimia paikallisella koneellasi, tässä on kolme tutkimisen arvoista suuntaa:

1. **Osakemarkkinoiden yhteenveto**: Ajasta OpenClaw hakemaan tietoa rahoitusalan rajapinnoista (API) kiinteällä aikavälillä, tekemään yhteenvedon päivän liikkeistä paikallisella mallillasi ja lähettämään koosteen puhelimeesi joka aamu valitsemasi kanavan kautta.

2. **Hienosäätötyön valvonta**: Käynnistä koulutustyö etänä Telegramin tai Discordin kautta ja anna agentin seurata koulutuslokia sekä raportoida säännöllisesti häviöarvot (loss), GPU:n käyttöasteen ja levytilan käytön puhelimeesi. Jos ajo pysähtyy tai VRAM:n käyttö piikkaa, saat siitä tiedon välittömästi ilman, että sinun tarvitsee olla koneen ääressä.

3. **IoT paikallisella VLM:llä**: Suuntaa kamera etuovellesi, aja näkömalli Lemonadella ja anna OpenClaw'n analysoida kuvia pyynnöstä tai laukaisimen perusteella. Kysy puhelimestasi "saapuiko tänään paketteja?" ja saat suoran vastauksen omalta laitteistoltasi.