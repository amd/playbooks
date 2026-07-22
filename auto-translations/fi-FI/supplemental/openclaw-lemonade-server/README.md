<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **Konekäännös.** Tämä sivu on käännetty automaattisesti englannista, eikä sitä ole tarkistanut ihminen. Se saattaa sisältää virheitä, ja jotkin vaiheet, komennot, lataukset tai tuotteiden saatavuus voivat vaihdella kielesi tai alueesi mukaan. Jos jokin vaikuttaa virheelliseltä, pidä alkuperäistä englanninkielistä playbookia ensisijaisena lähteenä.
<!-- auto-translated-disclaimer:end -->

# Suorita OpenClaw Lemonade Server -taustajärjestelmällä

## Yleiskatsaus

[**OpenClaw**](https://openclaw.ai/) on itsenäinen tekoälyagentti, joka pystyy kirjoittamaan ja suorittamaan koodia, hallitsemaan tiedostoja ja työskentelemään monivaiheisten monimutkaisten tehtävien parissa puolestasi. Toisin kuin chat-avustaja, joka vain vastaa kysymyksiin, OpenClaw toteuttaa todellisia toimenpiteitä järjestelmässäsi, mikä tarkoittaa, että se tarvitsee nopean ja tehokkaan tekoälytaustajärjestelmän, joka pysyy vaativan agenttisilmukan tahdissa.

[**Lemonade Server**](https://lemonade-server.ai/) on juuri tällainen taustajärjestelmä. Se on avoimen lähdekoodin paikallinen päättelypalvelin, joka ajaa generatiivisen tekoälyn malleja suoraan laitteistollasi ja tarjoaa ne käyttöön alan standardin mukaisen OpenAI API:n kautta.

Yhdessä ne muodostavat täysin paikallisen tekoälyagenttipinon: Lemonade hoitaa mallin päättelyn, ja OpenClaw tarjoaa agenttisilmukan, joka muuntaa mallin tulosteet todellisiksi toimenpiteiksi.

> **Ennen kuin jatkat:** OpenClaw on erittäin itsenäinen tekoälyagentti. Minkä tahansa tekoälyagentin päästäminen käsiksi järjestelmääsi voi johtaa arvaamattomiin tai tahattomiin lopputuloksiin. Jatka vain, jos ymmärrät riskit ja hyväksyt sen, että itsenäinen ohjelmisto toimii puolestasi.

---

## Mitä opit

Tämän oppaan lopussa osaat:

- Tutustua **Lemonade Serveriin**
- **Asentaa OpenClawn** ja **määrittää sen käyttämään Lemonade Serveriä** tekoälytaustajärjestelmänään.
- **Käynnistää OpenClaw-yhdyskäytävän** ja varmistaa, että agenttisi on valmis työskentelyyn.
- **Yhdistää viestintäkanavan** (Discord tai Telegram), jotta voit keskustella agenttisi kanssa mistä tahansa laitteesta.

---

## Muistiasetuksen määrittäminen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Tarkista ohjelmistopäivitykset

<!-- @require:software-update -->
<!-- @device:end -->

## Ohjelmiston esivaatimusten asentaminen

<!-- @os:linux -->
- Tietokone, jossa on **Ubuntu 24.04+** tai yhteensopiva Debian-pohjainen Linux-jakelu ja `apt-get`
- Vähintään **12 Gt RAM-muistia** (64 Gt+ suositellaan suuremmille malleille)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (valinnainen, OpenClawn hiekkalaatikointiin)

- **~10–30 Gt vapaata levytilaa** malliparametreille
<!-- @os:end -->
<!-- @os:windows -->
- Tietokone, jossa on **Windows 10/11**
- Vähintään **12 Gt RAM-muistia** (64 Gt+ suositellaan suuremmille malleille)
- **~10–30 Gt vapaata levytilaa** malliparametreille
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (valinnainen, OpenClawn hiekkalaatikointiin)
<!-- @os:end -->

<!-- @require:lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Hae ja lataa suositeltu malli

Tämän oppaan suositeltu malli on **Qwen3.6-35B-A3B-GGUF** Unslothilta, tehokas MoE-malli, jossa on 263 000 tokenin kontekstiikkuna ja joka soveltuu hyvin agenttityökuormille. Tämä malli käyttää UD-Q4_K_XL-kvantisointia. Hae se nyt:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Lataa se sitten suurella kontekstiikkunalla ja tallenna asetus tulevia ajokertoja varten:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

Mallin oletuskontekstipituus on 262 144 tokenia. Jos kohtaat muistin loppumiseen liittyviä (OOM) virheitä, harkitse kontekstiikkunan pienentämistä. Koska Qwen3.6 kuitenkin hyödyntää laajennettua kontekstia monimutkaisissa tehtävissä, suosittelemme säilyttämään vähintään 128 000 tokenin kontekstipituuden ajattelukyvyn säilyttämiseksi.

> **Vinkki: Poista ajattelu käytöstä nopeampien agenttivastausten saamiseksi:** Qwen3.6-35B-A3B toimii oletuksena ajattelutilassa, mikä lisää viivettä ennen jokaista vastausta. Agenttisilmukoissa tämä viive kertyy nopeasti. [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) -tietovarasto tarjoaa valmiin asetustiedoston, joka poistaa ajattelun käytöstä. Käyttääksesi sitä, lataa tiedosto ja tuo se:
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

## WSL:n määrittäminen

Ajamme OpenClawn WSL:n sisällä (suositellaan) ja yhdistämme sen Lemonadeen, joka toimii natiivisti Windowsissa. Näin saat Linux-komentotulkkiympäristön OpenClawlle säilyttäen samalla Lemonaden GPU-kiihdytyksen Windows-puolella.

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

### Sillan luominen Lemonadesta Windowsista WSL:ään

WSL2 toimii virtuaaliverkossa. Lemonade Windowsissa sitoutuu osoitteeseen `127.0.0.1`, johon WSL ei pääse suoraan käsiksi. Windowsin porttivälityspalvelin välittää liikennettä WSL-yhdyskäytävän IP-osoitteesta Windowsin localhostiin.

**Etsi WSL-yhdyskäytävän IP-osoite** (suorita WSL:n sisällä):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Lisää porttivälitys** (suorita PowerShellissä järjestelmänvalvojana, korvaa `<WSL-Gateway-IP>` WSL-yhdyskäytäväsi IP-osoitteella):

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

Jos olet jo ladannut Qwen3.6-35B-A3B-GGUF-mallin edellisessä vaiheessa, sinun pitäisi nähdä tällaista JSON-tulostetta:

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

> `netsh portproxy` -sääntö säilyy uudelleenkäynnistysten yli, mutta WSL-yhdyskäytävän IP-osoite voi muuttua `wsl --shutdown` -komennon jälkeen. Jos Lemonade ei ole enää tavoitettavissa WSL:stä uudelleenkäynnistyksen jälkeen, hae päivitetty yhdyskäytävän IP-osoite ja päivitä välityspalvelin tällä uudella osoitteella.

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

## OpenClawn asentaminen ja määrittäminen

### Asenna OpenClaw
<!-- @os:windows -->
> Suorita tämän osion komennot **WSL-päätteessäsi**.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

`--no-onboard`-lippu ohittaa vuorovaikutteisen asennusvelhon, sillä määrität mallitaustajärjestelmän manuaalisesti seuraavassa vaiheessa, mikä antaa sinulle tarkan hallinnan siitä, mitä mallia ja palvelinta käytetään.

Avaa uusi pääte ja varmista asennus:

```bash
openclaw --version
```

> **Vinkki:** Jos näet `command not found` -viestin asennuksen jälkeen, lisää npm:n globaali bin-hakemisto PATH-muuttujaan:
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
### Määritä OpenClaw käyttämään Lemonadea

Suorita OpenClaw'n ei-interaktiivinen käyttöönotto.
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

Tämä komento kirjoittaa OpenClaw'n määrityksen tiedostoon `~/.openclaw/openclaw.json`.

> **OpenClaw'n kontekstikoon mitoitus:** OpenClaw'n tiivistys (compaction) käynnistyy, kun `contextTokens > contextWindow − reserveTokens`. Oletusarvoinen `reserveTokensFloor` on 20 000 tokenia, ja tämä alaraja ohittaa arvon `reserveTokens`, jos se on pienempi, joten mikä tahansa mallin konteksti alle ~37k käynnistää loputtoman tiivistyssilmukan. Aseta pieni reservi ja poista alaraja käytöstä kerran määrityksessäsi, niin se koskee jokaista mallia eikä mallikohtaista säätöä tarvita:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` on *alaraja* (minimivarmistus), ei itse reservi, joten pelkän alarajan asettamisella ei ole vaikutusta. `reserveTokensFloor: 0` poistaa tämän varmistuksen käytöstä, jolloin pienempi `reserveTokens`-arvo hyväksytään.
>
> **Milloin tätä sovelletaan:** Käytä tätä määritystä, jos mallisi tehokas kontekstikoko on alle ~37k, joko siksi että malli on pieni (esim. 8k, 16k, 32k) tai koska olet tarkoituksella rajoittanut sen pienemmäksi (esim. ladannut 128k-mallin mutta asettanut kontekstiksi 16k Lemonadessa). Ilman tätä OpenClaw joutuu käynnistyksessä loputtomaan tiivistyssilmukkaan.
>
> **Suuren kontekstin mallit täydellä kontekstilla:** Voit ohittaa tämän kokonaan. Oletusarvot toimivat hyvin, tiivistys käynnistyy hyvissä ajoin ennen kuin ikkuna täyttyy, ja mallilla on runsaasti tilaa tuottaa pitkiä vastauksia. Jos sovellat tätä silti, huomaa, että `reserveTokens: 4096` rajoittaa vastauksen pituuden noin 4k tokeniin, mikä voi katkaista pitkän tiedostojen luonnin tai yksityiskohtaiset suunnitelmat.
>
> **Mihin tämä lisätään:** Sijoita `compaction`-lohko kohtaan `agents.defaults` `openclaw.json`-tiedostossasi (yleensä polussa `~/.openclaw/openclaw.json`):
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
> Loput määrityksestäsi (gateway, kanavat, mallit jne.) pysyvät muuttumattomina, vain `compaction`-avain täytyy lisätä.

### (Suositeltu) Ota Docker-hiekkalaatikointi käyttöön

OpenClaw voi ohjata kaikki agentin tiedosto- ja koodioperaatiot eristetyn Docker-säiliön kautta suoraan isäntäkoneella suorittamisen sijaan. Tämä rajoittaa minkä tahansa tahattoman toiminnon vaikutuksen hiekkalaatikkoon, jolloin isäntäkoneesi tiedostojärjestelmä ja verkko pysyvät koskemattomina.

Rakenna hiekkalaatikkokuva kerran (Dockerin täytyy olla asennettuna):

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

Hiekkalaatikkosäiliöillä **ei ole verkkoyhteyttä** oletuksena. Katso [hiekkalaatikoinnin viiteopas](https://docs.openclaw.ai/gateway/sandboxing) liitosasennuksista (bind mounts) ja verkkoasetusten ohituksista.

> #### Vianmääritys: Docker Permission Denied
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
> Sen jälkeen **käynnistä** järjestelmäsi **uudelleen**.
> 
> **Nopea väliaikainen korjaus** (nollautuu uudelleenkäynnistyksessä):
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

<!-- @os:linux -->
## (Suositeltu) OpenClaw-integraatio Firecrawl-palveluiden kanssa

[Firecrawl](https://docs.firecrawl.dev/introduction) tarjoaa itseisännöidyn verkon indeksointi- ja sisällönpoimintapalvelun, joka voi ohittaa nämä haasteet ja avata OpenClaw-automaation koko potentiaalin.

Tässä asennuksessa OpenClaw toimii joukkona Docker-säiliöitä, joita hallinnoidaan Podmanilla. Elinkaaren hallinnan ja automaattisen käynnistyksen yksinkertaistamiseksi rekisteröimme Firecrawlin käyttäjätason `systemd`-palveluksi, joka orkestroi taustalla olevaa Podman Compose -pinoa. Tämän ansiosta OpenClaw voi käynnistää yhdyskäytävän, pysäyttää sen ja tarkistaa Firecrawl-palvelun tilan tavallisilla `systemctl --user` -komennoilla ilman suoraa vuorovaikutusta säiliöiden kanssa.

Yksinkertaisuuden vuoksi olemme jakaneet koko prosessin neljään vaiheeseen:

---

### 1. Rekisteröi järjestelmäpalvelu
Siirry systemd-käyttäjämääritysten hakemistoon:
```bash
cd ~/.config/systemd/user
```
Luo ja avaa uusi tiedosto nimeltä `firecrawl.service`.
```bash
nano firecrawl.service
```
Kopioi ja liitä seuraava määritys:
```bash
[Unit]
Description=OpenClaw Firecrawl Service
After=podman.service
Requires=podman.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=%h/firecrawl

# Optional: Validate config before starting
ExecStartPre=/usr/bin/podman compose -f openclaw-compose.yaml config --quiet

# Generate token and write to .env file
ExecStartPre=/bin/bash -c 'chmod 644 %h/firecrawl/.env && echo "OPENCLAW_GATEWAY_TOKEN=$(openssl rand -hex 32)" > %h/firecrawl/.env'

# Step 1: Start containers in detached mode
ExecStart=/usr/bin/podman compose -f openclaw-compose.yaml up -d --remove-orphans

# Step 2: Wait for container to be healthy/ready
ExecStartPost=/bin/sleep 5

# Step 3: Run onboarding inside container in detached mode
ExecStartPost=/usr/bin/podman exec -d openclaw_gateway /bin/bash -c "openclaw onboard \
    --non-interactive \
    --accept-risk \
    --mode local \
    --auth-choice skip \
    --gateway-auth token \
    --gateway-token "$OPENCLAW_GATEWAY_TOKEN" "

# Stop containers when the service stops
ExecStop=/usr/bin/podman compose -f openclaw-compose.yaml down

[Install]
WantedBy=default.target
```
Tässä vaiheessa palvelu on määritelty, mutta sitä ei ole vielä rekisteröity `systemd`:lle.
Varmista, että tiedostonimi vastaa täsmälleen yllä luomaasi, ja suorita sitten:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
Jos onnistui, näet seuraavan tulosteen:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

`default.target.wants/`-hakemisto sisältää symboliset linkit palveluihin, jotka on määritetty käynnistymään automaattisesti.
### 2. Määritä Firecrawl

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) sopii ihanteellisesti niille, jotka tarvitsevat täyden hallinnan omista scraping- ja tiedonkäsittely-ympäristöistään, mutta se tuo mukanaan lisää ylläpito- ja määritystyötä.

Aloita kloonaamalla repositorio:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
Luo `.env` juurihakemistoon `/firecrawl`: 
```bash
# ===== Required ENVS ======
PORT=3002
HOST=0.0.0.0

# ===== Firecrawl =====
# FIRECRAWL_API_KEY="" # optional
```
### 3. Ota OpenClaw käyttöön Podman Composella

Ennen kuin jatkat, varmista, että olet hakenut uusimman OpenClaw Docker -otoksen:
```bash
podman pull ghcr.io/openclaw/openclaw:latest
```
Kun tämä on tehty, lataa OpenClaw Compose -tiedosto [openclaw-compose.yaml](assets/openclaw-compose.yaml) ja sijoita se juurihakemistoon `/firecrawl`:

> Tämä käytäntö on välttämätön, jotta `systemd` löytää palvelun ja pystyy käynnistämään sen oikein kohdassa `WorkingDirectory=${HOME}/firecrawl` määritellyn mukaisesti.

> Voit aina laajentaa pinoa lisäämällä tarvittaessa uusia Firecrawl-palveluita. Täydellinen luettelo saatavilla olevista palveluista löytyy virallisesta [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml) -tiedostosta.

### 4. Käynnistä OpenClaw-palvelu Firecrawlin kautta 

Ennen kuin annat hallinnan `systemd`:lle, varmista, että kaikki toimii oikein käynnistämällä pino manuaalisesti:
```bash
podman compose -f openclaw-compose.yaml up -d
```
Jos kaikki on määritetty oikein, näet OpenClaw-kontin käynnistyvän, ja komentorivin tulosteen tulisi näyttää suunnilleen tältä:
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

Kun olet vahvistanut tämän, sammuta pino ennen jatkamista:
```bash
podman compose -f openclaw-compose.yaml down
```
Ennen palvelun käynnistämistä sinun on varmistettava, että `firecrawl`-hakemistolla ja sen `.env`-tiedostolla on oikeat omistajuudet ja käyttöoikeudet. 
Tämä on välttämätöntä, jotta palvelu voi kirjoittaa tunnistetietosi käynnistyksen yhteydessä.
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
Nyt kun kaikki on vahvistettu, käynnistä palvelu `systemd`:n kautta:
```bash
systemctl --user start firecrawl.service
```
[OpenClaw-toiminnot](https://docs.openclaw.ai/) ovat käytettävissä interaktiivisen kontin sisällä, ja verkkokojelauta on saatavilla samalla isäntäkoneella ja portissa osoitteessa http://127.0.0.1:18789.
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### `OPENCLAW_GATEWAY_TOKEN`-arvon hankkiminen

Kun palvelu on käynnissä, huomaat, että kotihakemistoosi (~/.openclaw) on luotu uusi `.openclaw`-hakemisto. Tämä hakemisto on oletuksena lukittu, joten sinun on avattava se lukituksesta noutaaksesi yhdyskäytävätunnuksesi (gateway token).

1. Myönnä pääsy hakemistoon:
```bash
sudo chmod 777 ~/.openclaw/
```
2. Lue yhdyskäytävätunnuksesi:
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
Etsi tulosteesta `OPENCLAW_GATEWAY_TOKEN`-arvo.

3. Avaa yhdyskäytävän kojelauta selaimessasi osoitteessa http://127.0.0.1:18789. Liitä tunnuksesi, kun sinua pyydetään todentamaan.

Pysäytä palvelu suorittamalla:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---

## Käynnistä OpenClaw-yhdyskäytävä

Yhdyskäytävä on OpenClaw-prosessi, joka hallinnoi agenttisilmukkaa ja tarjoilee kojelaudan:

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

Avataksesi kojelaudan, suorita tämä toisessa päätteessä, kun yhdyskäytävä on yhä käynnissä:

```bash
openclaw dashboard
```

Koska yhdyskäytävä sitoutuu takaisinkytkentäosoitteeseen (loopback), kojelauta todentaa käyttäjän automaattisesti, kun se avataan samalta koneelta - paikallista käyttöä varten ei tarvita tunnuksen syöttämistä tai laitteen hyväksyntää. Sinun pitäisi nähdä OpenClaw-kojelauta, jossa Lemonade-mallisi näkyy aktiivisena taustajärjestelmänä.

> Jos olet ottanut hiekkalaatikoinnin (sandboxing) käyttöön, voit varmistaa sen pyytämällä agenttia suorittamaan `run hostname` kojelaudalta. Jos näet koneesi isäntänimen sijaan lyhyen kontin tunnisteen, hiekkalaatikko toimii.

**Onnittelut, olet rakentanut täysin paikallisen tekoälyagenttipinon alusta alkaen.**

> **Tarvitsetko yhdyskäytävätunnuksen?** Suorita `openclaw dashboard --no-open`, jolloin tulostetaan kojelaudan URL-osoite tunnus mukaan sisällytettynä (se myös yrittää kopioida sen leikepöydällesi). Vaihtoehtoisesti tunnus löytyy kohdasta `gateway.auth.token` tiedostossa `~/.openclaw/openclaw.json`.
>
> **Etälaitteen hyväksyminen:** Kun avaat kojelaudan toiselta koneelta tai puhelimesta, selain näyttää pyyntötunnuksen (request ID). Suorita yhdyskäytävää suorittavalla koneella:
> ```bash
> openclaw devices approve <requestId>
> ```
> Tämä tarvitaan vain etä- tai toissijaisille laitteille, samalta koneelta tehty takaisinkytkentäkäyttö todentaa itsensä automaattisesti.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Valinnainen: Yhdistä viestintäkanava

Kun yhdyskäytävä on käynnissä, voit tavoittaa paikallisen agenttisi mistä tahansa laitteesta. Valitse asetuksiisi sopiva vaihtoehto. OpenClaw tukee [Discordia](https://docs.openclaw.ai/channels/discord), [Telegramia](https://docs.openclaw.ai/channels/telegram) ja muita kanavia - katso täydellinen luettelo osoitteesta [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Vaihtoehto A: Discord

Discord vaatii palvelimen, jolla sinulla on **ylläpitäjän käyttöoikeudet** botin lisäämiseksi. Jos jaat palvelimia mutta et omista yhtään, käytä sen sijaan vaihtoehtoa B (Telegram).

#### Luo Discord-tili ja -palvelin

Jos sinulla ei ole Discord-tiliä, rekisteröidy osoitteessa [discord.com](https://discord.com). Tarvitset myös palvelimen, jolla olet ylläpitäjä - luo sellainen napsauttamalla **+**-kuvaketta Discordin sivupalkissa ja valitsemalla **Create My Own**. Yksityinen palvelin käy hyvin.

#### Luo Discord-sovellus ja botti

1. Siirry [Discordin kehittäjäportaaliin](https://discord.com/developers/applications) ja napsauta **New Application**. Anna sille nimi (esim. "openclaw-bot").
2. Napsauta sivupalkissa **Bot**. Aseta botille käyttäjänimi.
3. Vieritä yhä Bot-sivulla kohtaan **Privileged Gateway Intents** ja ota käyttöön:
   - **Message Content Intent** (pakollinen)
   - **Server Members Intent** (suositeltu)
4. Vieritä takaisin ylös ja napsauta **Reset Token** luodaksesi bottitunnuksesi. Kopioi se.

#### Lisää botti palvelimellesi

1. Napsauta sivupalkissa **OAuth2/ URL Generator**.
2. Ota kohdassa **Scopes** käyttöön `bot` ja `applications.commands`.
3. Ota kohdassa **Bot Permissions** käyttöön: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Kopioi luotu URL-osoite, liitä se selaimeesi, valitse palvelimesi ja vahvista. Botin pitäisi nyt näkyä palvelimesi jäsenluettelossa.
#### Kerää tunnuksesi

Ota Discordissa käyttöön kehittäjätila (**User Settings/ Advanced/ Developer Mode**) ja tee sitten seuraavat:
- Napsauta hiiren oikealla painikkeella palvelimesi kuvaketta: **Copy Server ID**
- Napsauta hiiren oikealla painikkeella omaa avatariasi: **Copy User ID**

#### Salli yksityisviestit palvelimen jäseniltä

Napsauta hiiren oikealla painikkeella palvelimesi kuvaketta / **Privacy Settings** / kytke päälle **Direct Messages**. Näin botti voi lähettää sinulle yksityisviestin, mikä vaaditaan pariutusvaiheessa.

#### Määritä OpenClaw Discordia varten

Tallenna botin token ympäristömuuttujaksi ja luo sitten yksi patch-tiedosto, joka ottaa Discordin käyttöön, viittaa tokeniin ja lisää palvelimesi sallittujen listalle. Korvaa `<server_id>` ja `<user_id>` yllä kerätyillä tunnuksilla.

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

> **Älä luota siihen, että pyydät agenttia tekemään tämän määrityksen puolestasi.** Kun sandboxing on käytössä, agentti ei voi kirjoittaa tiedostoon `~/.openclaw/openclaw.json` sandboxin sisältä, käytä sen sijaan yllä olevia CLI-komentoja isäntäkoneella.

Käynnistä yhdyskäytävä uudelleen, jotta se ottaa uuden kanavamäärityksen käyttöön:

```bash
openclaw gateway run --bind loopback --port 18789
```

Sinun pitäisi nähdä `logged in to discord as <bot-name>` yhdyskäytävän tulosteessa muutaman sekunnin kuluessa.

#### Pariuta Discord-tilisi

Lähetä botille yksityisviesti Discordissa. Se vastaa lyhyellä pariutuskoodilla.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Hyväksy se koneella, jolla OpenClaw on käynnissä:
```bash
openclaw pairing approve discord <CODE>
```

> Pariutuskoodit vanhenevat tunnin kuluttua.

Voit nyt keskustella agenttisi kanssa suoraan Discordista ja siirtää tehtäviä paikalliselle laitteistollesi.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Vaihtoehto B: Telegram

Telegram on useimmille käyttäjille yksinkertaisempi kuin Discord, sillä se ei vaadi palvelinta eikä ylläpitäjän oikeuksia.

#### Luo Telegram-botti

1. Avaa Telegram ja lähetä viesti käyttäjälle **@BotFather**.
2. Lähetä `/newbot` ja seuraa ohjeita. Tallenna botin antama token.

#### Määritä OpenClaw Telegramia varten

Tallenna token ympäristömuuttujaksi:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Lisää kanavamääritys tiedostoon `~/.openclaw/openclaw.json` (tai tee patch dashboardin kautta):

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

Käynnistä yhdyskäytävä uudelleen ja lähetä botillesi mikä tahansa viesti Telegramissa. Hyväksy pariutus:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Pariutuskoodit vanhenevat tunnin kuluttua. Voit nyt keskustella agenttisi kanssa Telegram-yksityisviesteillä.

---

## Seuraavat askeleet

Nyt kun agenttisi voi vastaanottaa komentoja puhelimestasi ja toimia paikallisella koneellasi, tässä on kolme suuntaa, joita kannattaa tutkia:

1. **Osakemarkkinoiden yhteenveto**: Ajasta OpenClaw hakemaan tietoa rahoitusalan rajapinnoista säännöllisin väliajoin, tekemään yhteenvedon päivän liikkeistä paikallisella mallillasi ja lähettämään koosteen puhelimeesi joka aamu valitsemasi kanavan kautta.

2. **Hienosäädön valvonta**: Käynnistä koulutustehtävä etänä Telegramin tai Discordin kautta ja anna agentin seurata koulutuslokia sekä raportoida ajoittain häviöarvot (loss), GPU:n käyttöasteen ja levytilan käytön takaisin puhelimeesi. Jos ajo jumiutuu tai VRAM-käyttö piikkaa, saat siitä tiedon välittömästi ilman, että sinun tarvitsee olla koneen ääressä.

3. **IoT paikallisella VLM:llä**: Suuntaa kamera etuovellesi, aja näkömalli Lemonadella ja anna OpenClawin analysoida kuvia pyynnöstä tai laukaisimesta. Kysy puhelimestasi "saapuiko tänään paketteja?" ja saat suoran vastauksen omalta laitteistoltasi.

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